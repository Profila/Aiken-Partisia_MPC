/**
 * Submits real secret-input transactions to the PBC MPC contract using the
 * official Partisia Blockchain TypeScript SDK.
 *
 * Per the PBC second-layer architecture, secrets go DIRECTLY to PBC —
 * not via Cardano. Each user's private value (age or survey answer) is
 * encrypted and secret-shared by PBC's ZK MPC infrastructure.
 *
 * The SDK creates on-chain ZK input transactions that:
 *   1. Encrypt the secret value for each MPC engine's public key
 *   2. Package encrypted shares into a single transaction
 *   3. Submit the transaction to the PBC blockchain
 *   4. MPC nodes verify and accept the shares asynchronously
 *
 * Usage:
 *   npx ts-node submit_secrets.ts --contract <PBC_ADDR> --query age_threshold --count 5
 *   npx ts-node submit_secrets.ts --query age_threshold --count 3  (uses .env)
 *
 * Each submission uses a unique PBC account (generated at runtime and funded
 * via the testnet faucet). The private keys for previously-used accounts are
 * stored in partisia/keys/ so they can be reused.
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

// PBC TypeScript SDK
import {
  RealZkClient,
  Client as PbcClient,
  CryptoUtils,
} from "@partisiablockchain/zk-client";
import { BitOutput, BN } from "@secata-public/bitmanipulation-ts";
import {
  BlockchainTransactionClient,
  SenderAuthenticationKeyPair,
} from "@partisiablockchain/blockchain-api-transaction-client";

dotenv.config({ path: path.resolve(__dirname, "../.env") });

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const PBC_TESTNET_URL =
  process.env.PBC_TESTNET_URL ??
  "https://node1.testnet.partisiablockchain.com";
const TEST_DATA_PATH = path.resolve(
  __dirname,
  "../test-data/profila_test_users.json"
);
const SUBMISSIONS_LOG_PATH = path.resolve(
  __dirname,
  "secret-submissions-log.json"
);
const KEYS_DIR = path.resolve(__dirname, "../partisia/keys");

/** Shortname for the submit_secret_value ZK action in the contract ABI. */
const SECRET_INPUT_SHORTNAME = 0x40;

/** Gas to allocate per secret-input transaction. */
const GAS_PER_TX = 50_000;

/** Delay (ms) between consecutive submissions to avoid nonce conflicts. */
const INTER_TX_DELAY_MS = 3_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TestUser {
  readonly user_id_hash: string;
  readonly age: number;
  readonly survey_q1_answer: boolean;
  readonly country_code: string;
}

interface TestDataset {
  readonly metadata: { readonly dataset_id: string };
  readonly users: readonly TestUser[];
}

interface SubmissionLogEntry {
  readonly user_id_hash: string;
  readonly pbc_sender: string;
  readonly pbc_tx_id: string;
  readonly query_type: string;
  readonly submitted_at: string;
  readonly on_chain: true;
  // NOTE: The actual secret value is NEVER logged
}

interface SubmissionSummary {
  readonly contract_address: string;
  readonly query_type: string;
  readonly total_attempted: number;
  readonly total_succeeded: number;
  readonly total_failed: number;
  readonly submissions: readonly SubmissionLogEntry[];
  readonly generated_at: string;
}

type QueryType = "age_threshold" | "survey_match";

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------

function parseArgs(): {
  readonly contract: string;
  readonly query: QueryType;
  readonly count: number;
  readonly privateKeys: readonly string[];
} {
  const args = process.argv.slice(2);
  let contract = process.env.PBC_CONTRACT_ADDRESS ?? "";
  let query: QueryType = "age_threshold";
  let count = 5;
  const privateKeys: string[] = [];

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--contract":
        contract = args[++i] ?? "";
        break;
      case "--query":
        query = args[++i] as QueryType;
        break;
      case "--count":
        count = parseInt(args[++i] ?? "5", 10);
        break;
      case "--key":
        privateKeys.push(args[++i] ?? "");
        break;
    }
  }

  if (!contract) {
    console.error(
      "  --contract <PBC_ADDRESS> is required (or set PBC_CONTRACT_ADDRESS in .env)"
    );
    process.exit(1);
  }
  if (query !== "age_threshold" && query !== "survey_match") {
    console.error("  --query must be 'age_threshold' or 'survey_match'");
    process.exit(1);
  }
  if (count < 1 || count > 50) {
    console.error("  --count must be between 1 and 50");
    process.exit(1);
  }

  return { contract, query, count, privateKeys };
}

