"use client";

import { useQuery } from "@tanstack/react-query";
import { Button, Card, Kicker } from "@country-decision-atlas/ui";
import {
  adminCommunityAnswersQuery,
  adminCommunityQuestionsQuery,
  adminDataErrorReportsQuery,
  adminUserStoryRatingsQuery,
  useUpdateCommunityAnswerStatusMutation,
  useUpdateCommunityQuestionStatusMutation,
  useUpdateDataErrorReportStatusMutation,
  useUpdateUserStoryRatingStatusMutation,
} from "../../entities/community/api";
import { isApiError } from "../../shared/api/http";
import { MODERATION_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

function moderationErrorMessage(error: unknown): string | undefined {
  if (isApiError(error)) {
    return typeof error.error?.message === "string"
      ? error.error.message
      : "Произошла ошибка.";
  }
  return error instanceof Error ? error.message : undefined;
}

export function CommunityModerationView() {
  const { status } = useAuthGuard(MODERATION_ROLES);

  const questions = useQuery({
    ...adminCommunityQuestionsQuery("pending"),
    enabled: status === "ok",
  });
  const answers = useQuery({
    ...adminCommunityAnswersQuery("pending"),
    enabled: status === "ok",
  });
  const reports = useQuery({
    ...adminDataErrorReportsQuery("pending"),
    enabled: status === "ok",
  });
  const ratings = useQuery({
    ...adminUserStoryRatingsQuery("pending"),
    enabled: status === "ok",
  });

  const updateQuestion = useUpdateCommunityQuestionStatusMutation();
  const updateAnswer = useUpdateCommunityAnswerStatusMutation();
  const updateReport = useUpdateDataErrorReportStatusMutation();
  const updateRating = useUpdateUserStoryRatingStatusMutation();

  const isLoading =
    status === "loading" ||
    (status === "ok" &&
      (questions.isPending ||
        answers.isPending ||
        reports.isPending ||
        ratings.isPending));

  if (isLoading) {
    return <LoadingState message="Загрузка модерации сообщества…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для модерации."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  const loadError =
    questions.error ?? answers.error ?? reports.error ?? ratings.error;
  const questionItems = questions.data ?? [];
  const answerItems = answers.data ?? [];
  const reportItems = reports.data ?? [];
  const ratingItems = ratings.data ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="community-moderation"
    >
      {loadError != null && (
        <ErrorState error={moderationErrorMessage(loadError)} />
      )}

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Вопросы на модерации</Kicker>
        {questionItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет вопросов на модерации.</p>
        ) : (
          questionItems.map((question) => (
            <div
              key={question.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
              data-testid="community-moderation-question"
            >
              <span className="text-c2 text-sm">{question.title}</span>
              <div className="flex gap-3">
                <Button
                  onClick={() =>
                    updateQuestion.mutate({
                      questionId: question.id,
                      payload: { status: "published" },
                    })
                  }
                  disabled={updateQuestion.isPending}
                  data-testid="community-moderation-question-approve"
                >
                  Approve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    updateQuestion.mutate({
                      questionId: question.id,
                      payload: { status: "rejected" },
                    })
                  }
                  disabled={updateQuestion.isPending}
                >
                  Reject
                </Button>
              </div>
            </div>
          ))
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Ответы на модерации</Kicker>
        {answerItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет ответов на модерации.</p>
        ) : (
          answerItems.map((answer) => (
            <div
              key={answer.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
              data-testid="community-moderation-answer"
            >
              <span className="text-c2 text-sm">{answer.body}</span>
              <div className="flex gap-3">
                <Button
                  onClick={() =>
                    updateAnswer.mutate({
                      answerId: answer.id,
                      payload: { status: "published" },
                    })
                  }
                  disabled={updateAnswer.isPending}
                >
                  Approve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    updateAnswer.mutate({
                      answerId: answer.id,
                      payload: { status: "rejected" },
                    })
                  }
                  disabled={updateAnswer.isPending}
                >
                  Reject
                </Button>
              </div>
            </div>
          ))
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Жалобы на данные</Kicker>
        {reportItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет жалоб на модерации.</p>
        ) : (
          reportItems.map((report) => (
            <div
              key={report.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
              data-testid="community-moderation-report"
            >
              <span className="text-c2 text-sm">
                {report.report_type}: {report.message}
              </span>
              <div className="flex gap-3">
                <Button
                  onClick={() =>
                    updateReport.mutate({
                      reportId: report.id,
                      payload: {
                        status: "resolved",
                        resolution_note: "Resolved by moderator.",
                      },
                    })
                  }
                  disabled={updateReport.isPending}
                >
                  Resolve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    updateReport.mutate({
                      reportId: report.id,
                      payload: {
                        status: "rejected",
                        resolution_note: "Rejected by moderator.",
                      },
                    })
                  }
                  disabled={updateReport.isPending}
                >
                  Reject
                </Button>
              </div>
            </div>
          ))
        )}
      </Card>

      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Reality-gap заявки</Kicker>
        {ratingItems.length === 0 ? (
          <p className="text-c3 text-sm">Нет заявок на модерации.</p>
        ) : (
          ratingItems.map((rating) => (
            <div
              key={rating.id}
              className="border-warm flex items-center justify-between gap-4 border-b py-3 last:border-b-0"
              data-testid="community-moderation-rating"
            >
              <span className="text-c2 text-sm">
                {rating.comment ?? "Без комментария"}
              </span>
              <div className="flex gap-3">
                <Button
                  onClick={() =>
                    updateRating.mutate({
                      ratingId: rating.id,
                      payload: { status: "published" },
                    })
                  }
                  disabled={updateRating.isPending}
                >
                  Approve
                </Button>
                <Button
                  variant="ghost"
                  onClick={() =>
                    updateRating.mutate({
                      ratingId: rating.id,
                      payload: { status: "rejected" },
                    })
                  }
                  disabled={updateRating.isPending}
                >
                  Reject
                </Button>
              </div>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}
