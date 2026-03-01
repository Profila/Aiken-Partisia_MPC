/**
 * Deploy the Profila MPC Aiken contract to Cardano preprod.
 *
 * This script:
 *   1. Generates a deploy key pair (or loads existing)
 *   2. Reads the compiled plutus.json
 *   3. Derives the script address
 *   4. Builds a TX sending 2 tADA to the script address with inline datum
 *   5. Signs and submits via Blockfrost
 *
 * Usage:
 *   cd cardano/scripts
 *   npm install
 *   npx tsx deploy-m1.ts
 *
 * First run: generates keys, shows address to fund from Lace.
 * Second run (after funding): deploys the contract.
 */

import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

import {
  Blockfrost,
  Constr,
  Data,
  fromText,
  generatePrivateKey,
  getAddressDetails,
  Lucid,
  paymentCredentialOf,
  type SpendingValidator,
  validatorToAddress,
} from "@lucid-evolution/lucid";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

dotenv.config({ path: path.resolve(import.meta.dirname, "../../.env") });

const BLOCKFROST_URL = "https://cardano-preprod.blockfrost.io/api/v0";
const BLOCKFROST_PROJECT_ID = process.env.BLOCKFROST_PROJECT_ID ?? "";
const NETWORK = "Preprod" as const;

const KEY_DIR = path.resolve(import.meta.dirname, "../keys");
const KEY_FILE = path.join(KEY_DIR, "deploy.sk");
const PLUTUS_JSON_PATH = path.resolve(import.meta.dirname, "../plutus.json");
const DEPLOY_OUTPUT_PATH = path.resolve(import.meta.dirname, "deploy-m1.json");

// MpcRequest datum values
const DATASET_ID = "profila_test_v1";
const QUERY_TYPE = "age_threshold";
const LOCK_AMOUNT = 2_000_000n; // 2 tADA in lovelace

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface PlutusBlueprint {
  readonly preamble: {
    readonly title: string;
    readonly plutusVersion: string;
  };
  readonly validators: readonly {
    readonly title: string;
    readonly compiledCode: string;
    readonly hash: string;
  }[];
}

interface DeployOutput {
  readonly script_address: string;
  readonly tx_hash: string;
  readonly validator_hash: string;
  readonly datum: {
    readonly dataset_id: string;
    readonly query_type: string;
    readonly initiator_pkh: string;
    readonly partisia_contract: string;
    readonly timestamp: number;
  };
  readonly deployed_at: string;
  readonly network: string;
  readonly cardanoscan_url: string;
}

// ---------------------------------------------------------------------------
// Key management
// ---------------------------------------------------------------------------

function loadOrGenerateKey(): {
  readonly key: string;
  readonly isNew: boolean;
} {
  if (!fs.existsSync(KEY_DIR)) {
    fs.mkdirSync(KEY_DIR, { recursive: true });
  }

  if (fs.existsSync(KEY_FILE)) {
    const key = fs.readFileSync(KEY_FILE, "utf-8").trim();
    return { key, isNew: false };
  }

  const key = generatePrivateKey();
  fs.writeFileSync(KEY_FILE, key, "utf-8");
  return { key, isNew: true };
}

// ---------------------------------------------------------------------------
// Load the Aiken validator from plutus.json
// ---------------------------------------------------------------------------

function loadValidator(): {
  readonly validator: SpendingValidator;
  readonly hash: string;
} {
  if (!fs.existsSync(PLUTUS_JSON_PATH)) {
    console.error("❌ plutus.json not found. Run: cd cardano && aiken build");
    process.exit(1);
  }

  const blueprint: PlutusBlueprint = JSON.parse(
    fs.readFileSync(PLUTUS_JSON_PATH, "utf-8"),
  );

  const spendEntry = blueprint.validators.find(
    (v) => v.title === "profila_mpc.profila_mpc.spend",
  );

  if (!spendEntry) {
    console.error("❌ Spend validator not found in plutus.json");
    process.exit(1);
  }

  const validator: SpendingValidator = {
    type: "PlutusV3",
    script: spendEntry.compiledCode,
  };

  return { validator, hash: spendEntry.hash };
}

// ---------------------------------------------------------------------------
// Build the MpcRequest inline datum
// ---------------------------------------------------------------------------

