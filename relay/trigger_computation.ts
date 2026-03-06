/**
 * Triggers the MPC computation on the PBC ZK contract.
 *
 * The start_computation action (shortname 0x01) can only be called by the
 * administrator once enough participants have submitted secrets. This script
 * sends the transaction programmatically using the PBC TypeScript SDK.
 *
 * Usage:
 *   npx ts-node trigger_computation.ts            # Trigger computation
 *   npx ts-node trigger_computation.ts --dry-run   # Check readiness only
 *
 * Requirements:
 *   - PBC_CONTRACT_ADDRESS set in .env
 *   - PBC_ACCOUNT_PRIVATE_KEY set in .env (administrator key)
 *   - At least min_participants (3) secrets must have been submitted
 *
 * Browser Alternative:
 *   If the SDK trigger fails, the computation can also be triggered
 *   via the testnet browser:
 *   1. Open: https://browser.testnet.partisiablockchain.com/contracts/{address}
 *   2. Sign in with the administrator's private key
 *   3. Click "Interact" tab
 *   4. Select "start_computation"
 *   5. Click "Send transaction"
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

import {
  BlockchainTransactionClient,
  SenderAuthenticationKeyPair,
} from "@partisiablockchain/blockchain-api-transaction-client";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PBC_API_BASE =
  process.env.PBC_TESTNET_URL ?? "https://node1.testnet.partisiablockchain.com";
const PBC_CONTRACT_ADDRESS = process.env.PBC_CONTRACT_ADDRESS ?? "";
const PBC_ACCOUNT_PRIVATE_KEY = process.env.PBC_ACCOUNT_PRIVATE_KEY ?? "";
const TRIGGER_LOG_PATH = path.resolve(
  __dirname,
  "trigger-computation-log.json",
);

/** Shortname for the start_computation action in the contract ABI. */
const START_COMPUTATION_SHORTNAME = 0x01;

/**
 * Gas to allocate for the computation trigger transaction.
 * ZK MPC computations require ~100M gas since the computation runs
 * across 4 MPC nodes performing secret sharing. Excess gas goes to
 * the contract's balance and is available for future operations.
 */
const TRIGGER_GAS = 100_000_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ContractStateResponse {
  readonly address: string;
  readonly serializedContract: string;
  readonly shardId: string;
  readonly account: {
    readonly balance: { readonly value: string };
  };
}

interface TriggerLogEntry {
  contract_address: string;
  action: string;
  shortname: string;
  triggered_at: string;
  method: string;
  status: string;
  tx_id: string;
  note: string;
}

// ---------------------------------------------------------------------------
// Check contract readiness
// ---------------------------------------------------------------------------

