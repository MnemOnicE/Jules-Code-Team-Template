# Project Plan (Drift Anchor)

This document defines the high-level roadmap and the strict boundaries of the project. Agents must check code changes against this file to prevent scope creep and architectural drift.

## 📍 Roadmap

### Phase 1: Foundation (Current)
- [ ] Establish "The Brain" (Context & Intent)
- [ ] Establish "The Shield" (Zero-Trust Security)
- [ ] Establish "The Proof" (Verification Suite)
- [ ] Establish "The Map" (Architecture Visualization)
- [ ] Establish "The Factory" (Automation)

### Phase 2: Feature Implementation
- [ ] ...

### Known Issues / Deferred
- [ ] **Security:** Track CVE-2025-13465 (lodash-es). Medium severity prototype pollution via `mermaid-js`. Fix deferred until `mermaid-cli` patch.

## 🛑 Definition of Done (DoD)
1.  All code changes are verified by property-based tests.
2.  No new secrets introduced.
3.  Architectural complexity metrics remain within bounds.
4.  Documentation in `/.context` is updated.

## 🚫 Out of Scope
*   Manual API key management (Strict OIDC enforcement).
*   Unverified "happy path" coding.
