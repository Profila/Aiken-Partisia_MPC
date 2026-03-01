/**
 * Generate synthetic test dataset for Profila MPC demonstrations.
 *
 * Creates 50 test users with realistic distribution:
 * - 35 over 18 (70%), 15 under/equal 18 (30%)
 * - 28 survey_q1_answer = true (56%), 22 false (44%)
 * - Mixed country codes: CH, DE, GB, US, FR, AU
 *
 * Usage: npx ts-node generate_test_data.ts
 * Output: ../test-data/profila_test_users.json
 */

import * as fs from "fs";
import * as path from "path";
import * as crypto from "crypto";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const TOTAL_USERS = 50;
const OVER_18_COUNT = 35;
const SURVEY_TRUE_COUNT = 28;
const COUNTRY_CODES = ["CH", "DE", "GB", "US", "FR", "AU"] as const;
const OUTPUT_PATH = path.resolve(
  __dirname,
  "../test-data/profila_test_users.json",
);

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TestUser {
  readonly user_id_hash: string;
  readonly age: number;
  readonly survey_q1_answer: boolean;
  readonly country_code: string;
  readonly profila_consent: true;
}

interface TestDataset {
  readonly metadata: {
    readonly dataset_id: string;
    readonly record_count: number;
    readonly mpc_secret_fields: readonly string[];
    readonly created: string;
    readonly note: string;
    readonly expected_results: {
      readonly age_threshold_gt_18: number;
      readonly survey_match_true: number;
    };
  };
  readonly users: readonly TestUser[];
}

// ---------------------------------------------------------------------------
// Deterministic pseudo-random (seeded for reproducibility)
// ---------------------------------------------------------------------------

function hashUserId(index: number): string {
  return crypto
    .createHash("sha256")
    .update(`test_user_${String(index + 1).padStart(3, "0")}`)
    .digest("hex");
}

function pickAge(isOver18: boolean, index: number): number {
  // Spread ages realistically
  if (isOver18) {
    // Ages 19-75, distributed
    const ages = [
      19, 22, 25, 28, 30, 32, 34, 37, 40, 43, 45, 48, 50, 55, 60, 65, 70, 75,
    ];
    return ages[index % ages.length];
  }
  // Ages 14-18
  const youngAges = [14, 15, 16, 17, 18];
  return youngAges[index % youngAges.length];
}

// ---------------------------------------------------------------------------
// Generate users
// ---------------------------------------------------------------------------

function generateUsers(): readonly TestUser[] {
  const users: TestUser[] = [];

  // Create flags for age and survey distribution
  const isOver18: boolean[] = Array(TOTAL_USERS).fill(false);
  for (let i = 0; i < OVER_18_COUNT; i++) isOver18[i] = true;

  const isSurveyTrue: boolean[] = Array(TOTAL_USERS).fill(false);
  for (let i = 0; i < SURVEY_TRUE_COUNT; i++) isSurveyTrue[i] = true;

  // Interleave for realistic distribution (not all young first)
  // Use a deterministic shuffle based on index
  const shuffledOver18 = [...isOver18].sort(
    (_, __, i = Math.floor(isOver18.length * 0.7)) => (i % 3) - 1,
  );

  let over18Index = 0;
  let under18Index = 0;

  for (let i = 0; i < TOTAL_USERS; i++) {
    const over18 = isOver18[i];
    const age = pickAge(over18, over18 ? over18Index++ : under18Index++);

    users.push({
      user_id_hash: hashUserId(i),
      age,
      survey_q1_answer: isSurveyTrue[i],
      country_code: COUNTRY_CODES[i % COUNTRY_CODES.length],
      profila_consent: true,
    });
  }

  return users;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main(): void {
  const users = generateUsers();

  const dataset: TestDataset = {
    metadata: {
      dataset_id: "profila_test_v1",
      record_count: TOTAL_USERS,
      mpc_secret_fields: ["age", "survey_q1_answer"],
      created: new Date().toISOString(),
      note: "Synthetic data only — generated for MPC demonstration. No real PII.",
      expected_results: {
        age_threshold_gt_18: users.filter((u) => u.age > 18).length,
        survey_match_true: users.filter((u) => u.survey_q1_answer).length,
      },
    },
    users,
  };

  // Ensure output directory exists
  const dir = path.dirname(OUTPUT_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(dataset, null, 2), "utf-8");

  console.log("✅ Generated test dataset:");
  console.log(`   File: ${OUTPUT_PATH}`);
  console.log(`   Users: ${dataset.metadata.record_count}`);
  console.log(
    `   Expected age_threshold (>18): ${dataset.metadata.expected_results.age_threshold_gt_18}`,
  );
  console.log(
    `   Expected survey_match (true): ${dataset.metadata.expected_results.survey_match_true}`,
  );
  // NOTE: This is synthetic demo data — safe to preview.
  // In production, NEVER log actual user secret fields.
  console.log("\n   First 5 records (synthetic — safe to display):");
  for (const u of users.slice(0, 5)) {
    console.log(
      `     ${u.user_id_hash.slice(0, 12)}… country=${u.country_code} [secret fields omitted]`,
    );
  }
}

main();