async function checkContractReady(): Promise<{
  readonly ready: boolean;
  readonly reason: string;
  readonly gas: string;
}> {
  const url = `${PBC_API_BASE}/chain/contracts/${PBC_CONTRACT_ADDRESS}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      return { ready: false, reason: `HTTP ${response.status}`, gas: "0" };
    }
    const data = (await response.json()) as ContractStateResponse;
    const gas = data.account.balance.value;

    if (parseInt(gas, 10) <= 0) {
      return { ready: false, reason: "Contract has zero gas", gas };
    }

    return { ready: true, reason: "Contract is live and has gas", gas };
  } catch (err) {
    return { ready: false, reason: `Network error: ${err}`, gas: "0" };
  }
}

// ---------------------------------------------------------------------------
// Log the trigger attempt
// ---------------------------------------------------------------------------

function logTriggerAttempt(entry: TriggerLogEntry): void {
  const existingLog: TriggerLogEntry[] = fs.existsSync(TRIGGER_LOG_PATH)
    ? JSON.parse(fs.readFileSync(TRIGGER_LOG_PATH, "utf-8"))
    : [];

  const updatedLog = [...existingLog, entry];
  fs.writeFileSync(
    TRIGGER_LOG_PATH,
    JSON.stringify(updatedLog, null, 2),
    "utf-8",
  );
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const dryRun = process.argv.includes("--dry-run");

  console.log("═══════════════════════════════════════════════════════════");
  console.log("  PROFILA × PARTISIA — Trigger MPC Computation");
  console.log("  Project Catalyst #1200045");
  console.log("═══════════════════════════════════════════════════════════");

  if (!PBC_CONTRACT_ADDRESS) {
    console.error("❌ PBC_CONTRACT_ADDRESS not set in .env");
    process.exit(1);
  }

  console.log(`\n📋 Contract: ${PBC_CONTRACT_ADDRESS}`);
  console.log(`📋 Action:   start_computation (shortname 0x01)`);
  console.log(`📋 Gas:      ${TRIGGER_GAS}`);
  console.log(`📋 Mode:     ${dryRun ? "DRY RUN" : "LIVE"}\n`);

  // ── 1. Check contract readiness ──────────────────────────────────────
  console.log("🔍 Checking contract readiness...");
  const { ready, reason, gas } = await checkContractReady();

  if (!ready) {
    console.error(`  ❌ Contract not ready: ${reason}`);
    process.exit(1);
  }

  console.log(`  ✅ ${reason}`);
  console.log(`  ⛽ Gas: ${gas}`);

  // ── 2. Trigger computation ────────────────────────────────────────────
  const browserUrl = `https://browser.testnet.partisiablockchain.com/contracts/${PBC_CONTRACT_ADDRESS}`;

  const logEntry: TriggerLogEntry = {
    contract_address: PBC_CONTRACT_ADDRESS,
    action: "start_computation",
    shortname: "0x01",
    triggered_at: new Date().toISOString(),
    method: dryRun ? "dry-run" : "sdk-programmatic",
    status: dryRun ? "documented" : "pending",
    tx_id: "",
    note: "",
  };

  if (dryRun) {
    console.log("\n📴 DRY RUN — checking readiness only\n");
    console.log(`  🌐 Browser fallback: ${browserUrl}\n`);
    logEntry.note = "Dry run — no transaction sent.";
  } else {
    // Validate admin key
    if (!PBC_ACCOUNT_PRIVATE_KEY) {
      console.error("❌ PBC_ACCOUNT_PRIVATE_KEY not set in .env");
      console.log(`\n  Fallback: trigger via browser at:\n  ${browserUrl}\n`);
      process.exit(1);
    }

    console.log("\n🚀 Sending start_computation transaction...\n");

    // Build the RPC payload with PBC's action invocation format.
    // PBC expects: [0x09, shortname] where 0x09 is the RPC prefix for
    // action calls. Without this prefix, the runtime fails with
    // "Unable to read int" when trying to parse the shortname.
    const rpc = Buffer.from([0x09, START_COMPUTATION_SHORTNAME]);

    // Create authenticated transaction client
    const auth = SenderAuthenticationKeyPair.fromString(
      PBC_ACCOUNT_PRIVATE_KEY,
    );
    const txClient = BlockchainTransactionClient.create(PBC_API_BASE, auth);

    // Build the transaction: { address, rpc } per PBC SDK Transaction interface
    const transaction = {
      address: PBC_CONTRACT_ADDRESS,
      rpc: rpc,
    };

    const sent = await txClient.signAndSend(transaction, TRIGGER_GAS);
    const executed = await txClient.waitForInclusionInBlock(sent);

    if (!executed.executionStatus?.success) {
      const errMsg = executed.executionStatus?.failure
        ? JSON.stringify(executed.executionStatus.failure)
        : "Unknown error";
      logEntry.status = "failed";
      logEntry.tx_id = executed.identifier ?? "";
      logEntry.note = `Transaction failed: ${errMsg}`;
      logTriggerAttempt(logEntry);

      console.error(`  ❌ Transaction failed: ${errMsg}`);
      console.log(`\n  Fallback: trigger via browser at:\n  ${browserUrl}\n`);
      process.exit(1);
    }

    logEntry.status = "triggered";
    logEntry.tx_id = executed.identifier;
    logEntry.note =
      "Computation triggered successfully via PBC TypeScript SDK.";

    console.log(`  ✅ Computation triggered!`);
    console.log(`  📝 TX: ${executed.identifier}`);
  }

  // ── 3. Log the attempt ───────────────────────────────────────────────
  logTriggerAttempt(logEntry);
  console.log(`\n📄 Trigger log saved: ${TRIGGER_LOG_PATH}`);

  // ── 4. Post-trigger instructions ─────────────────────────────────────
  console.log("\n  Next steps:");
  console.log("  1. Run: npx ts-node show_result.ts");
  console.log("     → Will fetch updated on-chain state");
  console.log("     → If computation_complete=true, shows MPC result");
  console.log("  2. Result also visible in PBC browser State tab");
  console.log(`     ${browserUrl}`);
  console.log("");
}

main().catch((err) => {
  console.error("❌ Error:", err);
  process.exit(1);
});
