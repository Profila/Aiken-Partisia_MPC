---
title: "E2E Technical Test Flow"
subtitle: "Project Catalyst #1200045 — MPC as a Layer 2 Service to Cardano"
author: "Profila AG × Partisia Blockchain"
date: "2026-03-02"
---

# E2E Technical Test Flow

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Aiken | v1.1.21+ | `curl -sSfL https://install.aiken-lang.org \| bash` |
| Rust | 1.86+ | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| wasm32 target | — | `rustup target add wasm32-unknown-unknown` |
| cargo-partisia | 5.513.0 | `cargo install cargo-partisia-contract` |
| Java | OpenJDK 17 | `brew install openjdk@17` (macOS) |
| Node.js | 18+ | `brew install node` |
| Blockfrost key | — | Free at https://blockfrost.io (Preprod network) |

## 1. Clone & Setup

```
git clone https://github.com/Profila/Aiken-Partisia_MPC.git
cd Aiken-Partisia_MPC
```

## 2. M1 — Verify Cardano Aiken Contract

**Run tests:**

```
cd cardano
aiken check
```

Expected: `6 passed, 0 failed, 0 warnings`

**Verify deployment record:**

```
cat scripts/deploy-m1.json
```

Expected: TX hash `50d28fd2bd...d53a57`, script address `addr_test1wzut662...hkwaz`

**Verify on-chain (browser):**

<https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57>

Check: Scroll to UTxOs → Output #0 to script address → click Datum → inline datum visible

**Verify on-chain (API — use your own Blockfrost key):**

```
curl -H "project_id: YOUR_KEY" \
  "https://cardano-preprod.blockfrost.io/api/v0/txs/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57/utxos"
```

Check: `inline_datum` field is non-null on output 0, decodes to `profila_test_v1` / `age_threshold`

**✅ M1 pass criteria:** 6/6 tests, TX exists on Cardano Preprod with MpcRequest inline datum

## 3. M2 — Verify PBC Contract & Relay

**Run Rust tests:**

```
cd ../partisia/contracts
cargo test
```

Expected: `9 passed; 0 failed`

**Build ZK contract:**

```
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
cargo pbc build --release
```

Expected: Outputs `.wasm`, `.abi`, `.zkbc`, `.zkwa`, `.pbc` — no errors

**Run relay (single poll):**

```
cd ../../relay
npm install
npx ts-node relay.ts --once
```

Expected: Connects to Blockfrost, polls script address.

**Verify relay log:**

```
cat relay-log.json
```

Check: Contains `cardano_tx: 50d28fd2...`, `dataset_id: profila_test_v1`, `query_type: age_threshold`

**Verify PBC contract on-chain (browser):**

<https://browser.testnet.partisiablockchain.com/contracts/0395e78580157893cde88165d1340e0b9992c31417>

Check: State tab shows `administrator`, `dataset_id: profila_test_v1`, `query_type: age_threshold`, `min_participants: 3`

**Verify PBC contract on-chain (API):**

```
curl -s "https://node1.testnet.partisiablockchain.com/chain/contracts/0395e78580157893cde88165d1340e0b9992c31417" | python3 -m json.tool | head -20
```

Check: Returns contract data with `serializedContract` field

**Verify deploy record:**

```
cat ../partisia/deploy/deploy-m3.json
```

Check: `contract_address`, `deployment_tx`, `init_params` match browser state

**✅ M2 pass criteria:** 9/9 Rust tests, ZK contract builds, relay detects Cardano UTxO, PBC contract live on testnet

## 4. M3 — Verify Secret Input Flow & Privacy

**Verify submission log:**

```
cat secret-submissions-log.json
```

Check:

- `total_succeeded: 5`
- Each entry has `pbc_tx_id`, `pbc_sender`, `on_chain: true`
- **NO raw ages or survey answers in the log**

**Verify all 5 TXs on PBC testnet (browser):**

<https://browser.testnet.partisiablockchain.com/contracts/0395e78580157893cde88165d1340e0b9992c31417?tab=transactions>

Check: 5 secret-input transactions from 5 different senders visible

**Verify individual TXs (spot-check any):**

