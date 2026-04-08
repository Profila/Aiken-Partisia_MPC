#!/usr/bin/env python3
"""Generate Milestone 1 Report PDF from markdown content."""

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
        self.cell(0, 7, "Milestone 1 - Proof of Achievement | Catalyst #1200045", align="C")
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

# ── Title ──
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 14, "Milestone 1", align="C")
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
pdf.ln(10)
pdf.hr()

# ── 1. Executive Summary ──
pdf.section_title("1. Executive Summary")
pdf.body_text(
    "Milestone 1 delivers a fully functional Aiken smart contract deployed to Cardano preprod testnet. "
    "The contract creates an on-chain MPC initiation record that the off-chain relay (Milestone 2) "
    "monitors to bridge Cardano requests to Partisia Blockchain's MPC infrastructure."
)
pdf.bold_text("All 6 acceptance criteria are met.")
pdf.hr()

# ── 2. Acceptance Criteria ──
pdf.section_title("2. Acceptance Criteria - Evidence Matrix")
w = [8, 62, 14, 86]
pdf.table_header(["#", "Criterion", "Status", "Evidence"], w)
rows = [
    ["1", "Aiken unit tests pass", "PASS", "Section 4 - 6/6 tests pass"],
    ["2", "Contract has MPC initiation", "PASS", "Section 3 - validator source"],
    ["3", "PDF documentation", "PASS", "This document"],
    ["4", "Test results in docs", "PASS", "Section 4 + test-results-m1.txt"],
    ["5", "YouTube video of demo", "PASS", "youtu.be/QRj4tAt23Aw"],
    ["6", "Testnet execution on-chain", "PASS", "Section 5 - TX on CardanoScan"],
]
for r in rows:
    pdf.table_row(r, w, ["C", "L", "C", "L"])
pdf.ln(4)
pdf.hr()

# ── 3. Smart Contract ──
pdf.section_title("3. Smart Contract - Technical Summary")
pdf.sub_title("3.1 Contract Details")
w2 = [50, 120]
details = [
    ["Language", "Aiken v1.1.21"],
    ["Plutus Version", "v3"],
    ["Validator Hash", "b8bd6946bb4f9ac805f242d86fea090191e64e1250aa8f2d54fc8c67"],
    ["Script Address", "addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz"],
    ["Source File", "cardano/validators/profila_mpc.ak"],
    ["Test File", "cardano/validators/profila_mpc_tests.ak"],
]
pdf.table_header(["Property", "Value"], w2)
for r in details:
    pdf.table_row(r, w2)
pdf.ln(4)

pdf.sub_title("3.2 Datum Type - MpcRequest")
pdf.body_text("The contract uses an inline datum to record MPC initiation requests:")
w3 = [38, 42, 90]
pdf.table_header(["Field", "Type", "Purpose"], w3)
datum_rows = [
    ["dataset_id", "ByteArray", "Identifies the Profila dataset to query"],
    ["query_type", "ByteArray", "\"age_threshold\" or \"survey_match\""],
    ["initiator_pkh", "VerificationKeyHash", "Public key hash of the requester"],
    ["partisia_contract", "ByteArray", "Target PBC contract address"],
    ["timestamp", "Int", "POSIX timestamp in milliseconds"],
]
for r in datum_rows:
    pdf.table_row(r, w3)
pdf.ln(4)

pdf.sub_title("3.3 Validation Rules")
pdf.body_text("The InitiateMPC redeemer enforces 4 validation checks:")
rules = [
    "1. Initiator must sign - initiator_pkh must be in tx.extra_signatories",
    "2. Dataset must exist - dataset_id must not be empty",
    "3. Valid query type - must be \"age_threshold\" or \"survey_match\"",
    "4. Positive timestamp - must be greater than 0",
]
for rule in rules:
    pdf.body_text(rule)
pdf.body_text(
    "Each check uses Aiken's trace operator (?) so failures are logged with "
    "the specific condition that failed (e.g., \"initiator_signed ? False\")."
)
pdf.hr()

# ── 4. Unit Tests ──
pdf.section_title("4. Unit Tests - Results")
pdf.bold_text("Command: cd cardano && aiken check")
pdf.bold_text("Result: 6/6 PASSED")
pdf.ln(2)

w4 = [8, 58, 40, 14, 25, 25]
pdf.table_header(["#", "Test Name", "Expected", "Result", "Mem", "CPU"], w4)
tests = [
    ["1", "test_initiate_mpc_valid", "pass", "PASS", "37,784", "12,233,900"],
    ["2", "test_initiate_mpc_empty_dataset", "fail (empty dataset)", "PASS", "32,854", "10,561,421"],
    ["3", "test_initiate_mpc_wrong_signer", "fail (PKH mismatch)", "PASS", "33,578", "10,818,873"],
    ["4", "test_initiate_mpc_bad_query", "fail (bad query_type)", "PASS", "39,875", "12,829,921"],
    ["5", "test_initiate_mpc_bad_timestamp", "fail (timestamp=0)", "PASS", "43,796", "14,301,528"],
    ["6", "test_valid_query_types", "pass (utility fn)", "PASS", "7,811", "1,826,212"],
]
for r in tests:
    pdf.table_row(r, w4, ["C", "L", "L", "C", "R", "R"])
