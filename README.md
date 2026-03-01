# MPC as a Layer 2 Service to Cardano

**Project Catalyst #1200045** | Profila AG x Partisia Blockchain

Privacy-preserving analytics on Cardano using Partisia Blockchain's Multi-Party Computation infrastructure. A data buyer can query demographic datasets (e.g. "how many users are over 18?") without ever seeing individual user records.

## Architecture

```
LAYER 1 — Cardano Preprod
  Aiken contract (MpcRequest datum + InitiateMPC validator)
       |
       v  relay.ts (polls Blockfrost -> calls PBC REST API)
       |
LAYER 2 — Partisia Testnet
  ZK MPC contract (receives secrets, runs private computation)
       |
       v  show_result.ts
       |
RESULT — Aggregate answer, zero individual data exposed
```

The off-chain relay connecting the two chains follows [Partisia's documented second-layer pattern](https://partisiablockchain.gitlab.io/documentation/smart-contracts/pbc-as-second-layer/partisia-blockchain-as-second-layer.html).

## Milestone Status

| Milestone | Title | Status |
|-----------|-------|--------|
| M1 | Aiken SC — MPC Initiation | Build |
| M2 | PBC MPC Contract + Relay | Build |
| M3 | Secret Input Flow | Build |
| M4 | MPC Computation + Closeout | Build |

## Prerequisites

- [Aiken](https://aiken-lang.org) v1.1.21+
- [Rust](https://rustup.rs) + cargo
- [PBC cargo extension](https://partisiablockchain.gitlab.io/documentation/smart-contracts/zk-smart-contracts/compile-and-deploy-zk-contract.html) (for M2)
- Node.js 18+ with `ts-node`
- Blockfrost preprod API key
- Cardano preprod wallet (funded with tADA)
- Partisia testnet account (funded)

## Setup

```bash
# Clone
git clone <REPO_URL>
cd Aiken-Partisia_MPC

# Environment
cp .env.example .env
# Edit .env with your API keys and wallet details

# Aiken (M1)
cd cardano && aiken check && aiken build

# Relay scripts (M2-M4)
cd ../relay && npm install

# Generate test data (M3)
npx ts-node generate_test_data.ts
```

## Usage

```bash
# Run relay (Cardano -> PBC bridge)
npx ts-node relay.ts --once       # Single poll
npx ts-node relay.ts --watch      # Continuous

# Submit secrets to PBC
npx ts-node submit_secrets.ts --contract <ADDR> --query age_threshold --count 20

# Display MPC result
npx ts-node show_result.ts
```

## Repository Structure

```
cardano/                  # M1 — Aiken smart contract
  validators/             #   Validator source code
  tests/                  #   Unit test results
  scripts/                #   Deploy outputs
partisia/                 # M2 — Partisia ZK contract
  contracts/profila_mpc/  #   Rust ZK contract source
  tests/                  #   Test results
  deploy/                 #   Deploy outputs
relay/                    # M2-M4 — TypeScript tooling
  relay.ts                #   Cardano->PBC bridge
  submit_secrets.ts       #   Secret submission CLI
  show_result.ts          #   Result display
  generate_test_data.ts   #   Test data generator
test-data/                # M3 — Synthetic dataset
docs/                     # All milestones — PDFs + evidence
```

## License

MIT

---

Profila AG x Partisia Blockchain | Project Catalyst #1200045
