# Deterministic Autonomous Software Factory Standard

**Standard Identifier:** OS-FACTORY-01  
**Version:** 1.0.0  
**Organization:** Strategic-Minds-AI  
**Classification:** Engineering Standard / Software Delivery Specification  
**Source Authority:** Operator Directives, `ai-hub-evals`, `ai-hub-control-plane`  
**Last Updated:** 2026-09-21  

---

## 1. Purpose & Scope

### 1.1 Purpose
This standard defines the mandatory, end-to-end operational specification for the Deterministic Autonomous Software Factory within Strategic Minds AI. It establishes an unalterable 21-stage software lifecycle, strict automated quality gates, deterministic repair loops, protected action enforcement, and cryptographic evidence generation to ensure zero human code review bottlenecks while guaranteeing production safety.

### 1.2 Scope
This standard applies to all software, tools, microservices, database schemas, prompt templates, and infrastructure code created, modified, or deployed across the 11 canonical repositories under the `Strategic-Minds-AI` GitHub organization.

---

## 2. Source Authority & First Principles

1. **Zero Unverified Code in Production:** No pull request is merged to `main` or deployed to production without passing all automated quality gates and obtaining `VERIFIED_100` certification.
2. **Deterministic Reproducibility:** Every build, test, and repair step must be completely reproducible using the exact immutable GitHub commit SHA.
3. **Automated Evidence Generation:** Every stage must output machine-readable, cryptographically signed evidence logs stored in Supabase.
4. **Three-Strike Repair Boundary:** A software factory build packet is allowed a maximum of 3 automated repair cycles before it is automatically marked `BLOCKED` and escalated to a human operator.

---

## 3. The 21-Stage Software Development Lifecycle

The autonomous software factory executes code delivery through a strict 21-stage sequential state machine. Skipping stages or altering order is strictly prohibited.

```
 [01] INTAKE ──► [02] SPEC_LOCK ──► [03] PLAN ──► [04] BRANCH_CREATE ──► [05] GENERATE
                                                                                │
 [10] SECURITY_TEST ◄── [09] INTEGRATION_TEST ◄── [08] UNIT_TEST ◄── [07] STATIC_VAL ◄── [06] BUILD
        │
        ▼
 [11] BROWSER_TEST ──► [12] ADVERSARIAL_TEST ──► [13] PREVIEW_DEPLOY ──► [14] ACCEPTANCE
                                                                                │
 [18] MONITOR ◄── [17] SMOKE_TEST ◄── [16] PRODUCTION_DEPLOY ◄── [15] APPROVAL (GATE)
        │
        ▼
 [19] REPAIR (IF FAIL) ──► [20] FINAL_RECEIPT (IF PASS) ──► [21] COMPLETE
```

### 3.1 Stage-by-Stage Operational Specification

#### Stage 01: `INTAKE`
- **Objective:** Ingest feature request, bug report, or system prompt packet.
- **Input:** Operator directive, issue ticket, or automated trigger payload.
- **Execution:** `ai-hub-control-plane` parses ticket, extracts requirements, and generates a structured `BuildPacket`.
- **Output:** Raw `BuildPacket` in Supabase `build_packets` table.
- **Pass Criteria:** Valid JSON schema matching `ai-hub-protocol` intake envelope.

#### Stage 02: `SPEC_LOCK`
- **Objective:** Freeze feature scope and compute target SHA requirements.
- **Input:** Raw `BuildPacket`.
- **Execution:** System validates requirement completeness and computes SHA-256 spec hash.
- **Output:** `SPEC_LOCK` receipt signed by control plane; status locked in Supabase.
- **Pass Criteria:** Spec hash recorded; no ambiguous requirement fields remaining.

#### Stage 03: `PLAN`
- **Objective:** Generate step-by-step task execution graph for autonomous developer swarms.
- **Input:** Locked spec envelope.
- **Execution:** `ai-hub-swarm-runtime` generates DAG (Directed Acyclic Graph) of sub-tasks and code change targets.
- **Output:** Detailed execution plan file in `ai-hub-sandbox`.
- **Pass Criteria:** Task DAG validation pass with defined file targets and test dependencies.

