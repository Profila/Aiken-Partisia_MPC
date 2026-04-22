#!/usr/bin/env python3
"""Generate Milestone 3 Report PDF."""

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
        self.cell(0, 7, "Milestone 3 - Proof of Achievement | Catalyst #1200045", align="C")
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
pdf.cell(0, 14, "Milestone 3", align="C")
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
pdf.cell(0, 6, "Date: 2026-03-06", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Network: Partisia Blockchain Testnet", align="C")
pdf.ln(10)
pdf.hr()

# 1. Executive Summary
pdf.section_title("1. Executive Summary")
pdf.body_text(
    "Milestone 3 delivers the secret input submission flow for privacy-preserving MPC computation. "
    "A synthetic test dataset of 50 users (representing Profila platform data) is defined, and 5 secret "
    "values are submitted as real on-chain ZK transactions to the Partisia Blockchain testnet contract. "
    "No individual user data is ever exposed - only the aggregate MPC result is visible."
)
pdf.bold_text("All 5 acceptance criteria are met.")
pdf.hr()

# 2. Acceptance Criteria
pdf.section_title("2. Acceptance Criteria - Evidence Matrix")
w = [8, 72, 14, 76]
pdf.table_header(["#", "Criterion", "Status", "Evidence"], w)
rows = [
    ["1", "Dataset defined as data input", "PASS", "Section 3 - Profila test data (50 users)"],
    ["2", "PDF documentation in English", "PASS", "This document"],
    ["3", "Data type/definition + secret sharing", "PASS", "Sections 3-4 - types + submission flow"],
    ["4", "YouTube video of process", "PASS", "youtu.be/psm2lMU7n1o"],
    ["5", "Demo on PBC testnet", "PASS", "Section 5 - 5 on-chain ZK transactions"],
]
for r in rows:
    pdf.table_row(r, w, ["C", "L", "C", "L"])
pdf.ln(4)
pdf.hr()

# 3. Dataset Definition
pdf.section_title("3. Dataset Definition - Profila Test Data")
pdf.sub_title("3.1 Data Source")
pdf.body_text(
    "The dataset consists of 50 synthetic test users representing typical Profila platform data. "
    "This is personal data and demographics which require analysis in a privacy-preserving manner. "
    "The data source is defined as test data from the Profila platform."
)
pdf.body_text("Dataset file: test-data/profila_test_users.json")
pdf.body_text("Dataset ID: profila_test_v1")
pdf.ln(2)

pdf.sub_title("3.2 Data Type Definition")
pdf.body_text("Each user record contains the following fields:")
w3 = [38, 25, 20, 87]
pdf.table_header(["Field", "Type", "Secret?", "Description"], w3)
data_rows = [
    ["user_id_hash", "string", "No", "SHA-256 hash of synthetic user ID"],
    ["age", "number", "YES", "User age (14-75) - MPC secret input"],
    ["survey_q1_answer", "boolean", "YES", "Survey response - MPC secret input"],
    ["country_code", "string", "No", "ISO country code (CH, DE, GB, US, FR, AU)"],
    ["profila_consent", "boolean", "No", "Consent flag (always true for PoC)"],
]
for r in data_rows:
    pdf.table_row(r, w3)
pdf.ln(4)

pdf.sub_title("3.3 MPC Query Types")
w4 = [40, 30, 25, 75]
pdf.table_header(["Query Type", "Secret Field", "PBC Type", "Computation"], w4)
query_rows = [
    ["age_threshold", "age", "Sbi64", "Count where value > 18"],
    ["survey_match", "survey_q1_answer", "Sbi64", "Sum all values (0 or 1)"],
]
for r in query_rows:
    pdf.table_row(r, w4)
pdf.ln(4)

pdf.sub_title("3.4 Dataset Distribution")
pdf.body_text("50 users total:")
pdf.body_text("- 35 users over age 18 (70%), 15 users age 18 or under (30%)")
pdf.body_text("- 28 users with survey_q1_answer = true (56%), 22 false (44%)")
pdf.body_text("- 6 countries: CH, DE, GB, US, FR, AU")
pdf.body_text("- Note: Synthetic data only - no real PII")
pdf.hr()

# 4. Secret Sharing Process
pdf.section_title("4. Secret Sharing Process")
pdf.sub_title("4.1 How Secrets Are Shared into the PBC Contract")
pdf.body_text(
    "The secret submission process uses the official Partisia Blockchain TypeScript SDK. "
    "Each user's private value (age or survey answer) is encrypted and secret-shared by "
    "PBC's ZK MPC infrastructure across 4 MPC nodes. No single node ever sees an individual value."
)
pdf.body_text("Process steps:")
pdf.body_text("1. Load test user record from Profila dataset")
pdf.body_text("2. Extract the secret field (age for age_threshold, survey answer for survey_match)")
pdf.body_text("3. Serialize the secret as Sbi64 (signed 64-bit integer) via BitOutput")
pdf.body_text("4. Encrypt the secret for each MPC engine's public key via RealZkClient")
pdf.body_text("5. Package encrypted shares into a single PBC blockchain transaction")
pdf.body_text("6. Submit the transaction on-chain (submit_secret_value, shortname 0x40)")
pdf.body_text("7. MPC nodes verify and accept the shares asynchronously")
pdf.ln(2)

pdf.sub_title("4.2 Privacy Guarantees")
pdf.body_text("The submission log contains ONLY: user_id_hash, pbc_tx_id, query_type, timestamp.")
pdf.body_text("Zero raw ages or survey answers are ever logged, stored, or transmitted in plaintext.")
pdf.body_text("The contract state shows only aggregate fields - no individual values visible.")
pdf.body_text("The PBC browser Secret Data tab shows computation status only - no individual ZK variables.")
pdf.hr()

# 5. On-Chain Evidence
pdf.section_title("5. On-Chain Evidence - PBC Testnet")
pdf.sub_title("5.1 Secret Input Transactions")
pdf.body_text("5 real on-chain ZK secret-input transactions submitted to PBC testnet:")
w5 = [8, 95, 67]
pdf.table_header(["#", "PBC Transaction Hash", "PBC Sender"], w5)
txs = [
    ["1", "7507fd18ef779c459c7248af32bee6e660f6b4ad...", "0043d3baeb08c94e8402..."],
    ["2", "519859f57ccc1acd44ed73fe80ae2a3c051b15ec...", "0077475a2deceb9c073e..."],
    ["3", "407423fd9996067e8c4b5de9390bdad6c14c1da2...", "0084400b5b22b47c2414..."],
    ["4", "4bfe3b1466c68f8b2e73376b35677ed2592ffd85...", "00d220baae1d73526743..."],
    ["5", "e4c158dda054b2fc9ba17a38a7fb4f8373c4720e...", "00d85675808c74ccfebb..."],
]
for r in txs:
    pdf.table_row(r, w5, ["C", "L", "L"])
pdf.ln(4)

pdf.sub_title("5.2 Verification")
pdf.body_text("PBC Contract on testnet:")
pdf.body_text("https://browser.testnet.partisiablockchain.com/contracts/039ed9214602f2a93eb05411f852fa78a476607634")
pdf.ln(2)
pdf.body_text("Full submission log with all TX hashes: relay/secret-submissions-log.json")
pdf.body_text("Privacy verification evidence: relay/m3-state-evidence.json")
pdf.ln(2)

pdf.sub_title("5.3 MPC Computation Result")
pdf.body_text("After secret submission, the MPC computation was triggered and completed:")
pdf.body_text("- Query: age_threshold (count users with age > 18)")
pdf.body_text("- Result: 5 (all 5 submitted test users had age > 18)")
pdf.body_text("- Computation method: MPC across 4 PBC ZK nodes")
pdf.body_text("- No individual data exposed - aggregate result only")
pdf.hr()

# 6. Repository
pdf.section_title("6. Repository")
pdf.body_text("GitHub: https://github.com/Profila/Aiken-Partisia_MPC")
pdf.body_text("Test dataset: test-data/profila_test_users.json")
pdf.body_text("Secret submission script: relay/submit_secrets.ts")
pdf.body_text("Submission log: relay/secret-submissions-log.json")
pdf.body_text("Privacy evidence: relay/m3-state-evidence.json")
pdf.body_text("M3 report: docs/evidence/milestone-3-report.json")
pdf.hr()

# 7. Video
pdf.section_title("7. Video Demo")
pdf.body_text("M3 Demo: https://youtu.be/psm2lMU7n1o")
pdf.body_text("Combined M1-M4 Demo: https://youtu.be/jwwfdTSUS2w")
pdf.ln(6)

# Footer
pdf.hr()
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Project Catalyst Fund 13 - Proposal #1200045", align="C")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence", "milestone-3-report.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