- <https://browser.testnet.partisiablockchain.com/transactions/c4c0450bbb06a9ce5fcce56229e88e0e51ec5aa5a1d706dde1c4313340635e96>
- <https://browser.testnet.partisiablockchain.com/transactions/d774f1f5e64cc14cb220b5d324fe47d319c9f5ceb56eb5a7dd75d3f861f811eb>
- <https://browser.testnet.partisiablockchain.com/transactions/d4ce72e1952064735132d629a3fd3d57f27c8914e57c05ead53111408e2b01a1>
- <https://browser.testnet.partisiablockchain.com/transactions/a61222941b834e8b3cb5afcadaae7ca50b2b273136a266b0a04e5786335390dd>
- <https://browser.testnet.partisiablockchain.com/transactions/9556d0f653e53de13f3ac4d29338d2ff6c4145cc95a78c1a553a77d880313c8d>

Check: Each TX exists, shows secret_input action type

**Privacy verification (browser):**

<https://browser.testnet.partisiablockchain.com/contracts/0395e78580157893cde88165d1340e0b9992c31417>

Check:

- **State tab:** Shows only `administrator`, `dataset_id`, `query_type`, `min_participants` — NO individual ages
- **Secret data tab:** Shows computation status only — NO individual values visible

**Verify test dataset:**

```
cat ../test-data/profila_test_users.json | head -10
```

Check: 50 users, `expected_results.age_threshold_gt_18: 35`

**Verify all tests still pass (no regressions):**

```
cd ../cardano && aiken check
cd ../partisia/contracts && cargo test
```

Expected: 6/6 + 9/9 = 15/15 pass

**✅ M3 pass criteria:** 5 real TXs on PBC testnet, submission log has no raw values, privacy verified in State + Secret data tabs, 15/15 tests pass

## 5. M4 — Verify E2E Result & Closeout

**Run result display:**

```
cd ../../relay
npx ts-node show_result.ts
```

Check: Fetches live PBC state, decodes `ProfilaMpcState`, shows contract fields, displays expected result (35)

**Verify result JSON:**

```
cat mpc-result.json
```

Check: Contains `cardano_initiation_tx`, `pbc_contract_address`, `secret_input_txs` (5 hashes), `privacy_note`

**Verify E2E run log:**

```
cat ../docs/evidence/e2e-run-log.json
```

Check: 6 stages documented with real TX hashes and timestamps

**Verify closeout report:**

```
cat ../docs/evidence/closeout-report.json
```

Check: All 4 milestones status: Complete, test summary 6+9=15, architecture documented

**Cross-chain verification (browser):**

| Chain | URL | What to verify |
|-------|-----|----------------|
| Cardano | <https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57> | Inline datum with `profila_test_v1` |
| PBC | <https://browser.testnet.partisiablockchain.com/contracts/0395e78580157893cde88165d1340e0b9992c31417> | State matches, 5 TXs visible |
| PBC | <https://browser.testnet.partisiablockchain.com/transactions/8e8ea840a7bb7c7a98c0df0a95e78580157893cde88165d1340e0b9992c31417> | Deployment TX exists |

**Open evidence page:**

```
open ../docs/poc-evidence.html
```

Check: All links resolve, TX hashes match on-chain records

**✅ M4 pass criteria:** show_result.ts fetches live state, result JSON has cross-chain references, closeout report complete, all on-chain links resolve

## Quick Checklist

| # | Check | How |
|---|-------|-----|
| 1 | Aiken 6/6 tests | `cd cardano && aiken check` |
| 2 | Rust 9/9 tests | `cd partisia/contracts && cargo test` |
| 3 | ZK contract builds | `cargo pbc build --release` |
| 4 | Relay detects Cardano UTxO | `cd relay && npx ts-node relay.ts --once` |
| 5 | Cardano TX exists | CardanoScan link above |
| 6 | PBC contract live | PBC Browser link above |
| 7 | 5 secret-input TXs exist | PBC Transactions tab |
| 8 | No raw values in logs | `cat relay/secret-submissions-log.json` |
| 9 | No individual data in State tab | PBC Browser → State tab |
| 10 | No individual data in Secret data tab | PBC Browser → Secret data tab |
| 11 | show_result.ts runs | `cd relay && npx ts-node show_result.ts` |
| 12 | Evidence HTML links resolve | `open docs/poc-evidence.html` |