#### Stage 04: `BRANCH_CREATE`
- **Objective:** Provision isolated Git branch or ephemeral repository (`sbx-*`).
- **Input:** Target repository name and execution plan.
- **Execution:** `ai-hub-control-plane` uses short-lived GitHub App token to spawn branch `feat/<packet-id>` or repo `sbx-<packet-id>`.
- **Output:** Isolated Git branch/repo with initial commit.
- **Pass Criteria:** Git reference confirmed active via GitHub API.

#### Stage 05: `GENERATE`
- **Objective:** Produce code modifications and tests via autonomous agent swarms.
- **Input:** Execution plan and branch reference.
- **Execution:** Worker swarms in `ai-hub-swarm-runtime` synthesize code, update schemas, and write unit/integration tests.
- **Output:** Uncommitted code changes staged in branch.
- **Pass Criteria:** All requested files updated with valid syntax.

#### Stage 06: `BUILD`
- **Objective:** Compile code and package assets in an isolated sandbox.
- **Input:** Staged code branch.
- **Execution:** `ai-hub-sandbox` triggers `npm run build` or platform compilation script.
- **Output:** Compiled build artifacts and build logs.
- **Pass Criteria:** Clean compilation with exit code `0` and zero syntax errors.

#### Stage 07: `STATIC_VALIDATION`
- **Objective:** Execute linter, type-checker, and static code analysis.
- **Input:** Compiled build workspace.
- **Execution:** `tsc --noEmit`, `eslint`, and AST static analyzers executed in `ai-hub-sandbox`.
- **Output:** Static analysis report (`validation_typecheck.log`, `validation_lint.log`).
- **Pass Criteria:** 0 type errors, 0 linting errors.

#### Stage 08: `UNIT_TEST`
- **Objective:** Verify isolated function and component logic.
- **Input:** Unit test files produced during `GENERATE`.
- **Execution:** `npm run test:unit` executed via `ai-hub-evals`.
- **Output:** JUnit XML test results and coverage report.
- **Pass Criteria:** 100% test pass rate; line coverage ≥ 85%.

#### Stage 09: `INTEGRATION_TEST`
- **Objective:** Verify multi-module integration and database contract compatibility.
- **Input:** Compiled application and local Supabase emulator instance.
- **Execution:** `npm run test:integration` executed in `ai-hub-sandbox`.
- **Output:** Integration test log and database transaction logs.
- **Pass Criteria:** All API endpoints and DB calls return expected responses.

#### Stage 10: `SECURITY_TEST`
- **Objective:** Scan code for vulnerabilities, hardcoded secrets, and dependency flaws.
- **Input:** Workspace source code and dependency tree.
- **Execution:** `npm audit`, secret scanners, and static application security testing (SAST) tools run by `ai-hub-evals`.
- **Output:** Security audit report (`validation_npm_audit.json`).
- **Pass Criteria:** 0 high or critical vulnerabilities; 0 detected secrets.

#### Stage 11: `BROWSER_TEST`
- **Objective:** Perform end-to-end visual and interaction testing via Cloud Browser engines.
- **Input:** Preview environment endpoint.
- **Execution:** Playwright/Puppeteer headless browser scripts execute user flows in `ai-hub-evals`.
- **Output:** Screenshots, DOM traces, and network logs.
- **Pass Criteria:** Visual regression threshold met; all DOM assertions pass.

#### Stage 12: `ADVERSARIAL_TEST`
- **Objective:** Probe application and prompts for injection, privilege escalation, and edge-case failures.
- **Input:** Deployed preview interface and MCP endpoints.
- **Execution:** Red-team swarm executes automated fuzzing and prompt injection attacks.
- **Output:** Threat model evaluation receipt in Supabase.
- **Pass Criteria:** 0 successful privilege escalations; 0 unhandled prompt injections.

#### Stage 13: `PREVIEW_DEPLOY`
- **Objective:** Deploy verified build to isolated Vercel preview environment.
- **Input:** Validated commit SHA.
- **Execution:** `ai-hub-infra` triggers Vercel Preview Deployment.
- **Output:** Live preview URL (`https://<app>-preview.vercel.app`).
- **Pass Criteria:** HTTP `200 OK` on health check endpoint.

