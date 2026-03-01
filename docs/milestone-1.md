# Milestone 1 — Aiken Smart Contract (MPC Initiation)

**Project Catalyst #1200045** | Profila AG x Partisia Blockchain

---

## Objective

Build and deploy an Aiken smart contract on Cardano preprod that authorises
MPC computations. The contract creates an on-chain record (UTxO with inline
datum) that the off-chain relay monitors to trigger Partisia MPC operations.

---

## Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Aiken unit tests pass | `cardano/tests/test-results-m1.txt` (6/6 pass) |
| 2 | Contract has MPC initiation functionality | `cardano/validators/profila_mpc.ak` |
| 3 | PDF documentation | `docs/milestone-1.pdf` |
| 4 | Test results in docs | `cardano/tests/test-results-m1.txt` |
| 5 | YouTube video of demo | Link in PDF |
| 6 | Testnet execution verifiable on-chain | CardanoScan preprod TX |

---

## Deliverables

### Smart Contract

**File:** `cardano/validators/profila_mpc.ak`

**Datum type — MpcRequest:**
| Field | Type | Purpose |
|-------|------|---------|
| `dataset_id` | `ByteArray` | Identifies the Profila dataset to query |
| `query_type` | `ByteArray` | `"age_threshold"` or `"survey_match"` |
| `initiator_pkh` | `VerificationKeyHash` | Who authorised the query |
| `partisia_contract` | `ByteArray` | PBC contract address |
| `timestamp` | `Int` | When the request was created |

**Redeemer:** `InitiateMPC`

**Validation rules:**
1. `initiator_pkh` must be in `tx.extra_signatories`
2. `dataset_id` must not be empty
3. `query_type` must be `"age_threshold"` or `"survey_match"`
4. `timestamp` must be positive

### Unit Tests

**File:** `cardano/validators/profila_mpc_tests.ak`

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | `test_initiate_mpc_valid` | PASS (happy path) | PASS |
| 2 | `test_initiate_mpc_empty_dataset` | FAIL (empty dataset_id) | PASS |
| 3 | `test_initiate_mpc_wrong_signer` | FAIL (PKH mismatch) | PASS |
| 4 | `test_initiate_mpc_bad_query` | FAIL (invalid query_type) | PASS |
| 5 | `test_initiate_mpc_bad_timestamp` | FAIL (timestamp = 0) | PASS |
| 6 | `test_valid_query_types` | PASS (utility fn) | PASS |

**Command:** `cd cardano && aiken check`

---

## Verification

```bash
# 1. Run Aiken tests
cd cardano && aiken check

# 2. Build the contract (generates plutus.json)
aiken build

# 3. Derive script address (for testnet deployment)
# The address is logged during deployment

# 4. Verify on CardanoScan
# https://preprod.cardanoscan.io/address/<SCRIPT_ADDRESS>
```

---

## Deployment (Preprod)

Deployment creates a UTxO at the script address with:
- 2 tADA locked
- Inline datum containing MpcRequest fields
- The UTxO serves as an on-chain anchor for the relay to detect

**Deploy output:** `cardano/scripts/deploy-m1.json`

---

## Status

- [x] Aiken project scaffolded
- [x] Validator implemented with 4 validation rules
- [x] 6 unit tests written and passing
- [x] Test results saved
- [ ] Deployed to Cardano preprod
- [ ] PDF documentation generated
- [ ] YouTube demo recorded

---

[← Back to Milestones](../MILESTONES.md) | [Next: Milestone 2 →](milestone-2.md)
