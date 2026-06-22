UPDATE country_score_breakdowns
SET source_ids = '["0b6ed9af-2dd4-4842-aa61-3e37cd35b508","2a096f22-ce0c-4e60-8e9f-1f5d6066c83d","da2a4a7f-656c-4bf8-b73d-8af098b601ed"]'::jsonb
WHERE criterion = 'long_term_status_score'
  AND (source_ids IS NULL OR source_ids = '[]'::jsonb)
  AND country_score_id IN (
      SELECT cs.id
      FROM country_scores cs
      JOIN countries c ON c.id = cs.country_id
      WHERE c.slug = 'russia'
  );
