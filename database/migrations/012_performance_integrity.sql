-- Migration 012: Performance and integrity pass: adds indexes across translation jobs, glossary, watchlists, and legal signal evidence.
CREATE INDEX IF NOT EXISTS idx_translation_jobs_source_locale_id
    ON translation_jobs(source_locale_id);

CREATE INDEX IF NOT EXISTS idx_translation_jobs_target_locale_id
    ON translation_jobs(target_locale_id);

CREATE INDEX IF NOT EXISTS idx_translation_glossary_source_locale_id
    ON translation_glossary(source_locale_id);

CREATE INDEX IF NOT EXISTS idx_translation_glossary_target_locale_id
    ON translation_glossary(target_locale_id);

CREATE INDEX IF NOT EXISTS idx_watchlists_country_id
    ON watchlists(country_id);

CREATE INDEX IF NOT EXISTS idx_legal_signal_evidence_signal_id
    ON legal_signal_evidence(legal_signal_id);

CREATE INDEX IF NOT EXISTS idx_sources_country_status
    ON sources(country_id, status);

CREATE INDEX IF NOT EXISTS idx_legal_signals_country_type_status
    ON legal_signals(country_id, signal_type, status);

CREATE INDEX IF NOT EXISTS idx_legal_signals_impact_level
    ON legal_signals(impact_level);

ALTER TABLE legal_signals
    DROP CONSTRAINT IF EXISTS legal_signals_country_id_fkey;

ALTER TABLE legal_signals
    ADD CONSTRAINT legal_signals_country_id_fkey
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE RESTRICT;

ALTER TABLE country_scores
    DROP CONSTRAINT IF EXISTS country_scores_country_id_fkey;

ALTER TABLE country_scores
    ADD CONSTRAINT country_scores_country_id_fkey
    FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE RESTRICT;

ALTER TABLE country_scores
    DROP CONSTRAINT IF EXISTS country_scores_scenario_id_fkey;

ALTER TABLE country_scores
    ADD CONSTRAINT country_scores_scenario_id_fkey
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE RESTRICT;