function buildDatum(initiatorPkh: string): {
  readonly serialised: string;
  readonly fields: DeployOutput["datum"];
} {
  const timestamp = Date.now();

  // MpcRequest is Constr(0, [dataset_id, query_type, initiator_pkh,
  //                          partisia_contract, timestamp])
  // All ByteArray fields are hex-encoded.
  const serialised = Data.to(
    new Constr(0, [
      fromText(DATASET_ID),
      fromText(QUERY_TYPE),
      initiatorPkh,
      fromText(""), // partisia_contract — empty until M2 deployment
      BigInt(timestamp),
    ]),
  );

  return {
    serialised,
    fields: {
      dataset_id: DATASET_ID,
      query_type: QUERY_TYPE,
      initiator_pkh: initiatorPkh,
      partisia_contract: "",
      timestamp,
    },
  };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
  console.log("═══════════════════════════════════════════════════");
  console.log("  PROFILA × PARTISIA — M1 Contract Deployment");
  console.log("  Project Catalyst #1200045 | Cardano Preprod");
  console.log("═══════════════════════════════════════════════════\n");

  // -- Validate config --
  if (!BLOCKFROST_PROJECT_ID) {
    console.error("❌ BLOCKFROST_PROJECT_ID not set in .env");
    process.exit(1);
  }

  // -- Load / generate deploy key --
  const { key: privateKey, isNew } = loadOrGenerateKey();
  if (isNew) {
    console.log("🔑 Generated new deploy key → cardano/keys/deploy.sk");
    console.log("   (This file is gitignored — keep it safe)\n");
  } else {
    console.log("🔑 Loaded existing deploy key\n");
  }

  // -- Initialise Lucid with Blockfrost --
  const lucid = await Lucid(
    new Blockfrost(BLOCKFROST_URL, BLOCKFROST_PROJECT_ID),
    NETWORK,
  );

  lucid.selectWallet.fromPrivateKey(privateKey);
  const deployAddress = await lucid.wallet().address();
  console.log(`📬 Deploy address: ${deployAddress}`);

  // -- Check balance --
  const utxos = await lucid.wallet().getUtxos();
  const totalLovelace = utxos.reduce(
    (sum, u) => sum + (u.assets["lovelace"] ?? 0n),
    0n,
  );
  const totalAda = Number(totalLovelace) / 1_000_000;
  console.log(
    `💰 Balance: ${totalAda.toFixed(6)} tADA (${totalLovelace} lovelace)`,
  );

  if (totalLovelace < LOCK_AMOUNT + 500_000n) {
    console.log("\n" + "─".repeat(55));
    console.log("⚠️  Not enough tADA to deploy.");
    console.log("");
    console.log("Please send ~5 tADA from your Lace wallet to:");
    console.log(`  ${deployAddress}`);
    console.log("");
    console.log("Then run this script again.");
    console.log("─".repeat(55));
    process.exit(0);
  }

  // -- Load validator --
  const { validator, hash: validatorHash } = loadValidator();
  const scriptAddress = validatorToAddress(NETWORK, validator);
  console.log(`\n📜 Validator hash: ${validatorHash}`);
  console.log(`📍 Script address: ${scriptAddress}`);

  // -- Build datum --
  const initiatorPkh = paymentCredentialOf(deployAddress).hash;
  console.log(`👤 Initiator PKH:  ${initiatorPkh}`);

  const { serialised: datum, fields: datumFields } = buildDatum(initiatorPkh);

  // -- Build, sign, submit --
  console.log(
    `\n🔨 Building TX: lock ${Number(LOCK_AMOUNT) / 1_000_000} tADA at script with MpcRequest datum...`,
  );

  const tx = await lucid
    .newTx()
    .pay.ToContract(
      scriptAddress,
      { kind: "inline", value: datum },
      { lovelace: LOCK_AMOUNT },
    )
    .complete();

  const signedTx = await tx.sign.withWallet().complete();
  const txHash = await signedTx.submit();

  console.log(`\n✅ Transaction submitted!`);
  console.log(`   TX hash: ${txHash}`);
  console.log(
    `   CardanoScan: https://preprod.cardanoscan.io/transaction/${txHash}`,
  );

  // -- Save deploy output --
  const output: DeployOutput = {
    script_address: scriptAddress,
    tx_hash: txHash,
    validator_hash: validatorHash,
    datum: datumFields,
    deployed_at: new Date().toISOString(),
    network: NETWORK,
    cardanoscan_url: `https://preprod.cardanoscan.io/transaction/${txHash}`,
  };

  fs.writeFileSync(
    DEPLOY_OUTPUT_PATH,
    JSON.stringify(output, null, 2),
    "utf-8",
  );
  console.log(`\n📄 Deploy output saved: ${DEPLOY_OUTPUT_PATH}`);

  // -- Update .env with script address --
  const envPath = path.resolve(import.meta.dirname, "../../.env");
  if (fs.existsSync(envPath)) {
    let envContent = fs.readFileSync(envPath, "utf-8");
    envContent = envContent.replace(
      /^CARDANO_SCRIPT_ADDRESS=.*$/m,
      `CARDANO_SCRIPT_ADDRESS=${scriptAddress}`,
    );
    fs.writeFileSync(envPath, envContent, "utf-8");
    console.log(`\n✏️  Updated .env with CARDANO_SCRIPT_ADDRESS`);
  }

  console.log("\n═══════════════════════════════════════════════════");
  console.log("  M1 Deployment Complete");
  console.log("═══════════════════════════════════════════════════");
  console.log(`  Script address: ${scriptAddress}`);
  console.log(`  TX hash:        ${txHash}`);
  console.log(`  Datum:          ${DATASET_ID} / ${QUERY_TYPE}`);
  console.log(
    `  Verify:         https://preprod.cardanoscan.io/transaction/${txHash}`,
  );
  console.log("═══════════════════════════════════════════════════\n");
}

main().catch((err) => {
  console.error("❌ Deploy error:", err);
  process.exit(1);
});
