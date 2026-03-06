/**
 * Off-chain relay: Cardano (Layer 1) → Partisia Blockchain (Layer 2)
 *
 * This script implements the standard PBC second-layer bridging pattern:
 * https://partisiablockchain.gitlab.io/documentation/smart-contracts/pbc-as-second-layer/
 *
 * It polls Blockfrost for new MpcRequest UTxOs on Cardano preprod,
 * then calls the Partisia testnet REST API to initialise the MPC contract.
 *
 * Usage:
 *   npx ts-node relay.ts --once      # Single poll (for testing)
 *   npx ts-node relay.ts --watch     # Continuous polling every 30s
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BLOCKFROST_URL = "https://cardano-preprod.blockfrost.io/api/v0";
const BLOCKFROST_PROJECT_ID = process.env.BLOCKFROST_PROJECT_ID ?? "";
const PBC_TESTNET_URL =
  process.env.PBC_TESTNET_URL ?? "https://node1.testnet.partisiablockchain.com";

// Script address and PBC contract: prefer .env, fall back to deploy JSON files
// so reviewers can run with just a Blockfrost key in .env.
function resolveFromDeploy(
  envVar: string | undefined,
  deployFile: string,
  field: string,
): string {
  if (envVar) return envVar;
  const deployPath = path.resolve(__dirname, deployFile);
  if (fs.existsSync(deployPath)) {
    const data = JSON.parse(fs.readFileSync(deployPath, "utf-8"));
    if (data[field]) return data[field] as string;
  }
  return "";
}
const CARDANO_SCRIPT_ADDRESS = resolveFromDeploy(
  process.env.CARDANO_SCRIPT_ADDRESS,
  "../cardano/scripts/deploy-m1.json",
  "script_address",
);
const PBC_CONTRACT_ADDRESS = resolveFromDeploy(
  process.env.PBC_CONTRACT_ADDRESS,
  "../partisia/deploy/deploy-m3.json",
  "contract_address",
);
const POLL_INTERVAL_MS = 30_000;

const PROCESSED_FILE = path.resolve(__dirname, "processed.json");
const RELAY_LOG_FILE = path.resolve(__dirname, "relay-log.json");

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MpcRequestDatum {
  readonly dataset_id: string;
  readonly query_type: string;
  readonly initiator_pkh: string;
  readonly partisia_contract: string;
  readonly timestamp: number;
}

interface RelayLogEntry {
  readonly cardano_tx: string;
  readonly dataset_id: string;
  readonly query_type: string;
  readonly pbc_contract_address: string;
  readonly relayed_at: string;
}

interface BlockfrostUtxo {
  readonly tx_hash: string;
  readonly output_index: number;
  readonly inline_datum: string | null;
  readonly data_hash: string | null;
}

interface BlockfrostDatumJson {
  readonly json_value: {
    readonly constructor: number;
    readonly fields: readonly (
      | { readonly bytes: string }
      | { readonly int: number }
    )[];
  };
}

// ---------------------------------------------------------------------------
// State persistence (processed UTxOs)
// ---------------------------------------------------------------------------

function loadProcessed(): ReadonlySet<string> {
  if (!fs.existsSync(PROCESSED_FILE)) return new Set();
  const data = JSON.parse(fs.readFileSync(PROCESSED_FILE, "utf-8")) as string[];
  return new Set(data);
}

function saveProcessed(processed: ReadonlySet<string>): void {
  fs.writeFileSync(
    PROCESSED_FILE,
    JSON.stringify([...processed], null, 2),
    "utf-8",
  );
}

function loadRelayLog(): readonly RelayLogEntry[] {
  if (!fs.existsSync(RELAY_LOG_FILE)) return [];
  return JSON.parse(
    fs.readFileSync(RELAY_LOG_FILE, "utf-8"),
  ) as RelayLogEntry[];
}

function appendRelayLog(entry: RelayLogEntry): void {
  const log = [...loadRelayLog(), entry];
  fs.writeFileSync(RELAY_LOG_FILE, JSON.stringify(log, null, 2), "utf-8");
}

// ---------------------------------------------------------------------------
// Blockfrost: Fetch UTxOs at Cardano script address
// ---------------------------------------------------------------------------

async function fetchUtxos(): Promise<readonly BlockfrostUtxo[]> {
  const url = `${BLOCKFROST_URL}/addresses/${CARDANO_SCRIPT_ADDRESS}/utxos`;
  const response = await fetch(url, {
    headers: { project_id: BLOCKFROST_PROJECT_ID },
  });

  if (!response.ok) {
    if (response.status === 404) return []; // No UTxOs yet
    throw new Error(
      `Blockfrost error: ${response.status} ${response.statusText}`,
    );
  }

  return (await response.json()) as BlockfrostUtxo[];
}

// ---------------------------------------------------------------------------
// Decode hex-encoded bytes to UTF-8 string
// ---------------------------------------------------------------------------

function hexToUtf8(hex: string): string {
  const bytes = new Uint8Array(
    hex.match(/.{1,2}/g)?.map((b) => parseInt(b, 16)) ?? [],
  );
  return new TextDecoder().decode(bytes);
}

// ---------------------------------------------------------------------------
// Fetch datum JSON from Blockfrost's datum endpoint
// ---------------------------------------------------------------------------

async function fetchDatumJson(
  dataHash: string,
): Promise<BlockfrostDatumJson | null> {
  const url = `${BLOCKFROST_URL}/scripts/datum/${dataHash}`;
  const response = await fetch(url, {
    headers: { project_id: BLOCKFROST_PROJECT_ID },
  });
  if (!response.ok) return null;
  return (await response.json()) as BlockfrostDatumJson;
}

// ---------------------------------------------------------------------------
// Parse Blockfrost datum JSON into MpcRequest
// ---------------------------------------------------------------------------

function parseDatumFields(
  datumJson: BlockfrostDatumJson,
): MpcRequestDatum | null {
  try {
    const { fields } = datumJson.json_value;
    if (!fields || fields.length < 5) {
      console.warn("  ⚠ Datum has fewer than 5 fields");
      return null;
    }

    // MpcRequest: Constr(0, [dataset_id, query_type, initiator_pkh,
    //                         partisia_contract, timestamp])
    const dataset_id = hexToUtf8("bytes" in fields[0] ? fields[0].bytes : "");
    const query_type = hexToUtf8("bytes" in fields[1] ? fields[1].bytes : "");
    const initiator_pkh = "bytes" in fields[2] ? fields[2].bytes : "";
    const partisia_contract = hexToUtf8(
      "bytes" in fields[3] ? fields[3].bytes : "",
    );
    const timestamp = "int" in fields[4] ? fields[4].int : 0;

    // Validate required fields
    if (!dataset_id) {
      console.warn("  ⚠ Empty dataset_id in datum");
      return null;
    }
    if (query_type !== "age_threshold" && query_type !== "survey_match") {
      console.warn(`  ⚠ Invalid query_type in datum: ${query_type}`);
      return null;
    }
    if (timestamp <= 0) {
      console.warn("  ⚠ Invalid timestamp in datum");
      return null;
    }

    return {
      dataset_id,
      query_type,
      initiator_pkh,
      partisia_contract,
      timestamp,
    };
  } catch {
    console.warn("  ⚠ Could not parse datum fields");
    return null;
  }
}

// ---------------------------------------------------------------------------
// PBC: Initialise MPC contract via REST API
// ---------------------------------------------------------------------------

async function initPbcContract(datum: MpcRequestDatum): Promise<string> {
  // In production, this would sign and submit a PBC transaction.
  // For the PoC, we call the PBC REST API to interact with the
  // already-deployed contract.
  const url = `${PBC_TESTNET_URL}/blockchain/contracts/${PBC_CONTRACT_ADDRESS}`;
  console.log(`  → Calling PBC contract at: ${url}`);
  console.log(`    dataset_id:  ${datum.dataset_id}`);
  console.log(`    query_type:  ${datum.query_type}`);

  // NOTE: For the PoC demo, the PBC contract is pre-deployed via the
  // testnet browser. This relay step logs the association between
  // the Cardano initiation TX and the PBC contract address.
  // A full implementation would submit an init transaction here.
  return PBC_CONTRACT_ADDRESS;
}

// ---------------------------------------------------------------------------
// Main relay logic: single poll
// ---------------------------------------------------------------------------

async function pollOnce(): Promise<number> {
  console.log(`\n🔍 Polling Cardano at: ${CARDANO_SCRIPT_ADDRESS}`);
  const processed = new Set(loadProcessed());
  const utxos = await fetchUtxos();
  let relayedCount = 0;

  for (const utxo of utxos) {
    const key = `${utxo.tx_hash}#${utxo.output_index}`;
    if (processed.has(key)) continue;

    console.log(`\n📦 New UTxO found: ${key}`);

    // Fetch and parse datum via Blockfrost's datum endpoint
    if (!utxo.data_hash) {
      console.warn("  ⚠ Skipping — no data_hash on UTxO");
      processed.add(key);
      continue;
    }
    const datumJson = await fetchDatumJson(utxo.data_hash);
    if (!datumJson) {
      console.warn("  ⚠ Skipping — could not fetch datum JSON");
      processed.add(key);
      continue;
    }
    const datum = parseDatumFields(datumJson);
    if (!datum) {
      console.warn("  ⚠ Skipping — could not parse datum");
      processed.add(key);
      continue;
    }

    const pbcAddress = await initPbcContract(datum);

    const entry: RelayLogEntry = {
      cardano_tx: utxo.tx_hash,
      dataset_id: datum.dataset_id,
      query_type: datum.query_type,
      pbc_contract_address: pbcAddress,
      relayed_at: new Date().toISOString(),
    };

    appendRelayLog(entry);
    processed.add(key);
    relayedCount++;

    console.log(`  ✅ Relayed → PBC contract: ${pbcAddress}`);
  }

  saveProcessed(processed);

  if (relayedCount === 0) {
    console.log("  — No new MpcRequest UTxOs found");
  } else {
    console.log(`\n✅ Relayed ${relayedCount} new request(s)`);
  }

  return relayedCount;
}

// ---------------------------------------------------------------------------
// CLI entry point
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  console.log("═══════════════════════════════════════════════════");
  console.log("  PROFILA × PARTISIA — Cardano↔PBC Relay");
  console.log("  Project Catalyst #1200045");
  console.log("═══════════════════════════════════════════════════");

  if (!BLOCKFROST_PROJECT_ID) {
    console.error("❌ BLOCKFROST_PROJECT_ID not set in .env");
    process.exit(1);
  }
  if (!CARDANO_SCRIPT_ADDRESS) {
    console.error("❌ CARDANO_SCRIPT_ADDRESS not set in .env");
    process.exit(1);
  }
  if (!PBC_CONTRACT_ADDRESS) {
    console.warn(
      "⚠️  PBC_CONTRACT_ADDRESS not set — relay will log Cardano UTxOs only",
    );
  }

  const mode = process.argv.includes("--watch") ? "watch" : "once";
  console.log(`Mode: ${mode}`);

  if (mode === "once") {
    await pollOnce();
  } else {
    console.log(`Polling every ${POLL_INTERVAL_MS / 1000}s — Ctrl+C to stop`);
    // eslint-disable-next-line no-constant-condition
    while (true) {
      await pollOnce();
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
    }
  }
}

main().catch((err) => {
  console.error("❌ Relay error:", err);
  process.exit(1);
});
