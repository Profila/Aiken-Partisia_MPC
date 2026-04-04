# Milestone 1 Summary

**Project:** MPC as a Layer 2 Service to Cardano (Catalyst #1200045)
**Partners:** Profila AG x Partisia Blockchain
**Milestone:** Write a smart contract in Cardano (An updated Aiken data subscription smart contract on preprod testnet)

---

## Acceptance Criteria & Evidence

### 1. Smart contract is tested using Aiken unit tests

6 unit tests — all passing. Results: [`cardano/tests/test-results-m1.txt`](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/cardano/tests/test-results-m1.txt)

| Test | Result |
|------|--------|
| test_initiate_mpc_valid | PASS |
| test_initiate_mpc_empty_dataset | PASS |
| test_initiate_mpc_wrong_signer | PASS |
| test_initiate_mpc_bad_query | PASS |
| test_initiate_mpc_bad_timestamp | PASS |
| test_valid_query_types | PASS |

### 2. Smart contract contains functionality to initiate Partisia MPC smart contract

Aiken validator with `MpcRequest` datum and `InitiateMPC` redeemer: [`cardano/validators/profila_mpc.ak`](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/cardano/validators/profila_mpc.ak)

### 3. Documentation provided in PDF format in English

Full milestone report: [`docs/evidence/milestone-1-report.md`](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/docs/evidence/milestone-1-report.md)

### 4. Documentation includes Aiken test script results and smart contract definitions

- Test results: [`cardano/tests/test-results-m1.txt`](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/cardano/tests/test-results-m1.txt)
- Smart contract definitions: [`cardano/validators/profila_mpc.ak`](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/cardano/validators/profila_mpc.ak)
- Unit tests: [`cardano/validators/profila_mpc_tests.ak`](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/cardano/validators/profila_mpc_tests.ak)

### 5. Video uploaded to YouTube

- M1 Demo: https://youtu.be/QRj4tAt23Aw
- Combined M1-M4 Demo: https://youtu.be/jwwfdTSUS2w

### 6. Video includes demo of test script and smart contract executed on testnet

Testnet deployment transaction (Cardano Preprod): [View on CardanoScan](https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57)

Script address: [`addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz`](https://preprod.cardanoscan.io/address/addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz)

---

## Evidence of Milestone Completion

| Evidence | Link |
|----------|------|
| Documentation (GitHub) | [milestone-1-report.md](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/docs/evidence/milestone-1-report.md) |
| Video (YouTube) | [M1 Demo](https://youtu.be/QRj4tAt23Aw) |
| Stakeholder sign-off | [Closeout report approved in repo](https://github.com/Profila/Aiken-Partisia_MPC/blob/main/docs/evidence/closeout-report.json) |
| Repository | [github.com/Profila/Aiken-Partisia_MPC](https://github.com/Profila/Aiken-Partisia_MPC) |
