CREATE TABLE IF NOT EXISTS ai_interaction_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_type TEXT NOT NULL,
    locale TEXT NOT NULL DEFAULT 'ru',
    country_slug TEXT,
    scenario_slug TEXT,
    persona_slug TEXT,
    provider TEXT NOT NULL DEFAULT 'fake',
    provider_model TEXT NOT NULL DEFAULT 'fake-grounded-v1',
    ai_mode TEXT NOT NULL DEFAULT 'fake',
    status TEXT NOT NULL,
    refused BOOLEAN NOT NULL DEFAULT FALSE,
    grounded BOOLEAN NOT NULL DEFAULT TRUE,
    query_hash TEXT,
    sanitized_preview TEXT,
    context_items_count INTEGER NOT NULL DEFAULT 0,
    citations_count INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_interaction_logs_request_type_check
        CHECK (request_type IN (
            'ask',
            'explain_number',
            'decision_intent'
        )),
    CONSTRAINT ai_interaction_logs_locale_check
        CHECK (locale IN ('ru', 'en')),
    CONSTRAINT ai_interaction_logs_ai_mode_check
        CHECK (ai_mode IN ('fake', 'real', 'off')),
    CONSTRAINT ai_interaction_logs_status_check
        CHECK (status IN (
            'completed',
            'refused',
            'failed',
            'feature_disabled'
        )),
    CONSTRAINT ai_interaction_logs_counts_check
        CHECK (
            context_items_count >= 0
            AND citations_count >= 0
        ),
    CONSTRAINT ai_interaction_logs_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT ai_interaction_logs_no_pii_metadata_keys_check
        CHECK (
            NOT metadata ?| ARRAY[
                'email',
                'phone',
                'name',
                'full_name',
                'telegram_user_id',
                'ip',
                'ip_address',
                'user_agent',
                'token',
                'admin_token',
                'password'
            ]
        )
);

CREATE INDEX IF NOT EXISTS idx_ai_interaction_logs_request_type
    ON ai_interaction_logs (request_type);

CREATE INDEX IF NOT EXISTS idx_ai_interaction_logs_created_at
    ON ai_interaction_logs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_interaction_logs_country
    ON ai_interaction_logs (country_slug)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ai_interaction_logs_status
    ON ai_interaction_logs (status);

CREATE INDEX IF NOT EXISTS idx_ai_interaction_logs_query_hash
    ON ai_interaction_logs (query_hash)
    WHERE query_hash IS NOT NULL;

INSERT INTO feature_flags (
    key,
    name,
    description,
    status,
    access_tier,
    default_enabled,
    metadata
)
VALUES
    (
        'ai_augmentation',
        'AI augmentation',
        'Fake-by-default grounded AI assistance.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-grounded-assistant-foundation-v1"}'::jsonb
    ),
    (
        'ai_grounded_qa',
        'Grounded AI Q&A',
        'Question answering limited to published cited project context.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-grounded-assistant-foundation-v1"}'::jsonb
    ),
    (
        'ai_explain_number',
        'AI explain number',
        'Explains already calculated CII, trust, drift, platform and decision scores.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-grounded-assistant-foundation-v1"}'::jsonb
    ),
    (
        'ai_nl_decision',
        'AI natural language decision helper',
        'Converts relocation intent text into decision form hints without running decision.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-grounded-assistant-foundation-v1"}'::jsonb
    )
ON CONFLICT (key) DO UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    access_tier = EXCLUDED.access_tier,
    default_enabled = EXCLUDED.default_enabled,
    metadata = EXCLUDED.metadata,
    updated_at = NOW();

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    ('ai_augmentation', 'public', TRUE),
    ('ai_grounded_qa', 'public', TRUE),
    ('ai_explain_number', 'public', TRUE),
    ('ai_nl_decision', 'public', TRUE)
ON CONFLICT (feature_key, access_tier)
DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
