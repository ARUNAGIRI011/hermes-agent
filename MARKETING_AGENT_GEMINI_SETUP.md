# Hermes Marketing Agent + Google Gemini

This fork adds a marketing-agent skill for campaign planning and human-reviewed content drafting. Hermes already provides a native Google Gemini provider; this project does not need a separate Gemini SDK or custom model adapter.

## 1. Get a Gemini API key
1. Create a key in Google AI Studio: https://aistudio.google.com/apikey
2. Keep it private. Do not paste it into chat, commit it, or add it to source files.
3. Free-tier quotas and model availability vary. Agent turns can make multiple model calls, so monitor usage and quotas.

## 2. Configure Hermes
Use the Hermes setup/model picker rather than hard-coding a model ID:

```bash
hermes model
```

Choose **More providers → Google AI Studio**, then select a Gemini model currently available to your API key. Hermes' native provider accepts `GOOGLE_API_KEY` or `GEMINI_API_KEY` and uses the native endpoint:

```text
https://generativelanguage.googleapis.com/v1beta
```

Hermes documentation: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/google-gemini.md

For manual configuration, the shape is:

```yaml
model:
  default: <model-id-shown-by-hermes-model-picker>
  provider: gemini
  base_url: https://generativelanguage.googleapis.com/v1beta
```

Store the API key in Hermes' local environment file (`~/.hermes/.env` on Linux/WSL, or the equivalent Hermes config directory on Windows), not in this repository. Use the documented setup flow for your installed Hermes version.

## 3. Use the marketing skill
Start Hermes and ask for the marketing-agent skill to be used for a campaign, social post, email draft, SEO outline, or content calendar. The skill is in `skills/marketing-agent/SKILL.md`.

## 4. Safe initial operating mode
- Generate drafts only.
- Require a human to approve all content before publishing or sending.
- Connect publishing/email/analytics integrations separately and grant the minimum required permissions.
- Do not put customer personal data, secrets, or unverified claims into prompts.
- Add rate limits, retry/backoff, cost monitoring, and audit logs before unattended jobs.

## 5. Smoke test
Ask Hermes: “Use the marketing-agent skill to draft three LinkedIn posts for [product] aimed at [audience]. Mark all as drafts and list any claims that need verification.”

Confirm the response is grounded, correctly formatted, and clearly marked for human review before connecting any publishing integration.
