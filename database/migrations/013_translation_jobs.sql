-- Migration 013: Translation jobs worker foundation: worker-queue columns and indexes for claiming and prioritizing translation jobs.
ALTER TABLE translation_jobs
ADD COLUMN IF NOT EXISTS max_attempts INTEGER NOT NULL DEFAULT 3,
ADD COLUMN IF NOT EXISTS provider_model TEXT,
ADD COLUMN IF NOT EXISTS locked_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS locked_by TEXT,
ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS failed_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS idx_translation_jobs_unique_active_target
ON translation_jobs(translation_unit_id, target_locale_code)
WHERE status IN ('queued', 'running', 'pending', 'processing');

CREATE INDEX IF NOT EXISTS idx_translation_jobs_status_priority
ON translation_jobs(status, priority, created_at);

CREATE INDEX IF NOT EXISTS idx_translation_jobs_locked
ON translation_jobs(locked_at, locked_by);
