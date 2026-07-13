"use client";

import { FormEvent, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Badge,
  Button,
  Card,
  Field,
  FieldLabel,
  Kicker,
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

function QuestionCard({
  question,
  identityId,
  onStatus,
}: {
  question: CommunityQuestion;
  identityId: string;
  onStatus: (status: StatusState) => void;
}) {
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
        message: `Answer received with status ${created.status}; moderation is required before publication.`,
      });
    } catch (error: unknown) {
      onStatus({
        kind: "error",
        message: errorMessage(error, "Answer could not be submitted."),
      });
    }
  }

  return (
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <div className="flex items-center justify-between gap-2">
        <h5 className="font-display text-base font-semibold">{question.title}</h5>
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
              {answer.source_backed && <Badge variant="trust">source-backed</Badge>}
              {answer.consensus?.controversial && (
                <Badge variant="warning">controversial</Badge>
              )}
              {answer.consensus && (
                <Badge variant="default">
                  consensus {Math.round(answer.consensus.score)}
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
                      message: `Vote recorded. Consensus score: ${Math.round(summary.score)}.`,
                    });
                  } catch (error: unknown) {
                    onStatus({
                      kind: "error",
                      message: errorMessage(error, "Vote could not be submitted."),
                    });
                  }
                }}
              >
                Up
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
                      message: `Vote recorded. Consensus score: ${Math.round(summary.score)}.`,
                    });
                  } catch (error: unknown) {
                    onStatus({
                      kind: "error",
                      message: errorMessage(error, "Vote could not be submitted."),
                    });
                  }
                }}
              >
                Helpful
              </Button>
            </div>
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-2">
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Add an answer for moderation"
          aria-label="Community answer"
          className={TEXTAREA_CLASS}
        />
        <Button
          type="button"
          variant="ghost"
          onClick={submitAnswer}
          disabled={!draft.trim()}
        >
          Submit answer
        </Button>
      </div>
    </Card>
  );
}

export function CommunityCountryBlock({
  countrySlug,
}: CommunityCountryBlockProps) {
  const identityId = useMemo(() => anonymousIdentity("community"), []);

  const { data: questionsData, isPending } = useQuery(
    communityQuestionsQuery(countrySlug),
  );
  const questions = questionsData?.items ?? [];

  const [status, setStatus] = useState<StatusState>({ kind: "idle", message: "" });
  const [questionTitle, setQuestionTitle] = useState("");
  const [questionBody, setQuestionBody] = useState("");
  const [reportType, setReportType] = useState<ReportType>("outdated");
  const [reportMessage, setReportMessage] = useState("");
  const [ratingComment, setRatingComment] = useState("");
  const [realityGapScore, setRealityGapScore] = useState(50);

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
        message: `Question received with status ${created.status}; it will appear after moderation.`,
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, "Question could not be submitted."),
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
        message: `Report received with status ${created.status}; editors will review it.`,
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, "Report could not be submitted."),
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
        official_expectation_score: realityGapScore,
        real_experience_score: realityGapScore,
        bureaucracy_score: realityGapScore,
        cost_surprise_score: realityGapScore,
        banking_difficulty_score: realityGapScore,
        safety_feeling_score: realityGapScore,
        comment: ratingComment || null,
        created_by_identity_type: "anonymous_session",
        created_by_identity_id: identityId,
      });
      setRatingComment("");
      setStatus({
        kind: "success",
        message: `Reality-gap input received with status ${created.status}.`,
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, "Rating could not be submitted."),
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
          <h3 className="font-display text-xl font-semibold">
            Community intelligence
          </h3>
          <p className="text-c3 text-sm leading-relaxed">
            Human experience is separated from trusted source-backed content
            and appears publicly only after moderation.
          </p>
        </div>
        <Badge
          variant="default"
          title="review gate"
        >
          review gate
        </Badge>
      </div>

      {status.kind !== "idle" && (
        <p
          className={status.kind === "error" ? "text-terra3 text-sm" : "text-sage3 text-sm"}
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
            <Kicker>Q&A</Kicker>
            {questions.length === 0 ? (
              <div data-testid="community-empty">
                <EmptyState message="No published community questions yet." />
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
                <FieldLabel>Question title</FieldLabel>
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
                <FieldLabel>Question details</FieldLabel>
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
                Submit for review
              </Button>
            </form>
          </section>

          <section
            className="flex flex-col gap-4"
            data-testid="community-report-panel"
          >
            <Kicker accent="terra">Report data issue</Kicker>
            <form
              className="flex flex-col gap-3"
              onSubmit={submitReport}
            >
              <Field>
                <FieldLabel>Issue type</FieldLabel>
                <select
                  value={reportType}
                  onChange={(event) =>
                    setReportType(event.target.value as ReportType)
                  }
                  data-testid="community-report-type"
                  className={INPUT_CLASS}
                >
                  <option value="outdated">Outdated</option>
                  <option value="wrong">Wrong</option>
                  <option value="missing_source">Missing source</option>
                  <option value="contradiction">Contradiction</option>
                  <option value="translation_issue">Translation issue</option>
                  <option value="other">Other</option>
                </select>
              </Field>
              <Field>
                <FieldLabel>Message</FieldLabel>
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
                Send to review
              </Button>
            </form>
          </section>

          <section
            className="flex flex-col gap-4"
            data-testid="community-rating-panel"
          >
            <Kicker accent="plum">Reality gap preview</Kicker>
            <p className="text-c4 text-xs">
              Limited community input only; no trusted ERG score is
              calculated yet.
            </p>
            <form
              className="flex flex-col gap-3"
              onSubmit={submitRating}
            >
              <Field>
                <FieldLabel>Experience score</FieldLabel>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={realityGapScore}
                  onChange={(event) =>
                    setRealityGapScore(Number(event.target.value))
                  }
                  data-testid="community-rating-score"
                  className="w-full"
                />
                <span className="font-display text-gold3 text-sm font-bold">
                  {realityGapScore}
                </span>
              </Field>
              <Field>
                <FieldLabel>Optional note</FieldLabel>
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
                Submit limited input
              </Button>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
