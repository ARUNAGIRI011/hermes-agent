# Hermes Marketing Agent — Auto-Publishing Architecture

## Scope
Configure this fork for campaign-based social publishing using Hermes Agent and Google Gemini for drafting. Initial targets: Instagram/Facebook (Meta), LinkedIn, YouTube, and TikTok. API access and permissions differ by platform and account type; each connector must be verified before it is enabled.

## Execution flow
Campaign brief -> Gemini drafting -> brand/fact/policy validation -> platform-specific adaptation and media checks -> campaign schedule and timezone -> durable queue/scheduler -> platform connector -> idempotency/retry/rate-limit handling -> audit log and per-platform report.

## Required components
1. **LLM provider:** Hermes native Gemini provider. Configure a key locally; never commit it.
2. **Campaign state:** campaign, brand profile, content version, media references, destination account, schedule, and enabled state.
3. **Scheduler/queue:** durable jobs, timezone-aware times, idempotency keys, bounded retries, exponential backoff, and dead-letter handling.
4. **Connectors:** separate connector per platform with OAuth, least-privilege scopes, token refresh, media upload, publish, status reconciliation, and rate-limit handling.
5. **Safety and governance:** campaign/platform auto-publish enablement, claim checks, audit trail, pause-all switch, and no automatic ad spend.
6. **Observability:** publish status, platform post IDs/URLs, retry counts, sanitized errors, and quota/usage metrics.

## Platform connection notes
- **Instagram/Facebook:** Meta APIs require eligible account/page setup and permissions; Instagram publishing depends on account type and API access. Verify current Meta app review requirements.
- **LinkedIn:** use official APIs and approved permissions for member or organization publishing.
- **YouTube:** use YouTube Data API OAuth. Store visibility (private, unlisted, or public) per campaign; new or unverified API projects may have upload restrictions.
- **TikTok:** use the official Content Posting API and required app scopes/review. The account owner must authorize publishing.
- **Other platforms:** add a dedicated, tested connector or use an authorized publishing provider. Do not promise universal posting.

These are planning notes, not confirmation that accounts are connected or API permissions granted.

## Rollout
1. Configure Gemini and run a generation smoke test.
2. Connect a test account per platform and verify scopes.
3. Test media validation and publish a test post with the account owner's approval.
4. Enable unattended publishing for selected campaigns/platforms only after tests pass.
5. Add monitoring, alerting, token rotation, retry policy, and a global pause control before unattended jobs.

## Secrets
Use Hermes local environment/configuration or a secret manager. Never add real tokens to this repository, example files, issues, prompts, or logs.
