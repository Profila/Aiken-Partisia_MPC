# Milestone 3 — Secret Input Flow

**Project Catalyst #1200045** | Profila AG x Partisia Blockchain

---

## Objective

Define the test dataset, implement the secret submission flow, and demonstrate
that individual user data is never exposed. Users submit secrets directly to
the PBC contract — not through Cardano. The MPC infrastructure automatically
secret-shares each value across nodes.

---

## Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Dataset defined | `test-data/profila_test_users.json` |
| 2 | PDF documentation | `docs/milestone-3.pdf` |
| 3 | Data type definitions documented | See below |
| 4 | Video of process on PBC testnet | Link in PDF |
| 5 | Secret input process demonstrated | `relay/secret-submissions-log.json` |

---

## Deliverables

### Synthetic Test Dataset

**Generator:** `relay/generate_test_data.ts`
**Output:** `test-data/profila_test_users.json`

| Property | Value |
|----------|-------|
| Total users | 50 |
| Over 18 | 35 (70%) |
| Under/equal 18 | 15 (30%) |
| Survey answer = true | 28 (56%) |
| Survey answer = false | 22 (44%) |
| Countries | CH, DE, GB, US, FR, AU |

**User record structure:**
| Field | Type | MPC Secret? | Description |
|-------|------|-------------|-------------|
| `user_id_hash` | string | No | SHA-256 of synthetic ID |
| `age` | number | **Yes** | User's age |
| `survey_q1_answer` | boolean | **Yes** | Survey response |
| `country_code` | string | No | ISO country code |
| `profila_consent` | boolean | No | Always true for PoC |

> **Privacy note:** `age` and `survey_q1_answer` are the MPC secret fields.
> They go directly to PBC's secret-sharing infrastructure and are never
> visible in any public contract state or Cardano transaction.

**Command:** `npx ts-node relay/generate_test_data.ts`

### Secret Submission Script

**File:** `relay/submit_secrets.ts`

Simulates Profila users submitting their secret values to the PBC contract.
Each user's secret is submitted via the PBC REST API. The script:

1. Loads the test dataset
2. Extracts the secret value based on query type:
   - `age_threshold` → user's age (integer)
   - `survey_match` → 0 or 1
3. Submits each secret to the PBC contract
4. Logs submission metadata (NEVER the actual secret value)
5. Saves log to `relay/secret-submissions-log.json`

**CLI:**
```bash
npx ts-node submit_secrets.ts --contract <PBC_ADDR> --query age_threshold --count 20
npx ts-node submit_secrets.ts --contract <PBC_ADDR> --query survey_match --count 50
```

**Arguments:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--contract` | Yes | env `PBC_CONTRACT_ADDRESS` | PBC contract address |
| `--query` | No | `age_threshold` | Query type |
| `--count` | No | `20` | Number of users to submit (1-50) |

### Privacy Evidence

The submission log intentionally omits secret values:

```json
{
  "user_id_hash": "a1b2c3...",
  "pbc_tx_id": "d4e5f6...",
  "query_type": "age_threshold",
  "submitted_at": "2025-..."
}
```

No `age` or `survey_q1_answer` field appears in any log file, relay output,
or public contract state. Only the aggregate MPC result is ever revealed.

---

## Data Type Definitions

### MPC Secret Fields

| Query Type | Secret Field | PBC Type | Range | Computation |
|------------|-------------|----------|-------|-------------|
| `age_threshold` | `age` | `Sbi64` | 14-75 | Count where value > 18 |
| `survey_match` | `survey_q1_answer` | `Sbi64` | 0 or 1 | Sum all values |

### Expected Results (for verification)

| Query | Input | Expected Count |
|-------|-------|----------------|
| `age_threshold` (> 18) | 50 users (35 over 18) | **35** |
| `survey_match` (= true) | 50 users (28 true) | **28** |

These expected values are embedded in the dataset metadata for automated
verification after MPC computation completes.

---

## Verification

```bash
# 1. Generate test data
npx ts-node relay/generate_test_data.ts

# 2. Inspect dataset metadata (expected results)
cat test-data/profila_test_users.json | head -20

# 3. Submit secrets (requires deployed PBC contract)
npx ts-node relay/submit_secrets.ts --contract <ADDR> --query age_threshold --count 50

# 4. Verify no secrets in logs
cat relay/secret-submissions-log.json
# Confirm: no "age" or "survey_q1_answer" fields present

# 5. Check PBC contract state (via testnet browser)
# https://browser.testnet.partisiablockchain.com/contracts/<ADDR>
# State should show participants count but NOT individual values
```

---

## Status

- [x] Test data generator implemented
- [x] 50-user synthetic dataset generated
- [x] Secret submission script implemented
- [x] Submission log excludes secret values
- [ ] Secrets submitted to PBC testnet contract
- [ ] PBC state evidence captured
- [ ] PDF documentation generated
- [ ] YouTube demo recorded

---

[← Milestone 2](milestone-2.md) | [Back to Milestones](../MILESTONES.md) | [Next: Milestone 4 →](milestone-4.md)
