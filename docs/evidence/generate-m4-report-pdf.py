#!/usr/bin/env python3
"""Generate Milestone 4 Report PDF."""

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
        self.cell(0, 7, "Milestone 4 - Proof of Achievement | Catalyst #1200045", align="C")
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
pdf.cell(0, 14, "Milestone 4", align="C")
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
pdf.cell(0, 6, "Network: Cardano Preprod + Partisia Blockchain Testnet", align="C")
pdf.ln(10)
pdf.hr()

# 1. Executive Summary
pdf.section_title("1. Executive Summary")
pdf.body_text(
    "Milestone 4 completes the end-to-end MPC pipeline. The MPC computation result is displayed "
    "to the initiator, the full cross-chain flow from Cardano query to Partisia MPC result is "
    "demonstrated, and the final closeout report and video are publicly available."
)
pdf.bold_text("All acceptance criteria are met. Project is complete.")
pdf.hr()

# 2. Acceptance Criteria
pdf.section_title("2. Acceptance Criteria - Evidence Matrix")
w = [8, 72, 14, 76]
pdf.table_header(["#", "Criterion", "Status", "Evidence"], w)
rows = [
    ["1", "MPC result displayed to initiator", "PASS", "Section 3 - result=5 on-chain"],
    ["2", "PDF documentation in English", "PASS", "This document"],
    ["3", "Process of displaying MPC result", "PASS", "Section 4 - show_result.ts flow"],
    ["4", "YouTube video of process", "PASS", "youtu.be/2YYvELDzrGo"],
    ["5", "E2E demo on Cardano + PBC testnet", "PASS", "Section 5 - full pipeline"],
    ["6", "Final closeout report public", "PASS", "Section 7 - closeout-report.json"],
    ["7", "Final closeout video public", "PASS", "youtu.be/jwwfdTSUS2w"],
]
for r in rows:
    pdf.table_row(r, w, ["C", "L", "C", "L"])
pdf.ln(4)
pdf.hr()

# 3. MPC Result
pdf.section_title("3. MPC Query Result")
pdf.sub_title("3.1 Result Displayed to Initiator")
pdf.body_text(
    "The MPC computation result is fetched from the live PBC contract state via REST API "
    "and displayed to the initiator via terminal output and HTML evidence page."
)
w2 = [50, 120]
pdf.table_header(["Property", "Value"], w2)
result_rows = [
    ["Query Type", "age_threshold (count users with age > 18)"],
    ["Dataset", "profila_test_v1"],
    ["Result", "5 (5 out of 5 submitted users have age > 18)"],
    ["Participants", "50 (dataset), 5 (submitted secrets)"],
    ["Computation Method", "MPC across 4 PBC ZK nodes"],
    ["Result Source", "on-chain (live PBC contract state)"],
    ["Computation Complete", "true"],
    ["Privacy", "Aggregate result only - no individual data exposed"],
]
for r in result_rows:
    pdf.table_row(r, w2)
pdf.ln(4)

pdf.sub_title("3.2 Result Evidence Files")
pdf.body_text("MPC result JSON: relay/mpc-result.json")
pdf.body_text("HTML result display: relay/result-display.html")
pdf.body_text("Result display script: relay/show_result.ts")
pdf.hr()

# 4. Result Display Process
pdf.section_title("4. Process of Displaying the MPC Result")
pdf.sub_title("4.1 How the Result Is Retrieved and Displayed")
pdf.body_text("1. show_result.ts calls PBC REST API: GET /chain/contracts/{address}")
pdf.body_text("2. Receives serializedContract (base64-encoded binary state)")
pdf.body_text("3. Decodes ProfilaMpcState: administrator, dataset_id, query_type, min_participants, result, computation_complete")
pdf.body_text("4. Extracts the aggregate result value (i64)")
pdf.body_text("5. Displays result in terminal with formatted output")
pdf.body_text("6. Generates HTML evidence page with cross-chain links")
pdf.body_text("7. Writes mpc-result.json with full provenance chain")
pdf.ln(2)