#### Stage 14: `ACCEPTANCE`
- **Objective:** Verify user story acceptance criteria against live preview URL.
- **Input:** Preview URL and original acceptance criteria.
- **Execution:** Automated acceptance worker verifies functional assertions against preview deployment.
- **Output:** Acceptance validation matrix.
- **Pass Criteria:** 100% acceptance criteria verified.

#### Stage 15: `APPROVAL` (PROTECTED GATE)
- **Objective:** Human operator review and authorization for production release.
- **Input:** Aggregated `VERIFIED_100` report, diff summary, and preview URL.
- **Execution:** Operator receives notification in Signal Command Center UI and signs approval receipt.
- **Output:** Signed approval receipt (`approval_id`) recorded in Supabase.
- **Pass Criteria:** Valid cryptographic signature from authorized operator. **(MANDATORY GATE)**.

#### Stage 16: `PRODUCTION_DEPLOY` (PROTECTED ACTION)
- **Objective:** Promote verified preview build to live production environment.
- **Input:** Signed approval receipt and canonical GitHub commit SHA.
- **Execution:** `ai-hub-infra` executes production promotion on Vercel/Railway.
- **Output:** Live production deployment.
- **Pass Criteria:** Production deployment successful; main branch merged.

#### Stage 17: `SMOKE_TEST`
- **Objective:** Post-deployment sanity check on live production endpoints.
- **Input:** Live production URL.
- **Execution:** Synthetic transactions executed against production health endpoints.
- **Output:** Smoke test telemetry log.
- **Pass Criteria:** All core health checks return HTTP `200 OK` within 500ms.

#### Stage 18: `MONITOR`
- **Objective:** Monitor production metrics for regression or error spikes.
- **Input:** Live application telemetry for 300 seconds post-deploy.
- **Execution:** `ai-hub-control-plane` monitors Vercel/Supabase logs for error rates.
- **Output:** 5-minute post-deploy telemetry report.
- **Pass Criteria:** Error rate < 0.01%; 0 unhandled exceptions.

#### Stage 19: `REPAIR` (Conditional State)
- **Objective:** Automated self-healing when failure occurs in stages 06-18.
- **Input:** Failure logs, stack trace, and diff packet.
- **Execution:** Increments repair counter (`repair_count`). If `repair_count` ≤ 3, forwards error context to `ai-hub-swarm-runtime` to generate patch and re-enters lifecycle at Stage 05 (`GENERATE`).
- **Output:** Repair patch commit or `BLOCKED` escalation ticket.
- **Pass Criteria:** Patch generated and re-submitted to build pipeline.

#### Stage 20: `FINAL_RECEIPT`
- **Objective:** Generate permanent cryptographic receipt for the entire software release.
- **Input:** All stage logs, test artifacts, approval receipts, and commit SHA.
- **Execution:** `ai-hub-evals` calculates SHA-256 digest over all evidence files and writes immutable record to Supabase `final_receipts`.
- **Output:** Cryptographic release receipt file.
- **Pass Criteria:** Receipt stored in Supabase with immutable write lock.

---

## 4. Hard Quality Gates & `VERIFIED_100` Certification

To receive the mandatory `VERIFIED_100` certification required for Stage 15 (`APPROVAL`), a build packet must satisfy all 5 hard certification criteria without exception:

1. **All Hard Gates Pass:** 100% pass rate across Static Validation, Unit Tests, Integration Tests, Security Tests, Browser Tests, and Adversarial Tests.
2. **Zero Open P0/P1 Defects:** No known critical or major security vulnerabilities, memory leaks, or functional blockers.
3. **Source-Runtime Parity:** Deployed preview runtime SHA matches source code commit SHA exactly.
4. **Three Fresh Clean Verification Cycles:** The full test suite must pass cleanly 3 consecutive times on the identical commit SHA without intermittent flakiness.
5. **Validator Independence:** Test execution and evidence generation must be performed by `ai-hub-evals` independently of the swarm agent that wrote the code.

