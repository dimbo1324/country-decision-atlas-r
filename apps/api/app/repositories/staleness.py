"""Shared "how many days old is too old" windows used by repository-layer
recompute/freshness SQL queries. Centralized so independent call sites
can't drift out of sync via an isolated edit -- every site listed next to
each constant currently agrees on the same value.
"""

# "This derived metric needs recomputing" cutoff -- author reputation,
# platform metrics, trust scores, decision passports, AI data-quality
# checks.
RECOMPUTE_STALE_AFTER_DAYS = 30

# "This source hasn't been re-verified in a while" freshness cutoff used
# by the AI assistant's context-building queries (ai_context.py).
SOURCE_FRESHNESS_STALE_AFTER_DAYS = 365