// ---------------------------------------------------------------------------
// Key management — load or generate PBC accounts
// ---------------------------------------------------------------------------

function loadKeysFromDirectory(): readonly string[] {
  if (!fs.existsSync(KEYS_DIR)) {
    return [];
  }
  return fs
    .readdirSync(KEYS_DIR)
    .filter((f) => f.endsWith(".pk"))
    .map((f) => fs.readFileSync(path.join(KEYS_DIR, f), "utf-8").trim());
}

function saveKey(privateKey: string): void {
  const address = CryptoUtils.privateKeyToAccountAddress(privateKey);
  const keyPath = path.join(KEYS_DIR, `${address}.pk`);
  if (!fs.existsSync(keyPath)) {
    if (!fs.existsSync(KEYS_DIR)) {
      fs.mkdirSync(KEYS_DIR, { recursive: true });
    }
    fs.writeFileSync(keyPath, privateKey, "utf-8");
  }
}

function generateNewKey(): string {
  const keyPair = CryptoUtils.generateKeyPair();
  const pk = keyPair.getPrivate("hex");
  saveKey(pk);
  return pk;
}

/**
 * Builds the pool of private keys for submission. Each unique address can
 * only submit once to the contract (duplicate check in contract code).
 */
function buildKeyPool(
  explicitKeys: readonly string[],
  count: number
): readonly string[] {
  const existing = loadKeysFromDirectory();
  const all = [...explicitKeys, ...existing];

  // Deduplicate by address
  const seen = new Set<string>();
  const unique: string[] = [];
  for (const pk of all) {
    if (!pk) continue;
    const addr = CryptoUtils.privateKeyToAccountAddress(pk);
    if (!seen.has(addr)) {
      seen.add(addr);
      unique.push(pk);
    }
  }

  // Generate additional keys if needed
  while (unique.length < count) {
    const newKey = generateNewKey();
    unique.push(newKey);
  }

  return unique.slice(0, count);
}

// ---------------------------------------------------------------------------
// Extract secret value from user record
// ---------------------------------------------------------------------------

function extractSecretValue(user: TestUser, query: QueryType): number {
  switch (query) {
    case "age_threshold":
      return user.age;
    case "survey_match":
      return user.survey_q1_answer ? 1 : 0;
  }
}

// ---------------------------------------------------------------------------
// Submit a single secret to PBC contract (REAL on-chain transaction)
// ---------------------------------------------------------------------------

