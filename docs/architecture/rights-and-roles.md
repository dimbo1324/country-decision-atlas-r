# Rights and Roles Model

> A reference document for how users, rights, and moderation are separated. Written for an owner designing a system like this for the first time: first a conceptual primer and common mistakes, then what's already implemented, then the target model and the path there. Owner requirement: the platform must stay minimally dependent on one person or a small circle — that's the subject of section 6.

---

## 1. Primer: four different mechanisms that must not be conflated

Almost every rights-design mistake comes from blending four independent axes. All four already exist in the project — understanding the boundary of each matters.

### Axis 1. Role — "who the user is"

A long-lived account attribute: a regular user, editor, moderator, owner. There should be **few** roles (3–5), changed rarely and only by an explicit administrative action.

### Axis 2. Right/capability — "what the user is allowed to do"

A specific permitted action: "publish author metrics," "moderate the board," "propose countries." There can be many capabilities, and they don't have to line up with roles: a regular user can gain the "metric author" capability without becoming an editor.

### Axis 3. Visibility — "who can see the object"

A property of the **object**, not the user: a board post can be public / members_only / private; a relocation plan can be private / link-only. Rights answer "can I act," visibility answers "who sees the result."

### Axis 4. Feature flag — "does the capability exist on the platform at all"

A kill switch for an entire feature during rollout stages (public/beta/internal/admin tiers). **A flag is not a right**: a flag answers "does the mechanism work on the platform at all," a right answers "is this particular user admitted to it." A common mistake is gating access with flags — then you can neither grant nor revoke access to one person, nor audit it.

### Baseline principles (locked in as invariants)

1. **Deny by default** — anything not explicitly allowed is forbidden.
2. **Least privilege** — every role/grant carries the minimum rights its function needs.
3. **Server-side enforcement only** — the UI may hide buttons, but the truth always lives in the API (already the case: `require_roles` in router dependencies).
4. **Every privileged action is audited** — already done for editorial and board actions (audit_events), extended to everything new.
5. **Rights are data, not code**: granting/revoking must never require a release.

---

## 2. What's already implemented (the factual baseline)

| Mechanism | Implementation | Assessment |
|---|---|---|
| Roles | `users.role`: `user` / `editor` / `moderator` / `owner`; dependencies `require_roles`, `require_editor`, `require_moderator` | Sufficient; no need to grow the role set |
| Capability grants | `user_capabilities` (Episode 3); `has_capability`/`require_capability`/`require_capability_or_roles`; board and Q&A queues moved off `require_moderator` onto scoped capabilities with no behavior change; grant/revoke is owner-only, with an audit record | Implemented per §3 |
| Assignment rules | Promotion/demotion to `owner` is owner-only; an admin users router | The governance foundation exists |
| Sessions | TTL tokens, revoke-all, PBKDF2-SHA256 | Sufficient |
| Visibility | The board: public/members_only/private + PII-free public projections | A template for new domains |
| Feature flags | Statuses + tiers + rules; `ensure_feature_enabled` | Sufficient; use only for rollout |
| Audit | audit_events on editorial actions, board actions, capability grants; `GET /admin/moderation/actions` — a feed with filters and a reject-spike heuristic (Episode 3) | Extend to new privileged actions as they appear |
| Conflict of interest | A moderator never handles their own posts/reports where they're a party (the board, Episode 3); enforced programmatically | Implemented for the board; extend to new moderator domains as they appear |
| Identity | Telegram linking (gRPC), email accounts | Sufficient |

Current distribution (simplified): `user` — personal data and community participation; `editor` — the content core and translations; `moderator` — board/community moderation queues; `owner` — everything, including role management.

The owner noted that they currently hold every role at once, and that this was deliberate — to debug the rights separation while building it. The model below is designed so that state can be exited without a rebuild.

---

## 3. Target model: roles + capability grants

### 3.1 The problem being prevented: role explosion

The new product line brings categories: metric authors, country contributors, board moderators, metric moderators… Making each one a role produces a combinatorial explosion ("author+contributor," "board moderator but not Q&A") and an unmanageable matrix. The standard industry answer: roles stay coarse, and fine-grained permissions are handed out as **capability grants**.

### 3.2 Capability grants

```sql
CREATE TABLE user_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    capability TEXT NOT NULL,          -- namespaced: 'author.metrics',
                                       -- 'contributor.countries',
                                       -- 'moderator.board', 'moderator.metrics',
                                       -- 'moderator.community'
    granted_by UUID NOT NULL REFERENCES users(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,            -- revoke != delete (history is kept)
    note TEXT,
    CONSTRAINT uq_user_capability UNIQUE (user_id, capability)
);
```

Rules:

- **A role expands into a default capability set**: `moderator` automatically holds every `moderator.*`, `editor` holds the editorial ones, `owner` holds all of them. The check is: `has_capability(user, cap) = role covers cap OR there's an active grant`.
- **Grants extend a regular user selectively**: `user` + a grant of `author.metrics` = an author, not an editor and not a moderator.
- Granting and revoking are governance-level actions only (the owner today; a documented process later), each recorded in audit_events.
- Checked in code the same way existing RBAC is: a `require_capability("author.metrics")` dependency alongside `require_roles`.

### 3.3 Moderation scopes

Moderator capabilities are named per domain (`moderator.board`, `moderator.metrics`, `moderator.community`). While there are only one or two moderators, they're granted every scope; the model is already ready for specialization ("moderates metrics but not board conversations") with zero schema changes.

---

## 4. Rights matrix (target)

Legend: A — anonymous, U — user, +AM — grant author.metrics, +CC — grant contributor.countries, M — moderator (within their scope), E — editor, O — owner. "Own" = an object the user owns.

