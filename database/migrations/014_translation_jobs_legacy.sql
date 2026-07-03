-- Migration 014: Makes legacy translation_jobs columns nullable now that the worker foundation (013) owns the new columns.
ALTER TABLE translation_jobs
    ALTER COLUMN entity_type DROP NOT NULL,
    ALTER COLUMN entity_id DROP NOT NULL,
    ALTER COLUMN target_locale_id DROP NOT NULL;
