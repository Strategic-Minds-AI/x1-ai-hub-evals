# Validator Independence

Repository: `Strategic-Minds-AI/x1-ai-hub-evals`

## Purpose
This document is a mandatory human-readable contract for the repository role: Independent deterministic evaluation, security, protocol conformance, browser, tenant isolation, cost and latency suites.

## Invariants
- Versioned source truth.
- Typed inputs/outputs.
- Explicit allowed/forbidden actions.
- Tenant/security/budget boundaries where applicable.
- Idempotency, timeout, bounded retry and failure state.
- Independent validation and evidence receipt.
- Rollback and exact next action.

## Change rule
Any material edit to this contract must declare changed contract keys and run dependency impact validation before the repository can return to VERIFIED state.
