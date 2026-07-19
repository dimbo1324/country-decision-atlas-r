"use client";

import { FormEvent, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import {
  Badge,
  Button,
  Card,
  Field,
  FieldLabel,
  Kicker,
  RadarChart,
  Skeleton,
} from "@country-decision-atlas/ui";
import {
  communityQuestionsQuery,
  communityAnswersQuery,
  useCreateCommunityQuestionMutation,
  useCreateCommunityAnswerMutation,
  useVoteCommunityAnswerMutation,
  useCreateDataErrorReportMutation,
  useCreateUserStoryRatingMutation,
} from "../../entities/community/api";
import { isApiError, type CommunityQuestion } from "../../shared/api";
import { EmptyState } from "../../shared/ui/EmptyState";

type CommunityCountryBlockProps = {
  countrySlug: string;
};

type StatusState = {
  kind: "idle" | "success" | "error";
  message: string;
};

type ReportType =
  | "outdated"
  | "wrong"
  | "missing_source"
  | "contradiction"
  | "translation_issue"
  | "other";

function anonymousIdentity(prefix: string) {
  if (typeof window === "undefined") {
    return `${prefix}-server`;
  }
  const key = `cda-${prefix}-identity`;
  const existing = window.localStorage.getItem(key);
  if (existing) return existing;
  const created = `${prefix}-${crypto.randomUUID()}`;
  window.localStorage.setItem(key, created);
  return created;
}

function errorMessage(error: unknown, fallback: string) {
  if (isApiError(error)) {
    return error.error?.message ?? fallback;
  }
  return error instanceof Error ? error.message : fallback;
}

const TEXTAREA_CLASS =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";
const INPUT_CLASS =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

const RATING_FIELDS = [
  "official_expectation_score",
  "real_experience_score",
  "bureaucracy_score",
  "cost_surprise_score",
  "banking_difficulty_score",
  "safety_feeling_score",
] as const;

function QuestionCard({
  question,
  identityId,
  onStatus,
}: {
  question: CommunityQuestion;
  identityId: string;
  onStatus: (status: StatusState) => void;
}) {
  const t = useTranslations("communityCountryBlock");
  const [draft, setDraft] = useState("");
  const { data: answers } = useQuery(communityAnswersQuery(question.id));
  const createAnswer = useCreateCommunityAnswerMutation(question.id);
  const voteAnswer = useVoteCommunityAnswerMutation(question.id);

  async function submitAnswer() {
    const body = draft.trim();
    if (!body) return;
    try {
      const created = await createAnswer.mutateAsync({
        body,
        source_ids: [],
        evidence_item_ids: [],
        created_by_identity_type: "anonymous_session",
        created_by_identity_id: identityId,
      });
      setDraft("");
      onStatus({
        kind: "success",
        message: t("answerReceived", { status: created.status }),
      });
    } catch (error: unknown) {
      onStatus({
        kind: "error",
        message: errorMessage(error, t("answerSubmitError")),
      });
    }
  }

  return (
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <div className="flex items-center justify-between gap-2">
        <h5 className="font-display text-base font-semibold">
          {question.title}
        </h5>
        <Badge variant="default">{question.status}</Badge>
      </div>
      <p className="text-c3 text-sm leading-relaxed">{question.body}</p>
      <div className="flex flex-col gap-3">
        {(answers ?? []).map((answer) => (
          <div
            key={answer.id}
            className="border-warm flex flex-col gap-2 border-l-2 pl-3"
          >
            <p className="text-c2 text-sm">{answer.body}</p>
            <div className="flex flex-wrap gap-2">
              {answer.source_backed && (
                <Badge variant="trust">{t("sourceBacked")}</Badge>
              )}
              {answer.consensus?.controversial && (
                <Badge variant="warning">{t("controversial")}</Badge>
              )}
              {answer.consensus && (
                <Badge variant="default">
                  {t("consensus", {
                    score: Math.round(answer.consensus.score),
                  })}
                </Badge>
              )}
            </div>
            <div className="flex gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={async () => {
                  try {
                    const summary = await voteAnswer.mutateAsync({
                      answerId: answer.id,
                      payload: {
                        vote_type: "up",
                        identity_type: "anonymous_session",
                        identity_id: identityId,
                      },
                    });
                    onStatus({
                      kind: "success",
                      message: t("voteRecorded", {
                        score: Math.round(summary.score),
                      }),
                    });
                  } catch (error: unknown) {
                    onStatus({
                      kind: "error",
                      message: errorMessage(error, t("voteSubmitError")),
                    });
                  }
                }}
              >
                {t("up")}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={async () => {
                  try {
                    const summary = await voteAnswer.mutateAsync({
                      answerId: answer.id,
                      payload: {
                        vote_type: "helpful",
                        identity_type: "anonymous_session",
                        identity_id: identityId,
                      },
                    });
                    onStatus({
                      kind: "success",
                      message: t("voteRecorded", {
                        score: Math.round(summary.score),
                      }),
                    });
                  } catch (error: unknown) {
                    onStatus({
                      kind: "error",
                      message: errorMessage(error, t("voteSubmitError")),
                    });
                  }
                }}
              >
                {t("helpful")}
              </Button>
            </div>
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-2">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={t("addAnswerPlaceholder")}
          aria-label={t("communityAnswerAriaLabel")}
          className={TEXTAREA_CLASS}
        />
        <Button
          type="button"
          variant="ghost"
          onClick={submitAnswer}
          disabled={!draft.trim()}
        >
          {t("submitAnswer")}
        </Button>
      </div>
    </Card>
  );
}

export function CommunityCountryBlock({
  countrySlug,
}: CommunityCountryBlockProps) {
  const t = useTranslations("communityCountryBlock");
  const identityId = useMemo(() => anonymousIdentity("community"), []);

  const { data: questionsData, isPending } = useQuery(
    communityQuestionsQuery(countrySlug),
  );
  const questions = questionsData?.items ?? [];

  const [status, setStatus] = useState<StatusState>({
    kind: "idle",
    message: "",
  });
  const [questionTitle, setQuestionTitle] = useState("");
  const [questionBody, setQuestionBody] = useState("");
  const [reportType, setReportType] = useState<ReportType>("outdated");
  const [reportMessage, setReportMessage] = useState("");
  const [ratingComment, setRatingComment] = useState("");
  const [ratingScores, setRatingScores] = useState<
    Record<(typeof RATING_FIELDS)[number], number>
  >({
    official_expectation_score: 50,
    real_experience_score: 50,
    bureaucracy_score: 50,
    cost_surprise_score: 50,
    banking_difficulty_score: 50,
    safety_feeling_score: 50,
  });

  const ratingAxes = RATING_FIELDS.map((field) => ({
    field,
    label: t(`ratingAxis.${field}`),
  }));

  const createQuestion = useCreateCommunityQuestionMutation(countrySlug);
  const createReport = useCreateDataErrorReportMutation();
  const createRating = useCreateUserStoryRatingMutation();

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ kind: "idle", message: "" });
    try {
      const created = await createQuestion.mutateAsync({
        country_slug: countrySlug,
        route_id: null,
        legal_signal_id: null,
        topic: "country_page",
        title: questionTitle,
        body: questionBody,
        created_by_identity_type: "anonymous_session",
        created_by_identity_id: identityId,
      });
      setQuestionTitle("");
      setQuestionBody("");
      setStatus({
        kind: "success",
        message: t("questionReceived", { status: created.status }),
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, t("questionSubmitError")),
      });
    }
  }

  async function submitReport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ kind: "idle", message: "" });
    try {
      const created = await createReport.mutateAsync({
        entity_type: "country",
        entity_id: null,
        country_slug: countrySlug,
        route_id: null,
        report_type: reportType,
        message: reportMessage,
        created_by_identity_type: "anonymous_session",
        created_by_identity_id: identityId,
      });
      setReportMessage("");
      setStatus({
        kind: "success",
        message: t("reportReceived", { status: created.status }),
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, t("reportSubmitError")),
      });
    }
  }

  async function submitRating(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ kind: "idle", message: "" });
    try {
      const created = await createRating.mutateAsync({
        user_story_id: null,
        country_slug: countrySlug,
        route_id: null,
        ...ratingScores,
        comment: ratingComment || null,
        created_by_identity_type: "anonymous_session",
        created_by_identity_id: identityId,
      });
      setRatingComment("");
      setStatus({
        kind: "success",
        message: t("ratingReceived", { status: created.status }),
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, t("ratingSubmitError")),
      });
    }
  }

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="community-country-block"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h3 className="font-display text-xl font-semibold">{t("title")}</h3>
          <p className="text-c3 text-sm leading-relaxed">{t("subtitle")}</p>
        </div>
        <div data-testid="community-review-badge">
          <Badge
            variant="default"
            title={t("reviewGate")}
          >
            {t("reviewGate")}
          </Badge>
        </div>
      </div>

      {status.kind !== "idle" && (
        <p
          className={
            status.kind === "error"
              ? "text-terra3 text-sm"
              : "text-sage3 text-sm"
          }
          role={status.kind === "error" ? "alert" : "status"}
          data-testid="community-status"
        >
          {status.message}
        </p>
      )}

      {isPending ? (
        <Skeleton lines={4} />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <section
            className="flex flex-col gap-4 lg:col-span-2"
            data-testid="community-qna-panel"
          >
            <Kicker>{t("qnaKicker")}</Kicker>
            {questions.length === 0 ? (
              <div data-testid="community-empty">
                <EmptyState message={t("emptyQuestions")} />
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {questions.map((question) => (
                  <QuestionCard
                    key={question.id}
                    question={question}
                    identityId={identityId}
                    onStatus={setStatus}
                  />
                ))}
              </div>
            )}

            <form
              className="flex flex-col gap-3"
              onSubmit={submitQuestion}
            >
              <Field>
                <FieldLabel>{t("questionTitleLabel")}</FieldLabel>
                <input
                  value={questionTitle}
                  onChange={(event) => setQuestionTitle(event.target.value)}
                  required
                  maxLength={300}
                  data-testid="community-question-title"
                  className={INPUT_CLASS}
                />
              </Field>
              <Field>
                <FieldLabel>{t("questionDetailsLabel")}</FieldLabel>
                <textarea
                  value={questionBody}
                  onChange={(event) => setQuestionBody(event.target.value)}
                  required
                  maxLength={4000}
                  data-testid="community-question-body"
                  className={TEXTAREA_CLASS}
                />
              </Field>
              <Button
                type="submit"
                disabled={!questionTitle.trim() || !questionBody.trim()}
                data-testid="community-question-submit"
              >
                {t("submitForReview")}
              </Button>
            </form>
          </section>

          <section
            className="flex flex-col gap-4"
            data-testid="community-report-panel"
          >
            <Kicker accent="terra">{t("reportDataIssueKicker")}</Kicker>
            <form
              className="flex flex-col gap-3"
              onSubmit={submitReport}
            >
              <Field>
                <FieldLabel>{t("issueTypeLabel")}</FieldLabel>
                <select
                  value={reportType}
                  onChange={(event) =>
                    setReportType(event.target.value as ReportType)
                  }
                  data-testid="community-report-type"
                  className={INPUT_CLASS}
                >
                  <option value="outdated">{t("issueType.outdated")}</option>
                  <option value="wrong">{t("issueType.wrong")}</option>
                  <option value="missing_source">
                    {t("issueType.missing_source")}
                  </option>
                  <option value="contradiction">
                    {t("issueType.contradiction")}
                  </option>
                  <option value="translation_issue">
                    {t("issueType.translation_issue")}
                  </option>
                  <option value="other">{t("issueType.other")}</option>
                </select>
              </Field>
              <Field>
                <FieldLabel>{t("messageLabel")}</FieldLabel>
                <textarea
                  value={reportMessage}
                  onChange={(event) => setReportMessage(event.target.value)}
                  required
                  maxLength={2000}
                  data-testid="community-report-message"
                  className={TEXTAREA_CLASS}
                />
              </Field>
              <Button
                type="submit"
                disabled={!reportMessage.trim()}
                data-testid="community-report-submit"
              >
                {t("sendToReview")}
              </Button>
            </form>
          </section>

          <section
            className="flex flex-col gap-4"
            data-testid="community-rating-panel"
          >
            <Kicker accent="plum">{t("realityGapPreviewKicker")}</Kicker>
            <p className="text-c4 text-xs">{t("realityGapNotice")}</p>
            <RadarChart
              axes={ratingAxes.map((axis) => axis.label)}
              series={[
                {
                  label: t("yourInput"),
                  values: ratingAxes.map((axis) => ratingScores[axis.field]),
                  accent: "gold",
                },
              ]}
              active
            />
            <form
              className="flex flex-col gap-3"
              onSubmit={submitRating}
            >
              {ratingAxes.map((axis) => (
                <Field key={axis.field}>
                  <FieldLabel>{axis.label}</FieldLabel>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={ratingScores[axis.field]}
                    onChange={(event) =>
                      setRatingScores((current) => ({
                        ...current,
                        [axis.field]: Number(event.target.value),
                      }))
                    }
                    data-testid={`community-rating-${axis.field}`}
                    className="w-full"
                  />
                  <span className="font-display text-gold3 text-sm font-bold">
                    {ratingScores[axis.field]}
                  </span>
                </Field>
              ))}
              <Field>
                <FieldLabel>{t("optionalNoteLabel")}</FieldLabel>
                <textarea
                  value={ratingComment}
                  onChange={(event) => setRatingComment(event.target.value)}
                  maxLength={2000}
                  data-testid="community-rating-comment"
                  className={TEXTAREA_CLASS}
                />
              </Field>
              <Button
                type="submit"
                data-testid="community-rating-submit"
              >
                {t("submitLimitedInput")}
              </Button>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
