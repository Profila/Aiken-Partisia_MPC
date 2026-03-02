# Milestone 1 — Proof of Achievement Report

**Project Catalyst #1200045: MPC as a Layer 2 Service to Cardano**
**Profila AG x Partisia Blockchain**
**Date: 2026-03-01**

---

## 1. Executive Summary

Milestone 1 delivers a fully functional Aiken smart contract deployed to
Cardano preprod testnet. The contract creates an on-chain MPC initiation
record that the off-chain relay (Milestone 2) monitors to bridge Cardano
requests to Partisia Blockchain's MPC infrastructure.

**All 6 acceptance criteria are met.**

---

## 2. Acceptance Criteria — Evidence Matrix

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Aiken unit tests pass | PASS | Section 4 — 6/6 tests pass |
| 2 | Contract has MPC initiation functionality | PASS | Section 3 — validator source |
| 3 | PDF documentation | PASS | This document |
| 4 | Test results in docs | PASS | Section 4 + `cardano/tests/test-results-m1.txt` |
| 5 | YouTube video of demo | PASS | [M1 Demo](https://youtu.be/QRj4tAt23Aw) &bull; [Combined M1-M4](https://youtu.be/jwwfdTSUS2w) |
| 6 | Testnet execution verifiable on-chain | PASS | Section 5 — TX on CardanoScan |

---

## 3. Smart Contract — Technical Summary

### 3.1 Contract Details

| Property | Value |
|----------|-------|
| Language | Aiken v1.1.21 |
| Plutus Version | v3 |
| Validator Hash | `b8bd6946bb4f9ac805f242d86fea090191e64e1250aa8f2d54fc8c67` |
| Script Address | `addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz` |
| Source File | `cardano/validators/profila_mpc.ak` |
| Test File | `cardano/validators/profila_mpc_tests.ak` |

### 3.2 Datum Type — MpcRequest

The contract uses an inline datum to record MPC initiation requests:

| Field | Type | Purpose |
|-------|------|---------|
| `dataset_id` | ByteArray | Identifies the Profila dataset to query |
| `query_type` | ByteArray | `"age_threshold"` or `"survey_match"` |
| `initiator_pkh` | VerificationKeyHash | Public key hash of the requester |
| `partisia_contract` | ByteArray | Target PBC contract address |
| `timestamp` | Int | POSIX timestamp in milliseconds |

### 3.3 Validation Rules

The `InitiateMPC` redeemer enforces 4 validation checks:

1. **Initiator must sign** — `initiator_pkh` must be in `tx.extra_signatories`
2. **Dataset must exist** — `dataset_id` must not be empty
3. **Valid query type** — must be `"age_threshold"` or `"survey_match"`
4. **Positive timestamp** — must be greater than 0

Each check uses Aiken's trace operator (`?`) so failures are logged with
the specific condition that failed (e.g., `"initiator_signed ? False"`).

---

## 4. Unit Tests — Results

**Command:** `cd cardano && aiken check`
**Result:** 6/6 PASSED

| # | Test Name | Expected | Result | Mem | CPU |
|---|-----------|----------|--------|-----|-----|
| 1 | `test_initiate_mpc_valid` | pass | PASS | 37,784 | 12,233,900 |
| 2 | `test_initiate_mpc_empty_dataset` | fail (empty dataset) | PASS | 32,854 | 10,561,421 |
| 3 | `test_initiate_mpc_wrong_signer` | fail (PKH mismatch) | PASS | 33,578 | 10,818,873 |
| 4 | `test_initiate_mpc_bad_query` | fail (bad query_type) | PASS | 39,875 | 12,829,921 |
| 5 | `test_initiate_mpc_bad_timestamp` | fail (timestamp=0) | PASS | 43,796 | 14,301,528 |
| 6 | `test_valid_query_types` | pass (utility fn) | PASS | 7,811 | 1,826,212 |

### Test Trace Output (failure cases)

- Test 2: `dataset_not_empty ? False`
- Test 3: `initiator_signed ? False`
- Test 4: `valid_query_type ? False`
- Test 5: `timestamp_positive ? False`

These traces confirm each validation rule independently rejects invalid inputs.

---

## 5. On-Chain Deployment — Evidence

### 5.1 Transaction Details

| Property | Value |
|----------|-------|
| TX Hash | `50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57` |
| Block | `55f1393cf07c825ca661129dbd42f09c306b255d42e2017e2bee654ddd845019` |
| Block Height | 4,468,996 |
| Slot | 116,719,755 |
| Network | Cardano Preprod |
| Fee | 169,505 lovelace (0.169505 tADA) |
| Valid Contract | `true` |

### 5.2 Verification Links

- **CardanoScan:** https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57
- **Script Address:** https://preprod.cardanoscan.io/address/addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz

### 5.3 UTxO at Script Address

The transaction created a UTxO at the script address with:

- **Amount:** 2,000,000 lovelace (2 tADA)
- **Inline Datum (CBOR):**
  ```
  d8799f4f70726f66696c615f746573745f76314d6167655f7468726573686f6c64
  581cfc1c993261d3d3104bcdbf3f54d16c134f634360e9b40a232894322440
  1b0000019cab7101a2ff
  ```

### 5.4 Decoded Inline Datum

| Field | Hex | Decoded Value |
|-------|-----|---------------|
| `dataset_id` | `70726f66696c615f746573745f7631` | `profila_test_v1` |
| `query_type` | `6167655f7468726573686f6c64` | `age_threshold` |
| `initiator_pkh` | `fc1c993261d3d3104bcdbf3f54d16c134f634360e9b40a2328943224` | (28-byte key hash) |
| `partisia_contract` | (empty) | (to be filled in M2) |
| `timestamp` | `0x0000019cab7101a2` | 2026-03-01T22:07:15Z |

### 5.5 Independent Verification

Anyone can verify this deployment:

```bash
# Via Blockfrost API
curl -H "project_id: <YOUR_KEY>" \
  "https://cardano-preprod.blockfrost.io/api/v0/txs/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57/utxos"

# Via CardanoScan (no API key needed)
# https://preprod.cardanoscan.io/transaction/50d28fd...
```

---

## 6. Repository

- **GitHub:** https://github.com/Profila/Aiken-Partisia_MPC
- **Contract source:** `cardano/validators/profila_mpc.ak`
- **Test source:** `cardano/validators/profila_mpc_tests.ak`
- **Deploy script:** `cardano/scripts/deploy-m1.ts`
- **Test results (JSON):** `cardano/tests/test-results-m1.txt`

---

## 7. How This Enables Milestones 2-4

The deployed UTxO at the script address serves as the **on-chain trigger**
for the entire MPC pipeline:

```
M1 (this milestone)       M2 (next)                M3 + M4
UTxO with MpcRequest  →   relay.ts detects it  →   Secrets submitted to PBC
inline datum               calls PBC REST API       MPC computation runs
                                                    Result displayed
```

The relay script (Milestone 2) polls this address via Blockfrost. When it
finds a UTxO with a valid MpcRequest datum, it bridges the request to the
Partisia Blockchain contract — triggering the privacy-preserving computation.

---

## 8. Video Demo Script (for recording)

When recording the YouTube demo, follow these steps:

1. Show terminal: `cd cardano && aiken check` (all 6 tests pass)
2. Show terminal: `aiken build` (generates plutus.json)
3. Show terminal: deploy script output with TX hash
4. Open browser: CardanoScan showing the transaction
5. Highlight: inline datum visible in UTxO output
6. Explain: "This UTxO is what the relay monitors to trigger MPC on Partisia"

Estimated recording time: 2-3 minutes.

---

Profila AG x Partisia Blockchain
Project Catalyst Fund 13 — Proposal #1200045
