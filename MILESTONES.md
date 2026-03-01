# Milestones — Project Catalyst #1200045

**MPC as a Layer 2 Service to Cardano** | Profila AG x Partisia Blockchain

This document tracks progress across the 4 approved milestones.
Each milestone has a dedicated page in `docs/` with full acceptance criteria,
deliverables, evidence checklist, and verification instructions.

---

## Overview

| # | Title | Acceptance Criteria | Status |
|---|-------|---------------------|--------|
| **M1** | [Aiken Smart Contract](docs/milestone-1.md) | Aiken tests pass, MPC initiation on-chain, PDF + video | Build |
| **M2** | [PBC MPC Contract + Relay](docs/milestone-2.md) | PBC tests pass, MPC execution, relay evidence, PDF + video | Build |
| **M3** | [Secret Input Flow](docs/milestone-3.md) | Dataset defined, secret submission demo, PDF + video | Build |
| **M4** | [MPC Computation + Closeout](docs/milestone-4.md) | E2E result, closeout report + video, on-chain verification | Build |

**Status key:** `Not started` · `Build` · `PoA submitted` · `Approved`

---

## Architecture (All Milestones)

```
  LAYER 1 — Cardano Preprod                        LAYER 2 — Partisia Testnet
 ┌───────────────────────────┐                    ┌───────────────────────────┐
 │  Aiken validator (M1)     │                    │  ZK MPC contract (M2)     │
 │  MpcRequest datum         │    relay.ts (M2)   │  submit_secret (M3)       │
 │  InitiateMPC redeemer     │ ─────────────────► │  compute_result (M4)      │
 │  On-chain anchor          │    Blockfrost →    │  Aggregate result         │
 └───────────────────────────┘    PBC REST API    └───────────────────────────┘
                                                            │
                                                   show_result.ts (M4)
                                                            │
                                                   Terminal + HTML evidence
```

**Key design decision:** The off-chain relay follows Partisia's documented
[second-layer bridging pattern](https://partisiablockchain.gitlab.io/documentation/smart-contracts/pbc-as-second-layer/partisia-blockchain-as-second-layer.html).
Secrets go *directly* to PBC — they never pass through Cardano.

---

## Test Summary

| Milestone | Test Type | Count | Framework | Command |
|-----------|-----------|-------|-----------|---------|
| M1 | Aiken unit tests | 6 | `aiken check` | `cd cardano && aiken check` |
| M2 | Rust unit tests | 8 | `cargo test` | `cd partisia/contracts/profila_mpc && cargo test` |
| M3 | Data generation | 1 script | `ts-node` | `npx ts-node relay/generate_test_data.ts` |
| M4 | E2E run | Full flow | CLI scripts | See [docs/milestone-4.md](docs/milestone-4.md) |

---

## Repository Map

```
cardano/                  ← M1
  validators/profila_mpc.ak          Aiken validator
  validators/profila_mpc_tests.ak    6 unit tests
  tests/test-results-m1.txt          Test output (JSON)

partisia/                 ← M2
  contracts/profila_mpc/src/
    contract.rs                      PBC ZK contract + 8 unit tests
    zk_compute.rs                    MPC computation kernel

relay/                    ← M2, M3, M4
  relay.ts                           Cardano → PBC bridge
  submit_secrets.ts                  Secret submission CLI
  show_result.ts                     Result display (terminal + HTML)
  generate_test_data.ts              Synthetic dataset generator

test-data/                ← M3
  profila_test_users.json            50 synthetic users

docs/                     ← All milestones
  milestone-1.md                     M1 detail
  milestone-2.md                     M2 detail
  milestone-3.md                     M3 detail
  milestone-4.md                     M4 detail
```

---

## Quick Links

- [Milestone 1 — Aiken Smart Contract](docs/milestone-1.md)
- [Milestone 2 — PBC MPC Contract + Relay](docs/milestone-2.md)
- [Milestone 3 — Secret Input Flow](docs/milestone-3.md)
- [Milestone 4 — MPC Computation + Closeout](docs/milestone-4.md)
- [README](README.md) — Setup instructions and usage

---

Profila AG x Partisia Blockchain | Project Catalyst #1200045
