#!/usr/bin/env python3
"""Generate Milestone 2 Report PDF."""

import sys, unittest.mock
for mod in ['cryptography', 'cryptography.hazmat', 'cryptography.hazmat.primitives',
            'cryptography.hazmat.primitives.serialization',
            'cryptography.hazmat.primitives.serialization.pkcs12',
            'cryptography.hazmat.primitives._serialization',
            'cryptography.hazmat.primitives.hashes',
            'cryptography.hazmat.bindings', 'cryptography.hazmat.bindings._rust']:
    sys.modules[mod] = unittest.mock.MagicMock()

from fpdf import FPDF
import os

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 7, "Milestone 2 - Proof of Achievement | Catalyst #1200045", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title)
        self.ln(10)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 8, title)
        self.ln(8)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(3)

    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def hr(self):
        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(6)

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, align=None):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(40, 40, 40)
        if align is None:
            align = ["L"] * len(cols)
        for i, col in enumerate(cols):
            a = align[i] if i < len(align) else "L"
            self.cell(widths[i], 6.5, col, border=1, align=a)
        self.ln()


pdf = ReportPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Title
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 14, "Milestone 2", align="C")
pdf.ln(8)
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "Proof of Achievement Report", align="C")
pdf.ln(10)

pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Project Catalyst #1200045: MPC as a Layer 2 Service to Cardano", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Date: 2026-03-01", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Network: Partisia Blockchain Testnet + Cardano Preprod", align="C")
pdf.ln(10)
pdf.hr()

# 1. Executive Summary
pdf.section_title("1. Executive Summary")
pdf.body_text(
    "Milestone 2 delivers the Partisia Blockchain MPC smart contract, the ZK computation kernel, "
    "and the off-chain relay that bridges Cardano Layer 1 to Partisia Layer 2. The contract is "
    "deployed to Partisia Blockchain testnet and the relay successfully detects Cardano MpcRequest "
    "UTxOs and bridges them to the PBC contract."
)
pdf.bold_text("All 6 acceptance criteria are met.")
pdf.hr()

# 2. Acceptance Criteria
pdf.section_title("2. Acceptance Criteria - Evidence Matrix")
w = [8, 62, 14, 86]
pdf.table_header(["#", "Criterion", "Status", "Evidence"], w)
rows = [
    ["1", "PBC unit tests pass", "PASS", "Section 4 - 11/11 tests pass"],
    ["2", "Contract executes MPC", "PASS", "Section 3 - ZK contract + compute kernel"],
    ["3", "PDF documentation", "PASS", "This document"],
    ["4", "Test results in docs", "PASS", "Section 4 + test-results-m2.txt"],
    ["5", "YouTube video of demo", "PASS", "youtu.be/lC_2EG6gxX0"],
    ["6", "Testnet execution on-chain", "PASS", "Section 5 - PBC Testnet Browser"],
]
for r in rows:
    pdf.table_row(r, w, ["C", "L", "C", "L"])
pdf.ln(4)
pdf.hr()

# 3. Smart Contract - Technical Summary
pdf.section_title("3. Smart Contract - Technical Summary")
pdf.sub_title("3.1 Contract Details")
w2 = [50, 120]
details = [
    ["Language", "Rust (PBC SDK v.16.126.0)"],
    ["ZK Compiler", "v6.35.0"],
    ["Contract Address", "039ed9214602f2a93eb05411f852fa78a476607634"],
    ["Source File", "partisia/contracts/profila_mpc/src/contract.rs"],
    ["ZK Compute", "partisia/contracts/profila_mpc/src/zk_compute.rs"],
    ["Test File", "partisia/tests/test-results-m2.txt"],
]
pdf.table_header(["Property", "Value"], w2)
for r in details:
    pdf.table_row(r, w2)
pdf.ln(4)

