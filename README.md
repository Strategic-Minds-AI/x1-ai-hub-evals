# x1-ai-hub-evals

**Strategic Minds AI — X1 AI Hub OS**

> **Role**: Independent deterministic evaluation, security, protocol conformance, browser, tenant isolation, cost and latency suites.

---

## Authority
Independent verification authority for the X1 AI Hub platform. Computes deterministic quality scores, protocol conformance reports, security audits, and VERIFIED_100 certifications.

Canonical repository: `Strategic-Minds-AI/x1-ai-hub-evals`  
Default branch: `main`  
Bootstrap branch: `bootstrap/x1-ai-hub-os-v1`  
Production release status: **LOCKED** (`production_release: LOCKED`)  
Visibility: **PUBLIC**

---

## Responsibilities
- Run independent deterministic evaluation suites against all system components.
- Audit protocol schema conformance, API contracts, and cross-repo compatibility.
- Execute automated browser end-to-end user experience and flow verification tests.
- Measure cost, latency, token consumption, and tenant isolation integrity across all services.

---

## Non-Responsibilities
- Serving live end-user application traffic.
- Modifying production database state outside of isolated test tenants.

---

## Upstream and Downstream Interfaces

### Upstream Interfaces
- x1-ai-hub-protocol (imports schemas for protocol validation)
- Target endpoints in x1-ai-hub, x1-ai-hub-control-plane, x1-ai-hub-mcp-gateway, and x1-ai-hub-swarm-runtime

### Downstream Interfaces
- x1-ai-hub (publishes verification badges and quality scores)
- Release management pipelines (provides gating audit clearance)

---

## Local Development
Prerequisites: Node.js >= 18, Python 3.11+, Playwright.
Commands:
```bash
npm install
npx playwright install
npm run eval:all # Runs full evaluation suite locally
```

---

## Tests
Evaluator harness self-tests (`npm test`). Synthetic tenant isolation leak detection tests (`npm run test:isolation`). Browser E2E flow tests (`npm run test:e2e`).

---

## Validation Gates
- 100% pass on VERIFIED_100 validation suite before production release lock lifting.
- Latency and cost regression limits strictly enforced (< 5% drift allowance).
- Zero security vulnerability findings in protocol conformance run.
- CI pipeline gate (`.github/workflows/x1-bootstrap-ci.yml`) must pass.

---

## Security
Evaluator operates using isolated, read-only auditor credentials. Synthetic test data strictly confined to dedicated test tenant namespaces (`tenant_eval_*`).

---

## Deployment
Runs as automated GitHub Actions workflows and scheduled evaluation background jobs on Railway.

---

## Rollback
Read-only evaluation service; test harness releases roll back via standard git commit reversion.

---

## Receipts
Emits cryptographically signed `ValidationReceipt` JSON artifacts recording test summary hashes, pass/fail counts, and `VERIFIED_100` compliance status.

---

## Ownership and Handoff
- **Owner**: Strategic Minds AI - Independent QA & Evals Team (`Strategic-Minds-AI`)
- **Handoff Contract**: Owned by Strategic Minds AI - Independent QA & Evals Team (`Strategic-Minds-AI`). Handoff requires `VERIFIED_100` audit certificate, test execution logs, failure fingerprint report, and operator approval.
- **Operating Contract**: All modifications belong to `bootstrap/x1-ai-hub-os-v1` branch until approved by the operator. Changes to machine contracts require dependency impact analysis, counterpart interface updates, and fresh `VERIFIED_100` evidence verification.
