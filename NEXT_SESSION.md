# Next Session Tasks — Local Environment

## Branch
`claude/confirm-project-state-KFnp9`

## What Was Done (this session)
- Gas doubled to 50,000 in `submit_secrets.ts` and `trigger_computation.ts`
- Added `compute_survey_sum` ZK function (shortname 0x62) in `zk_compute.rs`
- Added query-type dispatch (`age_threshold` / `survey_match`) in `contract.rs`
- Rewrote `trigger_computation.ts` to use PBC TypeScript SDK programmatically
- Added 2 new unit tests (survey sum decoding + dispatch logic)
- All TypeScript type-checks clean
- `cargo-partisia-contract` installed

## What Needs To Be Done (local session)

### Prerequisites
1. Create `.env` from `.env.example`:
   ```
   cp .env.example .env
   ```
2. Fill in:
   - `BLOCKFROST_PROJECT_ID` — free key from https://blockfrost.io (preprod)
   - `PBC_ACCOUNT_PRIVATE_KEY` — Partisia testnet admin key
   - `PBC_CONTRACT_ADDRESS=0395e78580157893cde88165d1340e0b9992c31417`

### Task 1: Rebuild ZK Contract
```bash
cd partisia/contracts/profila_mpc
cargo pbc build --release
```
Copy outputs to `partisia/deploy/`:
- `profila_mpc.pbc`
- `profila_mpc.zkwa`
- `profila_mpc.abi`

### Task 2: Deploy New Contract to PBC Testnet
Deploy the rebuilt contract with the new `compute_survey_sum` function.
Record the new contract address if it changes.

### Task 3: Submit 5 Secrets
```bash
cd relay
npx ts-node submit_secrets.ts --contract <PBC_ADDR> --query age_threshold --count 5
```
Record the 5 new TX hashes from `relay/secret-submissions-log.json`.

### Task 4: Trigger Computation
```bash
cd relay
npx ts-node trigger_computation.ts
```
Or with `--dry-run` first to verify readiness.

### Task 5: Show Result
```bash
cd relay
npx ts-node show_result.ts
```
Verify `mpc-result.json` and `result-display.html` are generated.

### Task 6: Update Evidence Files
Update these files in `docs/evidence/` with new TX hashes from steps 2-5:
- `e2e-run-log.json`
- `milestone-3-report.json`
- `milestone-4-report.json`
- `closeout-report.json`
- `m1-onchain-utxos.json` (if Cardano state changed)

### Task 7: Commit & Push
Commit all updated artifacts and evidence, push to `claude/confirm-project-state-KFnp9`.

## Key File Paths
| File | Purpose |
|------|---------|
| `partisia/contracts/profila_mpc/src/contract.rs` | ZK contract + dispatch |
| `partisia/contracts/profila_mpc/src/zk_compute.rs` | ZK compute functions |
| `relay/submit_secrets.ts` | Secret submission (gas=50k) |
| `relay/trigger_computation.ts` | SDK-based computation trigger |
| `relay/show_result.ts` | Result fetcher + display |
| `docs/evidence/*.json` | Evidence files needing TX updates |
| `.env.example` | Template for required env vars |

## On-Chain References (current)
- **Cardano TX**: `50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57`
- **Cardano Script**: `addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz`
- **PBC Contract**: `0395e78580157893cde88165d1340e0b9992c31417`
- **PBC Browser**: https://browser.testnet.partisiablockchain.com/contracts/0395e78580157893cde88165d1340e0b9992c31417
