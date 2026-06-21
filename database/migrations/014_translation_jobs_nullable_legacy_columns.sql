ALTER TABLE translation_jobs
    ALTER COLUMN entity_type DROP NOT NULL,
    ALTER COLUMN entity_id DROP NOT NULL,
    ALTER COLUMN target_locale_id DROP NOT NULL;