| Action | A | U | +AM | +CC | M | E | O |
|---|---|---|---|---|---|---|---|
| Read published core content | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Decision run / comparison / passports | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Weight profiles, watchlist, relocation plans | — | own | own | own | own | own | own |
| Q&A: ask/answer; reports; story ratings | — | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Board: post, contact request, blocks | — | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Author metrics: create/maintain/submit for publication | — | — | own | — | — | — | ✔ |
| Author metrics: approve/reject/hide | — | — | — | — | ✔(metrics) | — | ✔ |
| Propose a country; maintain the proposed country's data | — | — | — | own | — | — | ✔ |
| Country: transition to review/published | — | — | — | — | — | ✔ | ✔ |
| Content core: CRUD on sources/signals/cards | — | — | — | — | — | ✔ | ✔ |
| Board/Q&A moderation queues; hide; resolve reports | — | — | — | — | ✔(scope) | — | ✔ |
| View private context via a filed report | — | — | — | — | ✔(only the report's subject) | — | ✔ |
| Platform methodology: publish a new parameter version | — | — | — | — | — | — | ✔ |
| Feature flags, granting/revoking capabilities, roles | — | — | — | — | — | — | ✔ |
| Delete another user's account | — | — | — | — | — | — | ✔ |

The "view private data via a report" row is the principled one: a moderator sees private data (a conversation thread, say) **only in the context of a filed report and only its subject matter**; this is fixed in the privacy policy and in the access audit.

---

## 5. The moderator institution

An answer to the owner's request: "specific people with defined rights who handle moderation."

### 5.1 Where they come from

1. **Phase 0 (now)** — the owner holds every role at once; the model is already separated, so this overlap is a temporary configuration, not the architecture.
2. **Phase 1** — the owner invites 1–3 active participants with high **derived** reputation (tenure, Q&A/board contribution, no confirmed reports against them). Grants of `moderator.<scope>` plus mandatory acceptance of a moderator code of conduct.
3. **Phase 2** — moderator applications with formal admission thresholds (reputation, tenure) decided at the governance level.

### 5.2 What a moderator can and cannot do

Can (within their scope): work the queues (metric review, reports, pending Q&A); approve/reject/hide **with a mandatory reason**; freeze threads; temporarily restrict a user (a rate-limit sanction).

Can never: change roles or grants; read private data outside a report's subject matter; edit the content core; change platform methodology; delete accounts; see payment data (once it exists).

### 5.3 Accountability

- Every moderator action lands in audit_events (an existing mechanism) with a reason.
- An owner-facing "moderator actions" governance page: a feed, filters, anomaly detection (a reject spike, working on objects they have a stake in).
- Conflict of interest: a moderator never handles objects where they're a party (an author, a thread participant) — enforced programmatically.
- Revoking a grant is a single action; sanctions are reversible; irreversible actions (deleting an account) are owner-only.

---

## 6. The autonomy pyramid: "less dependence on people"

A direct answer to the owner's request to make the platform more autonomous. Each level offloads the one above it; a human is the last line of defense, not the first filter.

```
Level 3 — OWNER (governance)                assignments, methodology versions,
     ▲   only what can't be delegated          irreversible operations
Level 2 — MODERATORS (escalations)          publication queues, contested reports,
     ▲   only what wasn't resolved below       sanctions
Level 1 — COMMUNITY (self-moderation)       reports, consensus scoring,
     ▲   signals and thresholds                derived reputation,
     │                                          auto-hide after N confirmed
     │                                          reports (with level-2 post-review)
Level 0 — AUTOMATION (rules)                schema validation, PII scanning, rate
         always on, ahead of any human         limits, publication data-quality
                                               gates, report deduplication, k-anonymity
```

Practical consequences:

- No new surface ships without level 0 (already standard: PII scanning, limits, and dq checks exist as reusable mechanisms).
- Level-1 thresholds (how many confirmed reports hide an object before review) are methodology parameters (Episode 1), not constants.
- **Reputation is not a right.** Derived reputation (built the same way as Trust Score: contribution, freshness, confirmation rate, complaints) informs — badges, weight in consensus, admission to a moderator application — but never auto-grants a capability. Granting one is always an explicit governance action. This is the only reliable defense against gaming rights.
- Health metric: the share of objects that reach publication/resolution with no human involvement, at non-decreasing quality (tracked by the data-quality report).

---

## 7. Data ownership

| Category | Data owner | Rights |
|---|---|---|
| Personal (plans, weight profiles, subscriptions, watchlist) | The user | Full control: export, deletion; private-first by default |
| Author content (metrics, route templates) | The author | Maintenance and archiving are the author's; published-version visibility follows the lifecycle; on account deletion, archived with de-identified attribution (see open questions) |
| Core contributions (country data) | The platform (curated) | Contributor attribution is preserved; post-publish edits go through the editorial process |
| Core (sources, signals, platform methodology) | The platform | Editorial (editor) + governance (owner) |

---

## 8. Implementation path

The model ships as a single episode ("Rights and Roles v2," plan Episode 3) **without breaking anything existing**:

1. The `user_capabilities` table + a `require_capability` dependency (modeled on `require_roles`); roles keep working as capability bundles — no existing endpoint changes behavior.
2. Governance admin surfaces: granting/revoking grants, a feed of moderator actions.
3. Audit scaffolding: a reason is mandatory on every moderate action; a conflict-of-interest check.
4. Level-1 auto-sanctions: a parameterized auto-hide threshold on confirmed reports.
5. From there, grants are consumed by Episode 4 (`author.metrics`, `moderator.metrics`) and Episode 5 (`contributor.countries`).

Testing discipline: the matrix in section 4 becomes parameterized tests (action × role/grant → expected status); "deny by default" gets its own test on every new router.
