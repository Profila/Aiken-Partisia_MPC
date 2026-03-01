# Milestone 4 — MPC Computation + Closeout

**Project Catalyst #1200045** | Profila AG x Partisia Blockchain

---

## Objective

Trigger the MPC computation, display and verify the aggregate result,
document the complete end-to-end flow, and produce the final closeout
report for Project Catalyst.

---

## Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | MPC query result documented and displayed | `relay/mpc-result.json` + terminal output |
| 2 | PDF documentation | `docs/milestone-4.pdf` |
| 3 | Final process definition | `docs/e2e-run-log.md` |
| 4 | YouTube video (E2E demo) | Link in PDF |
| 5 | End-to-end on Cardano + PBC testnet | TX hashes in e2e-run-log |
| 6 | Final Closeout Report | `docs/closeout-report.pdf` |
| 7 | Final Closeout Video | YouTube link in closeout |

---

## Deliverables

### MPC Result

**File:** `relay/mpc-result.json`

```json
{
  "query_type": "age_threshold",
  "dataset_id": "profila_test_v1",
  "result": 35,
  "participants": 50,
  "computation_method": "MPC_PBC",
  "pbc_contract_address": "<PBC_CONTRACT_ADDRESS>",
  "pbc_compute_tx_id": "<PBC_COMPUTE_TX_ID>",
  "cardano_initiation_tx": "<CARDANO_TX_HASH>",
  "result_verified_at": "<ISO_TIMESTAMP>",
  "privacy_note": "Aggregate result only. No individual data exposed."
}
```

### Result Display

**File:** `relay/show_result.ts`

Produces two outputs:

1. **Terminal:** Formatted ASCII box with query details, TX hashes, and
   privacy verification checkmarks
2. **HTML:** `relay/result-display.html` — styled dark-theme card with
   explorer links to both Cardano and PBC transactions

**Command:** `npx ts-node relay/show_result.ts`

### End-to-End Run Log

**File:** `docs/e2e-run-log.md`

Documents all 6 stages with actual transaction hashes:

| Stage | Action | Evidence |
|-------|--------|----------|
| 1 | Deploy Aiken contract to Cardano preprod | CardanoScan TX |
| 2 | Submit MpcRequest UTxO (inline datum) | CardanoScan TX |
| 3 | Relay detects UTxO, calls PBC | relay-log.json |
| 4 | Users submit 50 secrets to PBC | secret-submissions-log.json |
| 5 | Admin triggers MPC computation | PBC TX |
| 6 | Result: "35 users match age > 18" | mpc-result.json |

### Closeout Report

**File:** `docs/closeout-report.md` → `docs/closeout-report.pdf`

Catalyst standard format:
- Project summary
- What was built
- Key achievements (privacy preserved, cross-chain MPC working)
- Challenges and solutions
- Budget summary
- Future development potential
- Links to all evidence

---

## E2E Demo Flow (for video)

```
Step 1: Show the Aiken contract source + test results
        $ cd cardano && aiken check
        ✅ 6/6 tests pass

Step 2: Deploy to Cardano preprod
        $ npx ts-node scripts/deploy.ts
        → TX hash on CardanoScan

Step 3: Run the relay
        $ npx ts-node relay/relay.ts --once
        → Detects UTxO, logs to relay-log.json

Step 4: Submit secrets
        $ npx ts-node relay/submit_secrets.ts --query age_threshold --count 50
        → 50 submissions, no secrets in log

Step 5: Trigger computation + show result
        $ npx ts-node relay/show_result.ts

        ╔════════════════════════════════════════════════════════╗
        ║  PROFILA × PARTISIA — MPC RESULT                      ║
        ╠════════════════════════════════════════════════════════╣
        ║  Query:        Age Threshold (> 18)                    ║
        ║  Dataset:      profila_test_v1                         ║
        ║  Participants: 50                                      ║
        ║  Result:       35 users match criteria                 ║
        ╠════════════════════════════════════════════════════════╣
        ║  ✓ No individual data was exposed                      ║
        ║  ✓ Result computed by MPC nodes                        ║
        ╚════════════════════════════════════════════════════════╝

Step 6: Open HTML evidence in browser
        → result-display.html with explorer links
```

---

## Verification

```bash
# 1. Run the full E2E flow (all scripts in sequence)
cd cardano && aiken check                           # M1 tests
cd ../relay
npx ts-node generate_test_data.ts                   # M3 data
npx ts-node relay.ts --once                         # M2 relay
npx ts-node submit_secrets.ts --query age_threshold --count 50  # M3 secrets
npx ts-node show_result.ts                          # M4 result

# 2. Verify result matches expected
# Expected: result = 35 (35 users over 18 in 50-user dataset)
cat relay/mpc-result.json

# 3. Check privacy — no individual data in any output
# relay-log.json: only TX hashes
# secret-submissions-log.json: only user_id_hash + TX IDs
# mpc-result.json: only aggregate result
```

---

## Status

- [x] show_result.ts implemented (terminal + HTML)
- [ ] MPC computation triggered on testnet
- [ ] mpc-result.json populated with real data
- [ ] E2E run log documented
- [ ] Closeout report written
- [ ] PDF documentation generated
- [ ] YouTube E2E demo recorded
- [ ] Closeout video recorded

---

[← Milestone 3](milestone-3.md) | [Back to Milestones](../MILESTONES.md)
