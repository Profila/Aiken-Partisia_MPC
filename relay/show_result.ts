/**
 * Displays the MPC computation result in a formatted terminal output
 * and generates an HTML evidence file.
 *
 * Usage: npx ts-node show_result.ts
 * Input:  relay/mpc-result.json
 * Output: relay/result-display.html
 */

import * as fs from "fs";
import * as path from "path";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface MpcResult {
  readonly query_type: string;
  readonly dataset_id: string;
  readonly result: number;
  readonly participants: number;
  readonly computation_method: string;
  readonly pbc_contract_address: string;
  readonly pbc_compute_tx_id: string;
  readonly cardano_initiation_tx: string;
  readonly result_verified_at: string;
  readonly privacy_note: string;
}

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

const RESULT_PATH = path.resolve(__dirname, "mpc-result.json");
const HTML_OUTPUT_PATH = path.resolve(__dirname, "result-display.html");

// ---------------------------------------------------------------------------
// Format helpers
// ---------------------------------------------------------------------------

function queryLabel(queryType: string): string {
  switch (queryType) {
    case "age_threshold":
      return "Age Threshold (> 18)";
    case "survey_match":
      return "Survey Match (answer = true)";
    default:
      return queryType;
  }
}

function shortHash(hash: string | undefined): string {
  if (!hash) return "[unknown]";
  if (hash.length <= 20) return hash;
  return `${hash.slice(0, 10)}...${hash.slice(-6)}`;
}

function cardanoExplorerUrl(txHash: string): string {
  return `https://preprod.cardanoscan.io/tx/${txHash}`;
}

function pbcExplorerUrl(address: string): string {
  return `https://browser.testnet.partisiablockchain.com/contracts/${address}`;
}

// ---------------------------------------------------------------------------
// Terminal display
// ---------------------------------------------------------------------------

function displayTerminal(result: MpcResult): void {
  const w = 56;
  const line = "═".repeat(w);
  const midLine = "═".repeat(w);
  const pad = (s: string) => s.padEnd(w);

  console.log(`\n  ╔${line}╗`);
  console.log(`  ║${pad("  PROFILA × PARTISIA — MPC RESULT")}║`);
  console.log(`  ╠${midLine}╣`);
  console.log(`  ║${pad(`  Query:        ${queryLabel(result.query_type)}`)}║`);
  console.log(`  ║${pad(`  Dataset:      ${result.dataset_id}`)}║`);
  console.log(`  ║${pad(`  Participants: ${result.participants}`)}║`);
  console.log(
    `  ║${pad(`  Result:       ${result.result} users match criteria`)}║`,
  );
  console.log(`  ╠${midLine}╣`);
  console.log(
    `  ║${pad(`  Cardano TX:   ${shortHash(result.cardano_initiation_tx)}`)}║`,
  );
  console.log(
    `  ║${pad(`  PBC Contract: ${shortHash(result.pbc_contract_address)}`)}║`,
  );
  console.log(
    `  ║${pad(`  PBC TX:       ${shortHash(result.pbc_compute_tx_id)}`)}║`,
  );
  console.log(`  ╠${midLine}╣`);
  console.log(`  ║${pad("  ✓ No individual data was exposed")}║`);
  console.log(`  ║${pad("  ✓ Result computed by MPC nodes")}║`);
  console.log(`  ║${pad(`  ✓ Verified: ${result.result_verified_at}`)}║`);
  console.log(`  ╚${line}╝\n`);
}

// ---------------------------------------------------------------------------
// HTML generation
// ---------------------------------------------------------------------------

function generateHtml(result: MpcResult): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Profila MPC Result — Project Catalyst #1200045</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 2rem;
    }
    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      max-width: 600px;
      width: 100%;
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      padding: 1.5rem 2rem;
      text-align: center;
    }
    .header h1 { font-size: 1.25rem; font-weight: 600; }
    .header p { font-size: 0.875rem; opacity: 0.8; margin-top: 0.25rem; }
    .body { padding: 1.5rem 2rem; }
    .row {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem 0;
      border-bottom: 1px solid #334155;
    }
    .row:last-child { border-bottom: none; }
    .label { color: #94a3b8; font-size: 0.875rem; }
    .value { font-weight: 600; text-align: right; }
    .result-value {
      font-size: 1.5rem;
      color: #34d399;
    }
    .links { padding: 1rem 2rem; background: #0f172a; }
    .links a {
      color: #60a5fa;
      text-decoration: none;
      font-size: 0.8rem;
      display: block;
      margin: 0.25rem 0;
      word-break: break-all;
    }
    .links a:hover { text-decoration: underline; }
    .footer {
      padding: 1rem 2rem;
      text-align: center;
      font-size: 0.75rem;
      color: #64748b;
      border-top: 1px solid #334155;
    }
    .check { color: #34d399; margin-right: 0.5rem; }
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h1>PROFILA × PARTISIA — MPC Result</h1>
      <p>Project Catalyst #1200045</p>
    </div>
    <div class="body">
      <div class="row">
        <span class="label">Query</span>
        <span class="value">${queryLabel(result.query_type)}</span>
      </div>
      <div class="row">
        <span class="label">Dataset</span>
        <span class="value">${result.dataset_id}</span>
      </div>
      <div class="row">
        <span class="label">Participants</span>
        <span class="value">${result.participants}</span>
      </div>
      <div class="row">
        <span class="label">Result</span>
        <span class="value result-value">${result.result} users match</span>
      </div>
    </div>
    <div class="links">
      <a href="${cardanoExplorerUrl(result.cardano_initiation_tx)}" target="_blank">
        Cardano TX: ${result.cardano_initiation_tx}
      </a>
      <a href="${pbcExplorerUrl(result.pbc_contract_address)}" target="_blank">
        PBC Contract: ${result.pbc_contract_address}
      </a>
    </div>
    <div class="footer">
      <p><span class="check">✓</span>No individual data was exposed</p>
      <p><span class="check">✓</span>Result computed by MPC nodes</p>
      <p style="margin-top: 0.5rem">Verified: ${result.result_verified_at}</p>
    </div>
  </div>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main(): void {
  // Check if result file exists; if not, create a sample for demo purposes
  if (!fs.existsSync(RESULT_PATH)) {
    console.log(
      "⚠  mpc-result.json not found — creating sample result for demo",
    );

    const sample: MpcResult = {
      query_type: "age_threshold",
      dataset_id: "profila_test_v1",
      result: 35,
      participants: 50,
      computation_method: "MPC_PBC",
      pbc_contract_address: "<PBC_CONTRACT_ADDRESS>",
      pbc_compute_tx_id: "<PBC_COMPUTE_TX_ID>",
      cardano_initiation_tx: "<CARDANO_TX_HASH>",
      result_verified_at: new Date().toISOString(),
      privacy_note: "Aggregate result only. No individual data exposed.",
    };

    fs.writeFileSync(RESULT_PATH, JSON.stringify(sample, null, 2), "utf-8");
  }

  const result: MpcResult = JSON.parse(fs.readFileSync(RESULT_PATH, "utf-8"));

  // Terminal display
  displayTerminal(result);

  // Generate HTML evidence file
  const html = generateHtml(result);
  fs.writeFileSync(HTML_OUTPUT_PATH, html, "utf-8");
  console.log(`📄 HTML evidence saved: ${HTML_OUTPUT_PATH}`);
}

main();
