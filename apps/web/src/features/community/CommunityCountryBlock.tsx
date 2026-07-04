"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  communityApi,
  isApiError,
  type CommunityAnswer,
  type CommunityQuestion,
} from "../../shared/api";

type CommunityCountryBlockProps = {
  countrySlug: string;
};

type AnswersByQuestion = Record<string, CommunityAnswer[]>;
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

export function CommunityCountryBlock({
  countrySlug,
}: CommunityCountryBlockProps) {
  const [questions, setQuestions] = useState<CommunityQuestion[]>([]);
  const [answers, setAnswers] = useState<AnswersByQuestion>({});
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<StatusState>({
    kind: "idle",
    message: "",
  });
  const [questionTitle, setQuestionTitle] = useState("");
  const [questionBody, setQuestionBody] = useState("");
  const [answerDrafts, setAnswerDrafts] = useState<Record<string, string>>({});
  const [reportType, setReportType] = useState<ReportType>("outdated");
  const [reportMessage, setReportMessage] = useState("");
  const [ratingComment, setRatingComment] = useState("");
  const [realityGapScore, setRealityGapScore] = useState(50);

  const identityId = useMemo(() => anonymousIdentity("community"), []);

  useEffect(() => {
    let cancelled = false;

    async function loadCommunity() {
      setLoading(true);
      try {
        const response = await communityApi.listCommunityQuestions({
          country_slug: countrySlug,
          limit: 20,
        });
        if (cancelled) return;
        setQuestions(response.items);
        const answerPairs = await Promise.all(
          response.items.map(async (question) => {
            const rows = await communityApi.listCommunityAnswers(question.id);
            return [question.id, rows] as const;
          }),
        );
        if (!cancelled) {
          setAnswers(Object.fromEntries(answerPairs));
        }
      } catch (error: unknown) {
        if (!cancelled) {
          setStatus({
            kind: "error",
            message: errorMessage(
              error,
              "Community content is temporarily unavailable.",
            ),
          });
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadCommunity();
    return () => {
      cancelled = true;
    };
  }, [countrySlug]);

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ kind: "idle", message: "" });
    try {
      const created = await communityApi.createCommunityQuestion({
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

  async function submitAnswer(questionId: string) {
    const body = answerDrafts[questionId]?.trim();
    if (!body) return;
    setStatus({ kind: "idle", message: "" });
    try {
      const created = await communityApi.createCommunityAnswer(questionId, {
        body,
        source_ids: [],
        evidence_item_ids: [],
        created_by_identity_type: "anonymous_session",
        created_by_identity_id: identityId,
      });
      setAnswerDrafts((current) => ({ ...current, [questionId]: "" }));
      setStatus({
        kind: "success",
        message: `Answer received with status ${created.status}; moderation is required before publication.`,
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, "Answer could not be submitted."),
      });
    }
  }

  async function voteAnswer(answerId: string, voteType: "up" | "helpful") {
    setStatus({ kind: "idle", message: "" });
    try {
      const summary = await communityApi.voteCommunityAnswer(answerId, {
        vote_type: voteType,
        identity_type: "anonymous_session",
        identity_id: identityId,
      });
      setStatus({
        kind: "success",
        message: `Vote recorded. Consensus score: ${Math.round(summary.score)}.`,
      });
    } catch (error: unknown) {
      setStatus({
        kind: "error",
        message: errorMessage(error, "Vote could not be submitted."),
      });
    }
  }

  async function submitReport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ kind: "idle", message: "" });
    try {
      const created = await communityApi.createDataErrorReport({
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
      const created = await communityApi.createUserStoryRating({
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
      className="communityBlock"
      data-testid="community-country-block"
    >
      <div className="sectionHeaderBlock">
        <div className="sectionHeaderMain">
          <h3 className="sectionHeaderTitle">Community intelligence</h3>
          <p className="sectionHeaderDesc">
            Human experience is separated from trusted source-backed content and
            appears publicly only after moderation.
          </p>
        </div>
        <span
          className="badge"
          data-testid="community-review-badge"
        >
          review gate
        </span>
      </div>

      {status.kind !== "idle" && (
        <p
          className={status.kind === "error" ? "formError" : "formHint"}
          role={status.kind === "error" ? "alert" : "status"}
          data-testid="community-status"
        >
          {status.message}
        </p>
      )}

      <div className="communityGrid">
        <section
          className="communityPanel"
          data-testid="community-qna-panel"
        >
          <h4>Q&A</h4>
          {loading ? (
            <p className="formHint">Loading community questions...</p>
          ) : questions.length === 0 ? (
            <p
              className="formHint"
              data-testid="community-empty"
            >
              No published community questions yet.
            </p>
          ) : (
            <div className="communityQuestionList">
              {questions.map((question) => (
                <article
                  className="communityQuestion"
                  key={question.id}
                >
                  <div className="communityQuestionHeader">
                    <h5>{question.title}</h5>
                    <span className="badge">{question.status}</span>
                  </div>
                  <p>{question.body}</p>
                  <div className="communityAnswerList">
                    {(answers[question.id] ?? []).map((answer) => (
                      <div
                        className="communityAnswer"
                        key={answer.id}
                      >
                        <p>{answer.body}</p>
                        <div className="metaRow">
                          {answer.source_backed && (
                            <span className="badge">source-backed</span>
                          )}
                          {answer.consensus?.controversial && (
                            <span className="badge metaChipWarn">
                              controversial
                            </span>
                          )}
                          {answer.consensus && (
                            <span className="metaChip">
                              consensus {Math.round(answer.consensus.score)}
                            </span>
                          )}
                        </div>
                        <div className="communityActions">
                          <button
                            type="button"
                            onClick={() => voteAnswer(answer.id, "up")}
                          >
                            Up
                          </button>
                          <button
                            type="button"
                            onClick={() => voteAnswer(answer.id, "helpful")}
                          >
                            Helpful
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="communityInlineForm">
                    <textarea
                      value={answerDrafts[question.id] ?? ""}
                      onChange={(event) =>
                        setAnswerDrafts((current) => ({
                          ...current,
                          [question.id]: event.target.value,
                        }))
                      }
                      placeholder="Add an answer for moderation"
                      aria-label="Community answer"
                    />
                    <button
                      type="button"
                      onClick={() => submitAnswer(question.id)}
                      disabled={!answerDrafts[question.id]?.trim()}
                    >
                      Submit answer
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}

          <form
            className="communityForm"
            onSubmit={submitQuestion}
          >
            <label>
              <span className="formLabel">Question title</span>
              <input
                value={questionTitle}
                onChange={(event) => setQuestionTitle(event.target.value)}
                required
                maxLength={300}
                data-testid="community-question-title"
              />
            </label>
            <label>
              <span className="formLabel">Question details</span>
              <textarea
                value={questionBody}
                onChange={(event) => setQuestionBody(event.target.value)}
                required
                maxLength={4000}
                data-testid="community-question-body"
              />
            </label>
            <button
              type="submit"
              disabled={!questionTitle.trim() || !questionBody.trim()}
              data-testid="community-question-submit"
            >
              Submit for review
            </button>
          </form>
        </section>

        <section
          className="communityPanel"
          data-testid="community-report-panel"
        >
          <h4>Report data issue</h4>
          <form
            className="communityForm"
            onSubmit={submitReport}
          >
            <label>
              <span className="formLabel">Issue type</span>
              <select
                value={reportType}
                onChange={(event) =>
                  setReportType(event.target.value as ReportType)
                }
                data-testid="community-report-type"
              >
                <option value="outdated">Outdated</option>
                <option value="wrong">Wrong</option>
                <option value="missing_source">Missing source</option>
                <option value="contradiction">Contradiction</option>
                <option value="translation_issue">Translation issue</option>
                <option value="other">Other</option>
              </select>
            </label>
            <label>
              <span className="formLabel">Message</span>
              <textarea
                value={reportMessage}
                onChange={(event) => setReportMessage(event.target.value)}
                required
                maxLength={2000}
                data-testid="community-report-message"
              />
            </label>
            <button
              type="submit"
              disabled={!reportMessage.trim()}
              data-testid="community-report-submit"
            >
              Send to review
            </button>
          </form>
        </section>

        <section
          className="communityPanel"
          data-testid="community-rating-panel"
        >
          <h4>Reality gap preview</h4>
          <p className="formHint">
            Limited community input only; no trusted ERG score is calculated
            yet.
          </p>
          <form
            className="communityForm"
            onSubmit={submitRating}
          >
            <label>
              <span className="formLabel">Experience score</span>
              <input
                type="range"
                min="0"
                max="100"
                value={realityGapScore}
                onChange={(event) =>
                  setRealityGapScore(Number(event.target.value))
                }
                data-testid="community-rating-score"
              />
              <span className="summaryValue">{realityGapScore}</span>
            </label>
            <label>
              <span className="formLabel">Optional note</span>
              <textarea
                value={ratingComment}
                onChange={(event) => setRatingComment(event.target.value)}
                maxLength={2000}
                data-testid="community-rating-comment"
              />
            </label>
            <button
              type="submit"
              data-testid="community-rating-submit"
            >
              Submit limited input
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