pdf.sub_title("3.2 Contract State - ProfilaMpcState")
pdf.body_text("The contract maintains public state with the following fields:")
w3 = [40, 30, 100]
pdf.table_header(["Field", "Type", "Purpose"], w3)
state_rows = [
    ["administrator", "Address", "Who deployed/administrates the contract"],
    ["dataset_id", "Vec<u8>", "Identifies the Profila dataset being queried"],
    ["query_type", "String", "\"age_threshold\" or \"survey_match\""],
    ["min_participants", "u32", "Minimum secrets required before computation"],
    ["result", "Option<i64>", "Aggregate result after MPC completes"],
    ["computation_complete", "bool", "Whether computation has finished"],
]
for r in state_rows:
    pdf.table_row(r, w3)
pdf.ln(4)

pdf.sub_title("3.3 Entry Points")
w4 = [55, 25, 90]
pdf.table_header(["Function", "Shortname", "Description"], w4)
entry_rows = [
    ["initialize()", "init", "Deploy contract with dataset parameters"],
    ["submit_secret_value()", "0x40", "User submits secret (age or survey answer)"],
    ["on_variable_inputted()", "0x41", "Callback when secret confirmed on-chain"],
    ["start_computation()", "0x01", "Admin triggers MPC computation"],
    ["on_compute_complete()", "0x42", "Callback when MPC finishes"],
    ["on_variables_opened()", "-", "Reads declassified aggregate result"],
]
for r in entry_rows:
    pdf.table_row(r, w4)
pdf.ln(4)

pdf.sub_title("3.4 ZK Computation Kernel")
pdf.body_text(
    "Two computation functions run securely across 4 MPC nodes - no single node ever sees "
    "an individual user's value:"
)
pdf.body_text("- compute_aggregate (0x61): Counts secret values > 18 (age_threshold query)")
pdf.body_text("- compute_survey_sum (0x62): Sums secret values directly (survey_match query)")
pdf.hr()

# 4. Unit Tests
pdf.section_title("4. Unit Tests - Results")
pdf.bold_text("Command: cd partisia/contracts && cargo test")
pdf.bold_text("Result: 11/11 PASSED")
pdf.ln(2)

w5 = [8, 82, 14, 66]
pdf.table_header(["#", "Test Name", "Result", "Category"], w5)
tests = [
    ["1", "test_init_contract_valid_query_types", "ok", "Initialisation validation"],
    ["2", "test_init_contract_rejects_invalid_query_types", "ok", "Initialisation validation"],
    ["3", "test_init_contract_min_participants_validation", "ok", "Initialisation validation"],
    ["4", "test_compute_age_threshold_result", "ok", "MPC result decoding"],
    ["5", "test_compute_survey_match_result", "ok", "MPC result decoding"],
    ["6", "test_decode_zero_result", "ok", "Edge case"],
    ["7", "test_decode_large_result", "ok", "Edge case"],
    ["8", "test_decode_short_byte_slice", "ok", "Edge case"],
    ["9", "test_decode_empty_slice", "ok", "Edge case"],
    ["10", "test_survey_sum_result_decoding", "ok", "Survey sum decoding"],
    ["11", "test_query_type_dispatch_logic", "ok", "Dispatch branching"],
]
for r in tests:
    pdf.table_row(r, w5, ["C", "L", "C", "L"])
pdf.ln(4)
pdf.hr()

# 5. On-Chain Deployment
pdf.section_title("5. On-Chain Deployment - Evidence")
pdf.sub_title("5.1 PBC Testnet Deployment")
w6 = [50, 120]
pdf.table_header(["Property", "Value"], w6)
deploy_rows = [
    ["Contract Address", "039ed9214602f2a93eb05411f852fa78a476607634"],
    ["Deployment TX", "d1394ee403db29de119d7b6b9ed9214602f2a93eb05411f852fa78a476607634"],
    ["Network", "Partisia Blockchain Testnet"],
    ["Deployed At", "2026-03-06T16:10:32Z"],
    ["Gas Balance", "332,837"],
    ["Storage Size", "82,864 bytes"],
]
for r in deploy_rows:
    pdf.table_row(r, w6)
pdf.ln(4)