pdf.sub_title("4.2 Computation Trigger")
pdf.body_text("The MPC computation was triggered via the PBC testnet browser with 100M gas:")
w3 = [50, 120]
pdf.table_header(["Property", "Value"], w3)
trigger_rows = [
    ["Action", "start_computation (shortname 0x01)"],
    ["Trigger TX", "d836a6fc075e9ce7...f07c54cc"],
    ["Gas Fee", "100,000,000 (100M)"],
    ["4 MPC Nodes", "All committed results successfully"],
    ["Contract Result", "computation_complete=true, result=5"],
]
for r in trigger_rows:
    pdf.table_row(r, w3)
pdf.ln(4)
pdf.hr()

# 5. End-to-End Flow
pdf.section_title("5. End-to-End Process - Cardano to MPC Result")
pdf.body_text("The complete pipeline from query initiation on Cardano to MPC result:")
pdf.ln(2)
pdf.set_font("Courier", "", 8)
pdf.multi_cell(0, 5,
    "Stage 1: Cardano SC Deployment  -> Aiken MpcRequest UTxO on preprod\n"
    "Stage 2: Relay Detection         -> relay.ts polls Blockfrost, detects datum\n"
    "Stage 3: PBC Contract Deployment -> ZK contract on PBC testnet\n"
    "Stage 4: Secret Submission       -> 5 real ZK transactions via PBC SDK\n"
    "Stage 5: MPC Computation         -> Triggered via browser, 4 nodes compute\n"
    "Stage 6: Result Display          -> show_result.ts decodes on-chain state"
)
pdf.ln(4)
pdf.set_font("Helvetica", "", 10)

pdf.sub_title("5.1 Cross-Chain Verification Links")
pdf.body_text("Cardano TX (query initiation):")
pdf.body_text("https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57")
pdf.body_text("Cardano Script Address:")
pdf.body_text("https://preprod.cardanoscan.io/address/addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz")
pdf.body_text("PBC Contract (result + state):")
pdf.body_text("https://browser.testnet.partisiablockchain.com/contracts/039ed9214602f2a93eb05411f852fa78a476607634")
pdf.ln(2)

pdf.sub_title("5.2 E2E Run Log")
pdf.body_text("Full 6-stage execution log with all TX hashes: docs/evidence/e2e-run-log.json")
pdf.hr()

# 6. Test Summary
pdf.section_title("6. Test Summary")
w4 = [40, 30, 30, 70]
pdf.table_header(["Suite", "Tests", "Passed", "Framework"], w4)
pdf.table_row(["Aiken (Cardano)", "6", "6", "aiken check"], w4, ["L", "C", "C", "L"])
pdf.table_row(["PBC (Rust)", "11", "11", "cargo test"], w4, ["L", "C", "C", "L"])
pdf.table_row(["Total", "17", "17", "All passing"], w4, ["L", "C", "C", "L"])
pdf.ln(4)
pdf.hr()

# 7. Closeout
pdf.section_title("7. Final Closeout")
pdf.sub_title("7.1 Closeout Report")
pdf.body_text("Publicly available in the repository:")
pdf.body_text("https://github.com/Profila/Aiken-Partisia_MPC/blob/main/docs/evidence/closeout-report.json")
pdf.ln(2)

pdf.sub_title("7.2 Closeout Video")
pdf.body_text("M4 Result & Closeout Demo: https://youtu.be/2YYvELDzrGo")
pdf.body_text("Combined M1-M4 Full Demo: https://youtu.be/jwwfdTSUS2w")
pdf.hr()

# 8. Repository
pdf.section_title("8. Repository")
pdf.body_text("GitHub: https://github.com/Profila/Aiken-Partisia_MPC")
pdf.body_text("Result display: relay/show_result.ts")
pdf.body_text("MPC result: relay/mpc-result.json")
pdf.body_text("Computation trigger: relay/trigger_computation.ts")
pdf.body_text("E2E run log: docs/evidence/e2e-run-log.json")
pdf.body_text("Closeout report: docs/evidence/closeout-report.json")
pdf.body_text("Evidence page: docs/poc-evidence.html")
pdf.hr()

# 9. Video
pdf.section_title("9. Video Demos")
pdf.body_text("M4 Result & Closeout: https://youtu.be/2YYvELDzrGo")
pdf.body_text("Combined M1-M4 End-to-End: https://youtu.be/jwwfdTSUS2w")
pdf.ln(6)

# Footer
pdf.hr()
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Project Catalyst Fund 13 - Proposal #1200045", align="C")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "evidence", "milestone-4-report.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
