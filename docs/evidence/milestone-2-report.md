# Milestone 2 — Proof of Achievement

**Project:** Profila × Partisia MPC PoC
**Catalyst Proposal:** #1200045 — MPC as a Layer 2 Service to Cardano
**Date:** 2026-03-01
**Network:** Partisia Blockchain Testnet + Cardano Preprod

---

## Summary

Milestone 2 delivers the Partisia Blockchain MPC smart contract, the ZK computation kernel, and the off-chain relay that bridges Cardano Layer 1 to Partisia Layer 2.

---

## Deliverables

### 1. PBC ZK MPC Contract — Compiled & Tested

| Artifact | Path | Size |
|----------|------|------|
| Contract source | `partisia/contracts/profila_mpc/src/contract.rs` | ~350 lines |
| ZK computation | `partisia/contracts/profila_mpc/src/zk_compute.rs` | 54 lines |
| WASM bytecode | `partisia/deploy/profila_mpc.zkwa` | 64 KB |
| ABI definition | `partisia/deploy/profila_mpc.abi` | 433 B |
| Deployable package | `partisia/deploy/profila_mpc.pbc` | 64 KB |

**Build command:** `cargo pbc build --release`
**Toolchain:** cargo-partisia-contract v5.513.0, zkcompiler v6.35.0, SDK v15.1.0

### 2. Unit Tests — 9/9 Passing

```
running 9 tests
test tests::test_compute_age_threshold_result ... ok
test tests::test_compute_survey_match_result ... ok
test tests::test_decode_empty_slice ... ok
test tests::test_decode_large_result ... ok
test tests::test_decode_short_byte_slice ... ok
test tests::test_decode_zero_result ... ok
test tests::test_init_contract_min_participants_validation ... ok
test tests::test_init_contract_rejects_invalid_query_types ... ok
test tests::test_init_contract_valid_query_types ... ok

test result: ok. 9 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

**Test categories:**
- Contract initialisation validation (query types, participant bounds)
- MPC computation result decoding (age threshold, survey match)
- Edge cases (empty, short, zero, large values)

### 3. Off-Chain Relay — Live Cardano Detection

The relay successfully polls the Cardano preprod script address, fetches UTxOs via Blockfrost, decodes the CBOR inline datum via Blockfrost's datum API, and extracts the MpcRequest fields.

**Relay log output:**
```json
{
  "cardano_tx": "50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57",
  "dataset_id": "profila_test_v1",
  "query_type": "age_threshold",
  "pbc_contract_address": "",
  "relayed_at": "2026-03-01T22:53:16.322Z"
}
```

The `pbc_contract_address` will be populated after PBC testnet deployment (manual browser step).

---

## Architecture Verification

```
Cardano Preprod                    Off-Chain Relay                PBC Testnet
┌──────────────┐                 ┌──────────────┐              ┌──────────────┐
│ Aiken SC     │  Blockfrost    │ relay.ts     │  PBC REST    │ ZK Contract  │
│ MpcRequest   │ ──────────────→│ poll UTxOs   │ ──────────→  │ profila_mpc  │
│ inline datum │  API v0        │ parse datum  │  API         │ .zkwa + .abi │
│ TX: 50d28f.. │                │ relay-log    │              │ (ready)      │
└──────────────┘                 └──────────────┘              └──────────────┘
     ✅ ON-CHAIN                      ✅ TESTED                   ✅ COMPILED
```

---

## Verification Commands

```bash
# Run unit tests
cd partisia/contracts && cargo test

# Build ZK contract
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
cd partisia/contracts && cargo pbc build --release

# Test relay (single poll)
cd relay && npx ts-node relay.ts --once

# Verify Cardano UTxO exists
curl -H "project_id: $BLOCKFROST_PROJECT_ID" \
  "https://cardano-preprod.blockfrost.io/api/v0/addresses/$CARDANO_SCRIPT_ADDRESS/utxos"
```

---

## On-Chain References

| Item | Value |
|------|-------|
| Cardano TX | `50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57` |
| Script Address | `addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz` |
| Datum Hash | `ddc7f46e181cb923cef1c46593b04292f360733cfeee98d2b074093e4f6ea1cc` |
| CardanoScan | https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57 |

## SDK & Toolchain Versions

| Tool | Version |
|------|---------|
| cargo-partisia-contract | 5.513.0 |
| PBC SDK | 15.1.0 (git tag) |
| ZK Compiler | 6.35.0 (Maven JAR) |
| Rust | 1.86.0 |
| Java | OpenJDK 17.0.18 |
| wasm32-unknown-unknown | installed via rustup |