pdf.ln(4)

pdf.sub_title("Test Trace Output (failure cases)")
traces = [
    "Test 2: dataset_not_empty ? False",
    "Test 3: initiator_signed ? False",
    "Test 4: valid_query_type ? False",
    "Test 5: timestamp_positive ? False",
]
for t in traces:
    pdf.body_text(t)
pdf.body_text("These traces confirm each validation rule independently rejects invalid inputs.")
pdf.hr()

# ── 5. On-Chain Deployment ──
pdf.section_title("5. On-Chain Deployment - Evidence")
pdf.sub_title("5.1 Transaction Details")
w5 = [50, 120]
pdf.table_header(["Property", "Value"], w5)
tx_rows = [
    ["TX Hash", "50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57"],
    ["Block Height", "4,468,996"],
    ["Slot", "116,719,755"],
    ["Network", "Cardano Preprod"],
    ["Fee", "169,505 lovelace (0.169505 tADA)"],
    ["Valid Contract", "true"],
]
for r in tx_rows:
    pdf.table_row(r, w5)
pdf.ln(4)

pdf.sub_title("5.2 Verification Links")
pdf.body_text("CardanoScan TX:")
pdf.body_text("https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57")
pdf.body_text("Script Address:")
pdf.body_text("https://preprod.cardanoscan.io/address/addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz")
pdf.ln(2)

pdf.sub_title("5.3 UTxO at Script Address")
pdf.body_text("The transaction created a UTxO at the script address with:")
pdf.body_text("Amount: 2,000,000 lovelace (2 tADA)")
pdf.body_text("Inline Datum (CBOR):")
pdf.set_font("Courier", "", 8)
pdf.set_text_color(40, 40, 40)
pdf.multi_cell(0, 5, "d8799f4f70726f66696c615f746573745f76314d6167655f7468726573686f6c64581cfc1c993261d3d3104bcdbf3f54d16c134f634360e9b40a23289432244\n01b0000019cab7101a2ff")
pdf.ln(4)

pdf.sub_title("5.4 Decoded Inline Datum")
w6 = [35, 55, 80]
pdf.table_header(["Field", "Decoded Value", "Notes"], w6)
decoded = [
    ["dataset_id", "profila_test_v1", ""],
    ["query_type", "age_threshold", ""],
    ["initiator_pkh", "fc1c993261d3d3...28943224", "(28-byte key hash)"],
    ["partisia_contract", "(empty)", "(to be filled in M2)"],
    ["timestamp", "2026-03-01T22:07:15Z", "POSIX ms"],
]
for r in decoded:
    pdf.table_row(r, w6)
pdf.ln(4)

pdf.sub_title("5.5 Independent Verification")
pdf.body_text("Anyone can verify this deployment via Blockfrost API:")
pdf.set_font("Courier", "", 8)
pdf.multi_cell(0, 5,
    'curl -H "project_id: <YOUR_KEY>" \\\n'
    '  "https://cardano-preprod.blockfrost.io/api/v0/txs/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57/utxos"'
)
pdf.ln(2)
pdf.set_font("Helvetica", "", 10)
pdf.body_text("Or via CardanoScan (no API key needed) using the links in Section 5.2.")
pdf.hr()

# ── 6. Repository ──
pdf.section_title("6. Repository")
pdf.body_text("GitHub: https://github.com/Profila/Aiken-Partisia_MPC")
pdf.body_text("Contract source: cardano/validators/profila_mpc.ak")
pdf.body_text("Test source: cardano/validators/profila_mpc_tests.ak")
pdf.body_text("Deploy script: cardano/scripts/deploy-m1.ts")
pdf.body_text("Test results: cardano/tests/test-results-m1.txt")
pdf.hr()

# ── 7. How This Enables M2-M4 ──
pdf.section_title("7. How This Enables Milestones 2-4")
pdf.body_text(
    "The deployed UTxO at the script address serves as the on-chain trigger for the entire MPC pipeline:"
)
pdf.ln(2)
pdf.set_font("Courier", "", 9)
pdf.multi_cell(0, 5,
    "M1 (this milestone)       M2 (next)                M3 + M4\n"
    "UTxO with MpcRequest  ->  relay.ts detects it  ->  Secrets submitted to PBC\n"
    "inline datum              calls PBC REST API       MPC computation runs\n"
    "                                                   Result displayed"
)
pdf.ln(4)
pdf.set_font("Helvetica", "", 10)
pdf.body_text(
    "The relay script (Milestone 2) polls this address via Blockfrost. When it finds a UTxO with a "
    "valid MpcRequest datum, it bridges the request to the Partisia Blockchain contract - triggering "
    "the privacy-preserving computation."
)
pdf.hr()

# ── 8. Video Demo ──
pdf.section_title("8. Video Demo")
pdf.body_text("M1 Demo: https://youtu.be/QRj4tAt23Aw")
pdf.body_text("Combined M1-M4 Demo: https://youtu.be/jwwfdTSUS2w")
pdf.ln(6)

# ── Footer ──
pdf.hr()
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Project Catalyst Fund 13 - Proposal #1200045", align="C")

# Output
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence", "milestone-1-report.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
