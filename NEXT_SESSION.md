# Session Complete — E2E Pipeline Run

## Branch
`claude/confirm-project-state-KFnp9`

## What Was Done

### Previous Session (code changes)
- Gas doubled to 50,000 in `submit_secrets.ts`
- Added `compute_survey_sum` ZK function (shortname 0x62) in `zk_compute.rs`
- Added query-type dispatch (`age_threshold` / `survey_match`) in `contract.rs`
- Rewrote `trigger_computation.ts` to use PBC TypeScript SDK programmatically
- Added 2 new unit tests (survey sum decoding + dispatch logic) — 11 total

### This Session (E2E pipeline run)
- Generated new PBC admin key pair (`00ce80e51b802cf27f6091d5d151f9e0e605df8337`)
- Funded admin account with 1B gas via PBC testnet faucet
- Deployed contract to PBC testnet: `039ed9214602f2a93eb05411f852fa78a476607634`
- Submitted 5 secrets via `submit_secrets.ts` (all confirmed on-chain)
- Triggered MPC computation via browser (100M gas) — result = 5 (all 5 users over 18)
- Fixed `trigger_computation.ts`: RPC encoding (added 0x09 prefix), gas bumped to 100M
- Fixed `show_result.ts`: dynamic admin address from deploy-m3.json instead of hardcoded
- Updated all evidence files with new TX hashes and on-chain result
- On-chain state: `computation_complete: true`, `result: 5`

## Key Learnings
1. ZK MPC gas: Computation across 4 nodes requires ~100M gas (not 50K)
2. PBC RPC format: Action shortnames need `0x09` prefix byte (e.g., `[0x09, 0x01]` not `[0x01]`)
3. PBC gas model: Gas from TEST COIN (BYOC) works; `chain/account/` API returns 404 for BYOC-only accounts
4. Contract rebuild skipped: No Rust installed; deployed existing WASM artifacts

## On-Chain References (current)
- **Cardano TX**: `50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57`
- **Cardano Script**: `addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz`
- **PBC Contract**: `039ed9214602f2a93eb05411f852fa78a476607634`
- **PBC Browser**: https://browser.testnet.partisiablockchain.com/contracts/039ed9214602f2a93eb05411f852fa78a476607634
- **Trigger TX**: `d836a6fc075e9ce7f4c77d905975a77a7304818c4c229c77d91a0b36f07c54cc`
- **Secret TXs**: See `relay/secret-submissions-log.json`

## Remaining Work (future session with Rust)
1. Install Rust + `cargo-partisia-contract`
2. Rebuild ZK contract to include `compute_survey_sum`
3. Redeploy with new bytecode
4. Run `survey_match` E2E test