pdf.sub_title("5.2 Verification Links")
pdf.body_text("PBC Testnet Browser:")
pdf.body_text("https://browser.testnet.partisiablockchain.com/contracts/039ed9214602f2a93eb05411f852fa78a476607634")
pdf.ln(2)

pdf.sub_title("5.3 Cardano Initiation Evidence")
pdf.body_text(
    "The relay service detected the Cardano MpcRequest UTxO and bridged it to the PBC contract. "
    "This demonstrates the cross-chain initiation from Cardano to Partisia:"
)
pdf.set_font("Courier", "", 8)
pdf.multi_cell(0, 5,
    '{\n'
    '  "cardano_tx": "50d28fd2bd263a84...418d53a57",\n'
    '  "dataset_id": "profila_test_v1",\n'
    '  "query_type": "age_threshold",\n'
    '  "pbc_contract_address": "039ed9214602f2a9...76607634",\n'
    '  "relayed_at": "2026-03-01T22:53:16.322Z"\n'
    '}'
)
pdf.ln(2)
pdf.set_font("Helvetica", "", 10)
pdf.body_text(
    "Note: This is the first known integration between Cardano and Partisia Blockchain. "
    "No existing bridges/integrations exist between these chains for MPC, as confirmed by "
    "the Partisia tech team. This has been accomplished with Ethereum to an extent, hence "
    "our concept project proposal."
)
pdf.hr()

# 6. Architecture
pdf.section_title("6. Cross-Chain Architecture")
pdf.set_font("Courier", "", 9)
pdf.multi_cell(0, 5,
    "Cardano Preprod            Off-Chain Relay           PBC Testnet\n"
    "+----------------+        +----------------+       +----------------+\n"
    "| Aiken SC       | Bfrost | relay.ts       | REST  | ZK Contract    |\n"
    "| MpcRequest     |------->| poll UTxOs     |------>| profila_mpc    |\n"
    "| inline datum   | API    | parse datum    | API   | .zkwa + .abi   |\n"
    "| TX: 50d28f..   |        | relay-log      |       | 039ed921..     |\n"
    "+----------------+        +----------------+       +----------------+\n"
    "     ON-CHAIN                   TESTED                 DEPLOYED"
)
pdf.ln(4)
pdf.set_font("Helvetica", "", 10)
pdf.hr()

# 7. Repository
pdf.section_title("7. Repository")
pdf.body_text("GitHub: https://github.com/Profila/Aiken-Partisia_MPC")
pdf.body_text("Contract source: partisia/contracts/profila_mpc/src/contract.rs")
pdf.body_text("ZK compute: partisia/contracts/profila_mpc/src/zk_compute.rs")
pdf.body_text("Test results: partisia/tests/test-results-m2.txt")
pdf.body_text("Relay service: relay/relay.ts")
pdf.body_text("Relay log: relay/relay-log.json")
pdf.body_text("Deployment evidence: partisia/deploy/deploy-m3.json")
pdf.hr()

# 8. SDK Versions
pdf.section_title("8. SDK & Toolchain Versions")
w7 = [60, 110]
pdf.table_header(["Tool", "Version"], w7)
sdk_rows = [
    ["cargo-partisia-contract", "5.513.0"],
    ["PBC SDK", "v.16.126.0 (binder 11.9.0)"],
    ["ZK Compiler", "6.35.0 (Maven JAR)"],
    ["Rust", "1.86.0"],
    ["Java", "OpenJDK 17.0.18"],
    ["wasm32-unknown-unknown", "installed via rustup"],
]
for r in sdk_rows:
    pdf.table_row(r, w7)
pdf.ln(4)
pdf.hr()

# 9. Video Demo
pdf.section_title("9. Video Demo")
pdf.body_text("M2 Demo: https://youtu.be/lC_2EG6gxX0")
pdf.body_text("Combined M1-M4 Demo: https://youtu.be/jwwfdTSUS2w")
pdf.ln(6)

# Footer
pdf.hr()
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Project Catalyst Fund 13 - Proposal #1200045", align="C")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence", "milestone-2-report.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
