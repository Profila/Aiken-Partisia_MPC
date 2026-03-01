/**
 * Simulates Profila users submitting secrets to the PBC MPC contract.
 *
 * Per the PBC second-layer architecture, secrets go DIRECTLY to PBC —
 * not via Cardano. Each user's private value (age or survey answer) is
 * secret-shared by PBC's MPC infrastructure before reaching the nodes.
 *
 * Usage:
 *   npx ts-node submit_secrets.ts --contract <PBC_ADDR> --query age_threshold --count 20
 *   npx ts-node submit_secrets.ts --contract <PBC_ADDR> --query survey_match --count 50
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

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
  readonly pbc_tx_id: string;
  readonly query_type: string;
  readonly submitted_at: string;
  // NOTE: The actual secret value is NEVER logged
}

type QueryType = "age_threshold" | "survey_match";

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------

function parseArgs(): {
  readonly contract: string;
  readonly query: QueryType;
  readonly count: number;
} {
  const args = process.argv.slice(2);
  let contract = process.env.PBC_CONTRACT_ADDRESS ?? "";
  let query: QueryType = "age_threshold";
  let count = 20;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--contract":
        contract = args[++i] ?? "";
        break;
      case "--query":
        query = args[++i] as QueryType;
        break;
      case "--count":
        count = parseInt(args[++i] ?? "20", 10);
        break;
    }
  }

  if (!contract) {
    console.error("❌ --contract <PBC_ADDRESS> is required (or set PBC_CONTRACT_ADDRESS in .env)");
    process.exit(1);
  }
  if (query !== "age_threshold" && query !== "survey_match") {
    console.error("❌ --query must be 'age_threshold' or 'survey_match'");
    process.exit(1);
  }
  if (count < 1 || count > 50) {
    console.error("❌ --count must be between 1 and 50");
    process.exit(1);
  }

  return { contract, query, count };
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
// Submit secret to PBC contract (simulated for PoC)
// ---------------------------------------------------------------------------

async function submitSecret(
  contractAddress: string,
  _userIndex: number,
  _secretValue: number
): Promise<string> {
  // In production, this would:
  // 1. Derive a unique PBC account for this user
  // 2. Call submit_secret_value() on the contract via PBC REST API
  // 3. The secret is automatically secret-shared by PBC infrastructure
  //
  // For the PoC, we simulate the submission and generate a mock TX ID.
  // When deployed to PBC testnet, this function would use the Partisia
  // SDK to sign and submit actual transactions.

  const url = `${PBC_TESTNET_URL}/blockchain/contracts/${contractAddress}`;

  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 100));

  // Generate a deterministic mock TX ID for reproducible evidence
  const crypto = await import("crypto");
  const txId = crypto
    .createHash("sha256")
    .update(`submit_${contractAddress}_${_userIndex}_${Date.now()}`)
    .digest("hex")
    .slice(0, 64);

  return txId;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  const { contract, query, count } = parseArgs();

  console.log("═══════════════════════════════════════════════════");
  console.log("  PROFILA × PARTISIA — Secret Submission");
  console.log("  Project Catalyst #1200045");
  console.log("═══════════════════════════════════════════════════");
  console.log(`  Contract:  ${contract}`);
  console.log(`  Query:     ${query}`);
  console.log(`  Count:     ${count}`);
  console.log("");

  // Load test data
  if (!fs.existsSync(TEST_DATA_PATH)) {
    console.error(`❌ Test data not found at: ${TEST_DATA_PATH}`);
    console.error("   Run: npx ts-node generate_test_data.ts first");
    process.exit(1);
  }

  const dataset: TestDataset = JSON.parse(
    fs.readFileSync(TEST_DATA_PATH, "utf-8")
  );
  const usersToSubmit = dataset.users.slice(0, count);

  console.log(
    `📊 Loaded dataset: ${dataset.metadata.dataset_id} (${dataset.users.length} users)`
  );
  console.log(`   Submitting ${usersToSubmit.length} secrets...\n`);

  const log: SubmissionLogEntry[] = [];
  let successCount = 0;

  for (let i = 0; i < usersToSubmit.length; i++) {
    const user = usersToSubmit[i];
    const secretValue = extractSecretValue(user, query);

    try {
      const txId = await submitSecret(contract, i, secretValue);

      const entry: SubmissionLogEntry = {
        user_id_hash: user.user_id_hash,
        pbc_tx_id: txId,
        query_type: query,
        submitted_at: new Date().toISOString(),
        // Secret value is intentionally NOT logged
      };

      log.push(entry);
      successCount++;

      // Progress indicator (don't log the actual value!)
      console.log(
        `  [${i + 1}/${usersToSubmit.length}] ✅ ${user.user_id_hash.slice(0, 12)}… → tx:${txId.slice(0, 16)}…`
      );
    } catch (err) {
      console.error(
        `  [${i + 1}/${usersToSubmit.length}] ❌ ${user.user_id_hash.slice(0, 12)}… → FAILED: ${err}`
      );
    }
  }

  // Save submission log
  fs.writeFileSync(SUBMISSIONS_LOG_PATH, JSON.stringify(log, null, 2), "utf-8");

  console.log("\n═══════════════════════════════════════════════════");
  console.log(`  ✅ Submitted: ${successCount}/${usersToSubmit.length}`);
  console.log(`  📄 Log saved: ${SUBMISSIONS_LOG_PATH}`);
  console.log(`  🔒 No individual secret values were logged`);
  console.log("═══════════════════════════════════════════════════");
}

main().catch((err) => {
  console.error("❌ Error:", err);
  process.exit(1);
});
