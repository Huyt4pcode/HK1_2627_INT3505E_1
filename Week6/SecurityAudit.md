# Security Audit — Social Network API

The API handles credentials, bearer tokens, and user-generated content. The
following are potential data-exposure risks and the controls that should be
applied.

| # | Potential exposure | Risk | Recommended control |
|---|---|---|---|
| 1 | Passwords exposed through request-body logging, tracing, or error reports on `POST /auth/login` | Account takeover if logs or telemetry are accessed | Redact password fields before logging; never record raw request bodies for authentication endpoints; restrict and audit access to logs |
| 2 | Access or refresh tokens exposed in application logs, URLs, analytics, or crash reports | An attacker can impersonate the user until the token expires or is revoked | Send tokens only over HTTPS in headers or request bodies; never put them in URLs; redact token fields; limit access-token lifetime |
| 3 | Refresh tokens copied or replayed after theft | Persistent account access and repeated token issuance | Rotate refresh tokens after every successful refresh; invalidate the previous token; detect reuse and revoke the token family |
| 4 | User enumeration through different login errors or response timing | Attackers can identify registered email addresses | Return the same generic `401` message for unknown email and incorrect password; normalize response behavior and rate-limit attempts |
| 5 | Posts disclosed through missing authorization or object-level access checks | Private, blocked, or restricted content becomes readable by changing `{id}` | Enforce authorization and visibility rules for every post lookup; return a non-disclosing `404` for posts the caller cannot view |
| 6 | Excessive scopes granted or accepted from `requestedScopes` | Compromised credentials or clients receive more access than necessary | Apply least privilege; allowlist scopes per user/client; grant only authorized scopes and return the actual granted scope |
| 7 | Sensitive account or internal fields included in post/error responses | Exposure of email, moderation notes, database details, stack traces, or secrets | Use explicit response schemas and field allowlists; keep errors generic and correlate them with a non-sensitive request ID |
| 8 | Personal data and post content exposed by unrestricted operational logs or backups | Bulk disclosure after unauthorized access to observability or backup systems | Minimize collected data; redact or pseudonymize identifiers and content; encrypt backups and logs; enforce retention and access controls |
| 9 | Credentials or tokens intercepted in transit | Account and session compromise | Require HTTPS/TLS for all endpoints; reject plaintext HTTP in production; configure secure transport at the edge |
| 10 | Repeated login or refresh attempts reveal credentials or consume resources | Credential stuffing, token abuse, or denial of service | Apply per-account and per-source rate limits; monitor suspicious patterns; use `429` with a safe `Retry-After` value |

Do not include real passwords, access tokens, refresh tokens, or personal data in
examples, committed files, screenshots, or test output.