---

## 5. Automated Repair Loops & Three-Strike Rule

```
                      ┌─────────────────────────────────┐
                      │    Stage Failure (06 - 18)      │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                       Check Repair Counter (repair_count)
                                      / \
                                     /   \
                        repair_count ≤ 3  repair_count > 3
                                   /       \
                                  ▼         ▼
             ┌─────────────────────────┐   ┌───────────────────────────┐
             │ Increment repair_count  │   │ Mark Build Packet BLOCKED │
             │ Generate Error Diff     │   │ Halt Pipeline Execution   │
             │ Re-enter Stage 05       │   │ Alert Human Operator      │
             └─────────────────────────┘   └───────────────────────────┘
```

- **Maximum Allowed Repairs:** Exactly 3 attempts.
- **Exhaustion Protocol:** If the 3rd repair cycle fails, the build state transitions to `BLOCKED`, all active sandbox leases are preserved for forensic analysis, and an urgent incident is filed in the Operator UI.

---

## 6. Repository Responsibilities in Factory Execution

| Lifecycle Stage Range | Primary Responsible Repository | Supporting Repositories |
| :--- | :--- | :--- |
| **01 - 04 (Intake & Setup)** | `Strategic-Minds-AI/ai-hub-control-plane` | `ai-hub-protocol`, `ai-hub` |
| **05 (Code Generation)** | `Strategic-Minds-AI/ai-hub-swarm-runtime` | `ai-hub-catalog`, `ai-hub-memory` |
| **06 - 07 (Build & Lint)** | `Strategic-Minds-AI/ai-hub-sandbox` | `ai-hub-infra` |
| **08 - 12 (Verification)** | `Strategic-Minds-AI/ai-hub-evals` | `ai-hub-sandbox`, `ai-hub-memory` |
| **13 - 14 (Preview & Acceptance)**| `Strategic-Minds-AI/ai-hub-infra` | `ai-hub-control-plane` |
| **15 - 16 (Approval & Deploy)** | `Strategic-Minds-AI/ai-hub` (Operator UI) | `ai-hub-control-plane`, `ai-hub-infra` |
| **17 - 18 (Smoke & Monitor)** | `Strategic-Minds-AI/ai-hub-control-plane` | `ai-hub-evals` |
| **19 (Automated Repair)** | `Strategic-Minds-AI/ai-hub-swarm-runtime` | `ai-hub-evals`, `ai-hub-sandbox` |
| **20 (Receipt & Completion)** | `Strategic-Minds-AI/ai-hub-evals` | Supabase DB |

---

## 7. Failure Modes & Recovery Procedures

| Failure Event | Impact | Automatic Mitigation | Recovery Action |
| :--- | :--- | :--- | :--- |
| **Flaky Test Failure** | Test suite fails intermittently during Stage 08 or 09. | System retries verification cycle up to 3 times on same SHA. | If failure persists, trigger Stage 19 Repair. |
| **Protected Gate Override Attempt** | Agent attempts Stage 16 without Stage 15 sign-off receipt. | GitHub Branch Protection rejects merge; Control plane logs security alert. | Agent context invalidated; transaction reset. |
| **Preview Deploy Timeout** | Vercel preview deployment stalls (> 5 minutes). | Control plane cancels deployment request and queues retry. | Check Vercel API status and redeploy. |

---

## 8. Factory Service Level Objectives (SLOs)

- **Total Factory Pipeline Cycle Time (Clean Pass):** ≤ 20 minutes from `INTAKE` to `ACCEPTANCE`.
- **Repair Cycle Generation Time:** ≤ 3 minutes per repair attempt.
- **Evidence Logging Latency:** Real-time (≤ 2 seconds post-stage completion).
- **False Positive Test Failure Rate:** < 1.0% across all automated test suites.

---

## 9. Standard Compliance Verification

This standard is automatically enforced by `ai-hub-control-plane` and `ai-hub-evals`. Any attempt to bypass stage execution results in immediate pipeline termination and security auditing.

**Certified By:** Strategic Minds AI Software Governance Board  
**Standard Status:** Active & Enforced