async function submitSecret(
  contractAddress: string,
  privateKey: string,
  secretValue: number
): Promise<{ readonly txId: string; readonly sender: string }> {
  // 1. Create PBC client and ZK client for the contract
  const pbcClient = new PbcClient(PBC_TESTNET_URL);
  const zkClient = RealZkClient.create(contractAddress, pbcClient);

  // 2. Derive sender address from private key
  const senderAddress = CryptoUtils.privateKeyToAccountAddress(privateKey);

  // 3. Serialize the secret value as Sbi64 (signed 64-bit integer)
  //    PBC ZK contracts expect BitOutput-encoded secret data
  const secretInput = BitOutput.serializeBits((out) => {
    out.writeSignedBN(new BN(secretValue), 64);
  });

  // 4. Create RPC buffer with the action shortname (0x40 = submit_secret_value)
  const rpc = Buffer.from([SECRET_INPUT_SHORTNAME]);

  // 5. Build the on-chain ZK input transaction
  //    This encrypts the secret for each MPC engine and packages
  //    the encrypted shares into a single blockchain transaction
  const transaction = await zkClient.buildOnChainInputTransaction(
    senderAddress,
    secretInput,
    rpc
  );

  // 6. Create transaction client with the sender's authentication
  const auth = SenderAuthenticationKeyPair.fromString(privateKey);
  const txClient = BlockchainTransactionClient.create(PBC_TESTNET_URL, auth);

  // 7. Sign and send the transaction
  const sent = await txClient.signAndSend(transaction, GAS_PER_TX);

  // 8. Wait for inclusion in a block
  const executed = await txClient.waitForInclusionInBlock(sent);

  if (!executed.executionStatus?.success) {
    throw new Error(
      `Transaction ${executed.identifier} failed on-chain`
    );
  }

  return { txId: executed.identifier, sender: senderAddress };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const { contract, query, count, privateKeys: explicitKeys } = parseArgs();

  console.log("");
  console.log("  PROFILA x PARTISIA -- Secret Submission (REAL)");
  console.log("  Project Catalyst #1200045");
  console.log("  ──────────────────────────────────────────────");
  console.log(`  Contract:  ${contract}`);
  console.log(`  Network:   ${PBC_TESTNET_URL}`);
  console.log(`  Query:     ${query}`);
  console.log(`  Count:     ${count}`);
  console.log(`  Gas/TX:    ${GAS_PER_TX}`);
  console.log("");

  // Load test data
  if (!fs.existsSync(TEST_DATA_PATH)) {
    console.error(`  Test data not found at: ${TEST_DATA_PATH}`);
    console.error("   Run: npx ts-node generate_test_data.ts first");
    process.exit(1);
  }

  const dataset: TestDataset = JSON.parse(
    fs.readFileSync(TEST_DATA_PATH, "utf-8")
  );
  const usersToSubmit = dataset.users.slice(0, count);

  console.log(
    `  Dataset: ${dataset.metadata.dataset_id} (${dataset.users.length} users)`
  );
  console.log(`  Submitting ${usersToSubmit.length} secrets...\n`);

  // Build key pool (one unique PBC account per submission)
  const keyPool = buildKeyPool(explicitKeys, count);

  const log: SubmissionLogEntry[] = [];
  let successCount = 0;
  let failCount = 0;

  for (let i = 0; i < usersToSubmit.length; i++) {
    const user = usersToSubmit[i];
    const secretValue = extractSecretValue(user, query);
    const privateKey = keyPool[i];
    const sender = CryptoUtils.privateKeyToAccountAddress(privateKey);

    try {
      const result = await submitSecret(contract, privateKey, secretValue);

      const entry: SubmissionLogEntry = {
        user_id_hash: user.user_id_hash,
        pbc_sender: result.sender,
        pbc_tx_id: result.txId,
        query_type: query,
        submitted_at: new Date().toISOString(),
        on_chain: true,
        // Secret value is intentionally NOT logged
      };

      log.push(entry);
      successCount++;

      // Progress indicator (don't log the actual value!)
      console.log(
        `  [${i + 1}/${usersToSubmit.length}] OK ${user.user_id_hash.slice(0, 12)}... -> tx:${result.txId.slice(0, 16)}...`
      );
    } catch (err: unknown) {
      failCount++;
      const errMsg = err instanceof Error ? err.message : String(err);
      console.error(
        `  [${i + 1}/${usersToSubmit.length}] FAIL ${user.user_id_hash.slice(0, 12)}... (${sender.slice(0, 12)}...) -> ${errMsg}`
      );
    }

    // Delay between submissions to avoid nonce conflicts
    if (i < usersToSubmit.length - 1) {
      await new Promise((r) => setTimeout(r, INTER_TX_DELAY_MS));
    }
  }

  // Save submission log
  const summary: SubmissionSummary = {
    contract_address: contract,
    query_type: query,
    total_attempted: usersToSubmit.length,
    total_succeeded: successCount,
    total_failed: failCount,
    submissions: log,
    generated_at: new Date().toISOString(),
  };

  fs.writeFileSync(
    SUBMISSIONS_LOG_PATH,
    JSON.stringify(summary, null, 2),
    "utf-8"
  );

  console.log("\n  ──────────────────────────────────────────────");
  console.log(`  Submitted: ${successCount}/${usersToSubmit.length}`);
  if (failCount > 0) {
    console.log(`  Failed:    ${failCount}`);
  }
  console.log(`  Log saved: ${SUBMISSIONS_LOG_PATH}`);
  console.log(`  No individual secret values were logged`);
  console.log("");
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
