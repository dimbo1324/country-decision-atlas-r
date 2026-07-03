-- Migration 043: Episode 12-13 closeout: indexes for the community Q&A tables (questions/answers/votes).
-- Closeout guardrails for Episode 12-13 AI/community foundations.
-- Keeps migration 042 stable while adding indexes required by the checklist.

CREATE INDEX IF NOT EXISTS idx_qna_questions_route
    ON qna_questions (route_id)
    WHERE route_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_qna_answers_created_at
    ON qna_answers (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_qna_votes_identity
    ON qna_votes (identity_id);
