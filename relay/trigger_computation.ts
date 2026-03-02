/**
 * Triggers the MPC computation on the PBC ZK contract.
 *
 * The start_computation action (shortname 0x01) can only be called by the
 * administrator once enough participants have submitted secrets. This script
 * demonstrates the trigger mechanism and documents the browser-based
 * alternative when the CLI is unavailable.
 *
 * Usage:
 *   npx ts-node trigger_computation.ts [--dry-run]
 *
 * Requirements:
 *   - PBC_CONTRACT_ADDRESS set in .env
 *   - PBC_ACCOUNT_PRIVATE_KEY set in .env (for CLI-based trigger)
 *   - At least min_participants (3) secrets must have been submitted
 *
 * Browser Alternative:
 *   When the PBC CLI is unavailable, the computation can be triggered
 *   via the testnet browser:
 *   1. Open: https://browser.testnet.partisiablockchain.com/contracts/{address}
 *   2. Sign in with the administrator's private key
 *   3. Click "Interact" tab
 *   4. Select "start_computation" action
 *   5. Click "Send transaction"
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PBC_API_BASE =
  process.env.PBC_TESTNET_URL ?? "https://node1.testnet.partisiablockchain.com";
const PBC_CONTRACT_ADDRESS = process.env.PBC_CONTRACT_ADDRESS ?? "";
const TRIGGER_LOG_PATH = path.resolve(__dirname, "trigger-computation-log.json");

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
  readonly contract_address: string;
  readonly action: string;
  readonly shortname: string;
  readonly triggered_at: string;
  readonly method: string;
  readonly status: string;
  readonly note: string;
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

    // Verify contract exists and has gas
    if (parseInt(gas, 10) <= 0) {
      return { ready: false, reason: "Contract has zero gas", gas };
    }

    return { ready: true, reason: "Contract is live and has gas", gas };
  } catch (err) {
    return { ready: false, reason: `Network error: ${err}`, gas: "0" };
  }
}

// ---------------------------------------------------------------------------
// Document the trigger
// ---------------------------------------------------------------------------

function logTriggerAttempt(entry: TriggerLogEntry): void {
  const existingLog: TriggerLogEntry[] = fs.existsSync(TRIGGER_LOG_PATH)
    ? JSON.parse(fs.readFileSync(TRIGGER_LOG_PATH, "utf-8"))
    : [];

  const updatedLog = [...existingLog, entry];
  fs.writeFileSync(TRIGGER_LOG_PATH, JSON.stringify(updatedLog, null, 2), "utf-8");
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

  // ── 2. Trigger or document ───────────────────────────────────────────
  //
  // NOTE: The PBC CLI `cargo pbc transaction` currently returns HTTP 400
  // for all transaction types on testnet (verified with official example
  // contracts). This is a known issue with the CLI tooling.
  //
  // For the PoC, computation trigger is performed via the PBC testnet
  // browser's "Interact" interface, which correctly handles the binder
  // layer and ZK infrastructure parameters.
  //
  // The full programmatic path requires the Partisia TypeScript SDK
  // (off-chain-secret-sharing example shows the pattern) — integrating
  // this is a post-PoC enhancement.

  const browserUrl = `https://browser.testnet.partisiablockchain.com/contracts/${PBC_CONTRACT_ADDRESS}`;

  if (dryRun) {
    console.log("\n📴 DRY RUN — logging trigger intent only\n");
  }

  console.log("  ┌──────────────────────────────────────────────────────┐");
  console.log("  │  Trigger Methods                                    │");
  console.log("  ├──────────────────────────────────────────────────────┤");
  console.log("  │                                                     │");
  console.log("  │  A. Browser (current):                              │");
  console.log("  │     1. Open the PBC browser URL below               │");
  console.log("  │     2. Sign in as administrator                     │");
  console.log("  │     3. Click 'Interact' tab                         │");
  console.log("  │     4. Select 'start_computation'                   │");
  console.log("  │     5. Click 'Send transaction'                     │");
  console.log("  │                                                     │");
  console.log("  │  B. PBC TypeScript SDK (post-PoC):                  │");
  console.log("  │     Use upload-shares / download-shares pattern     │");
  console.log("  │     from pbc-examples/ts/                           │");
  console.log("  │                                                     │");
  console.log("  │  C. cargo pbc CLI (when fixed):                     │");
  console.log("  │     cargo pbc transaction action \\                  │");
  console.log("  │       --net testnet \\                               │");
  console.log("  │       --address <CONTRACT> \\                        │");
  console.log("  │       --action start_computation                    │");
  console.log("  │                                                     │");
  console.log("  └──────────────────────────────────────────────────────┘");
  console.log(`\n  🌐 Browser: ${browserUrl}\n`);

  // ── 3. Log the attempt ───────────────────────────────────────────────
  const logEntry: TriggerLogEntry = {
    contract_address: PBC_CONTRACT_ADDRESS,
    action: "start_computation",
    shortname: "0x01",
    triggered_at: new Date().toISOString(),
    method: dryRun ? "dry-run" : "browser-manual",
    status: dryRun ? "documented" : "pending-browser",
    note:
      "PBC CLI (cargo pbc transaction) returns HTTP 400 for all transaction " +
      "types on testnet. Browser-based trigger via Interact tab is the " +
      "verified working method. See trigger_computation.ts for details.",
  };

  logTriggerAttempt(logEntry);
  console.log(`📄 Trigger log saved: ${TRIGGER_LOG_PATH}`);

  // ── 4. Post-trigger instructions ─────────────────────────────────────
  console.log("\n  After triggering computation:");
  console.log("  1. Run: npx ts-node show_result.ts");
  console.log("     → Will fetch updated on-chain state");
  console.log("     → If computation_complete=true, shows MPC result");
  console.log("  2. Result also visible in PBC browser State tab");
  console.log("");
}

main().catch((err) => {
  console.error("❌ Error:", err);
  process.exit(1);
});
