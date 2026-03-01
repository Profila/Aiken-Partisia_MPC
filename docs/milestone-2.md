# Milestone 2 — PBC MPC Contract + Relay

**Project Catalyst #1200045** | Profila AG x Partisia Blockchain

---

## Objective

Deploy a ZK MPC smart contract on Partisia Blockchain testnet that receives
secret inputs and runs privacy-preserving computation. Build an off-chain
relay that bridges Cardano initiation events to PBC contract execution.

---

## Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | PBC unit tests pass | `cargo test` output (8 tests) |
| 2 | Contract executes MPC | PBC testnet contract state |
| 3 | PDF documentation | `docs/milestone-2.pdf` |
| 4 | Test results in docs | Test output saved |
| 5 | YouTube video | Link in PDF |
| 6 | Evidence of Cardano SC initiating PBC contract via relay | `relay/relay-log.json` |

---

## Deliverables

### PBC ZK Contract

**File:** `partisia/contracts/profila_mpc/src/contract.rs`

**Contract state — ProfilaMpcState:**
| Field | Type | Purpose |
|-------|------|---------|
| `administrator` | `Address` | Who deployed the contract |
| `dataset_id` | `Vec<u8>` | Profila dataset identifier |
| `query_type` | `String` | `"age_threshold"` or `"survey_match"` |
| `min_participants` | `u32` | Minimum secrets before compute triggers |
| `result` | `Option<i64>` | Aggregate result (None until computation) |
| `computation_complete` | `bool` | Whether MPC has finished |

**Entry points:**
| Shortname | Function | Description |
|-----------|----------|-------------|
| `init` | `initialize()` | Deploy with dataset params |
| `0x40` | `submit_secret_value()` | User submits a secret (ZK input) |
| `0x41` | `on_variable_inputted()` | Callback when secret is confirmed |
| `0x01` | `start_computation()` | Admin triggers MPC computation |
| `0x42` | `on_compute_complete()` | Callback when MPC finishes |
| — | `on_variables_opened()` | Reads declassified result |

### ZK Computation Kernel

**File:** `partisia/contracts/profila_mpc/src/zk_compute.rs`

The computation runs securely across 4 MPC nodes using secret types (`Sbi64`).
No single node ever sees an individual value.

- **age_threshold:** counts secrets where value > 18
- **survey_match:** sums secrets (each is 0 or 1)

Both use the same unified threshold comparison: `if value > threshold { 1 } else { 0 }`.

### Unit Tests

**File:** `partisia/contracts/profila_mpc/src/contract.rs` (`#[cfg(test)]` module)

| # | Test | What it verifies |
|---|------|-----------------|
| 1 | `test_init_contract_valid_query_types` | Accepts age_threshold and survey_match |
| 2 | `test_init_contract_rejects_invalid_query_types` | Rejects empty, unknown, wrong-case |
| 3 | `test_init_contract_min_participants_validation` | Requires min_participants >= 2 |
| 4 | `test_compute_age_threshold_result` | LE decoding of count=3 (from [25,15,30,12,45]) |
| 5 | `test_compute_survey_match_result` | LE decoding of sum=3 (from [1,0,1,1,0]) |
| 6 | `test_decode_zero_result` | Zero result decoding |
| 7 | `test_decode_large_result` | Large value (10,000) decoding |
| 8 | `test_decode_short_byte_slice` | Short slice zero-padding |

**Command:** `cd partisia/contracts/profila_mpc && cargo test`

> **Note:** ZK runtime functions (`secret_variable_ids`, `load_sbi`) require the
> PBC MPC runtime and are verified via testnet deployment, not unit tests.
> This is the standard PBC testing approach.

### Off-Chain Relay

**File:** `relay/relay.ts`

The relay implements Partisia's documented
[second-layer pattern](https://partisiablockchain.gitlab.io/documentation/smart-contracts/pbc-as-second-layer/partisia-blockchain-as-second-layer.html):

1. Polls Blockfrost for UTxOs at the Cardano script address
2. Parses inline datum (validates dataset_id, query_type, timestamp)
3. Calls PBC REST API to associate with MPC contract
4. Logs relay event to `relay/relay-log.json`
5. Tracks processed UTxOs in `relay/processed.json`

**CLI:**
```bash
npx ts-node relay.ts --once     # Single poll (testing)
npx ts-node relay.ts --watch    # Continuous polling every 30s
```

---

## Verification

```bash
# 1. Run PBC unit tests (requires PBC toolchain)
cd partisia/contracts/profila_mpc && cargo test

# 2. Build PBC contract
cargo pbc build --release

# 3. Deploy to PBC testnet (via browser or CLI)
# https://browser.testnet.partisiablockchain.com

# 4. Run relay
cd relay && npx ts-node relay.ts --once

# 5. Check relay log
cat relay/relay-log.json
```

---

## Status

- [x] PBC ZK contract implemented (contract.rs + zk_compute.rs)
- [x] 8 unit tests written
- [x] Relay script implemented
- [ ] PBC toolchain installed (cargo pbc)
- [ ] Unit tests verified with PBC deps
- [ ] Contract deployed to PBC testnet
- [ ] Relay tested end-to-end
- [ ] PDF documentation generated
- [ ] YouTube demo recorded

---

[← Milestone 1](milestone-1.md) | [Back to Milestones](../MILESTONES.md) | [Next: Milestone 3 →](milestone-3.md)
