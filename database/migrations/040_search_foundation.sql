-- Migration 040: Search foundation v1: adds the search_documents table with a full-text vector index and entity/locale/status indexes.
CREATE TABLE IF NOT EXISTS search_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    country_slug TEXT,
    locale TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    body TEXT NOT NULL DEFAULT '',
    path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'published',
    content_hash TEXT NOT NULL,
    source_updated_at TIMESTAMPTZ,
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    search_vector TSVECTOR NOT NULL DEFAULT ''::tsvector,
    CONSTRAINT search_documents_entity_unique
        UNIQUE (entity_type, entity_id, locale),
    CONSTRAINT search_documents_entity_type_check
        CHECK (entity_type IN (
            'country',
            'route',
            'route_checklist_item',
            'legal_signal',
            'source',
            'evidence_item',
            'country_pair_compatibility',
            'methodology',
            'glossary_term'
        )),
    CONSTRAINT search_documents_locale_check
        CHECK (locale IN ('ru', 'en')),
    CONSTRAINT search_documents_status_check
        CHECK (status IN ('published', 'archived'))
);

CREATE INDEX IF NOT EXISTS idx_search_documents_vector
    ON search_documents USING GIN (search_vector);

CREATE INDEX IF NOT EXISTS idx_search_documents_entity
    ON search_documents (entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_search_documents_country
    ON search_documents (country_slug);

CREATE INDEX IF NOT EXISTS idx_search_documents_locale
    ON search_documents (locale);

CREATE INDEX IF NOT EXISTS idx_search_documents_status
    ON search_documents (status);

CREATE INDEX IF NOT EXISTS idx_search_documents_indexed_at
    ON search_documents (indexed_at DESC);

CREATE OR REPLACE FUNCTION build_search_vector(
    p_locale TEXT,
    p_title TEXT,
    p_summary TEXT,
    p_body TEXT
)
RETURNS TSVECTOR
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT
        CASE
            WHEN p_locale = 'ru' THEN
                setweight(to_tsvector('russian', coalesce(p_title, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(p_summary, '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(p_body, '')), 'C')
            ELSE
                setweight(to_tsvector('simple', coalesce(p_title, '')), 'A') ||
                setweight(to_tsvector('simple', coalesce(p_summary, '')), 'B') ||
                setweight(to_tsvector('simple', coalesce(p_body, '')), 'C')
        END;
$$;
