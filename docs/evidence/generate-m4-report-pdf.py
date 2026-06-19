#!/usr/bin/env python3
"""Generate Milestone 4 Report PDF (SoW-mapped: 7 acceptance criteria, in order)."""

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

REPO = "https://github.com/Profila/Aiken-Partisia_MPC"

def _chunks(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)] or [""]

def _s(t):
    if t is None: return ""
    return (str(t)
            .replace("—", "-").replace("–", "-")
            .replace("‘", "'").replace("’", "'")
            .replace("“", '"').replace("”", '"')
            .replace("…", "...").replace(" ", " "))

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
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, title)
        self.ln(1)
    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, title)
        self.ln(7)
    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)
    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)
    def link_line(self, label, url):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.l_margin)
        self.multi_cell(0, 5.5, _s(label), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(20, 60, 160)
        for chunk in _chunks(url, 95):
            self.set_x(self.l_margin)
            self.cell(170, 4.5, chunk, link=url, align="L")
            self.ln(4.5)
        self.ln(2)
    def hr(self):
        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(5)

pdf = ReportPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Title block
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 14, "Milestone 4", align="C")
pdf.ln(8)
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "Display the result of a MPC query and final closeout", align="C")
pdf.ln(9)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Project Catalyst #1200045: MPC as a Layer 2 Service to Cardano", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Network: Cardano Preprod + Partisia Blockchain Testnet", align="C")
pdf.ln(8)
pdf.hr()

pdf.section_title("Acceptance Criteria & Evidence")
pdf.ln(2)

# 1
pdf.sub_title("1. The result (dataset) of a MPC query will be documented and displayed to the initiator")
pdf.body_text(
    "MPC computation result: 5 (5 out of 5 submitted users have age > 18). "
    "Result fetched from live PBC contract state via REST API and displayed via terminal output "
    "and HTML evidence page. Aggregate result only - no individual data exposed."
)
pdf.link_line("MPC result:", f"{REPO}/blob/main/relay/mpc-result.json")
pdf.link_line("Result display script:", f"{REPO}/blob/main/relay/show_result.ts")

# 2
pdf.sub_title("2. Documentation provided in PDF format in English")
pdf.link_line("Link:", f"{REPO}/blob/main/docs/evidence/milestone-4-report.pdf")

# 3
pdf.sub_title("3. Documentation includes the definition of the final process of displaying the result of a MPC query")
pdf.body_text(
    "The process: show_result.ts calls PBC REST API, receives serialized contract state, "
    "decodes ProfilaMpcState binary, extracts aggregate result, displays in terminal and "
    "generates HTML evidence page with cross-chain links."
)
pdf.link_line("E2E run log (full 6-stage pipeline):", f"{REPO}/blob/main/docs/evidence/e2e-run-log.json")

# 4
pdf.sub_title("4. Video of the process uploaded to YouTube")
pdf.link_line("M4 Demo:", "https://youtu.be/2YYvELDzrGo")

# 5
pdf.sub_title("5. Video includes a demo of the end-to-end process as executed on the Cardano and PBC testnet, from query to MPC result")
pdf.link_line(
    "Cardano TX (query initiation):",
    "https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57",
)
pdf.link_line(
    "PBC Contract (result + state):",
    "https://browser.testnet.partisiablockchain.com/contracts/039ed9214602f2a93eb05411f852fa78a476607634",
)
pdf.link_line("Combined M1-M4 end-to-end demo:", "https://youtu.be/jwwfdTSUS2w")

# 6
pdf.sub_title("6. Final closeout report is publicly available")
pdf.link_line("Link:", f"{REPO}/blob/main/docs/evidence/closeout-report.pdf")

# 7
pdf.sub_title("7. Final closeout video is publicly available")
pdf.link_line("Catalyst Project Closeout Video (PCV):", "https://youtu.be/YFOK4pq9jIk")
pdf.link_line("Combined M1-M4 technical demo:", "https://youtu.be/jwwfdTSUS2w")

pdf.hr()

# Evidence of Milestone Completion
pdf.section_title("Evidence of Milestone Completion")
pdf.ln(1)
pdf.link_line(
    "Documentation (PDF):",
    f"{REPO}/blob/main/docs/evidence/milestone-4-report.pdf",
)
pdf.link_line("YouTube demo:", "https://youtu.be/2YYvELDzrGo")
pdf.link_line("Repository:", REPO)
pdf.link_line(
    "Stakeholder sign-off (Profila and Partisia):",
    f"{REPO}/blob/main/docs/Profila%20%26%20Partisia%20Sign-off.pdf",
)
pdf.link_line(
    "Final closeout report:",
    f"{REPO}/blob/main/docs/evidence/closeout-report.pdf",
)
pdf.link_line("Final closeout video (Catalyst PCV):", "https://youtu.be/YFOK4pq9jIk")

pdf.hr()
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Project Catalyst Fund 13 - Proposal #1200045", align="C")

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "milestone-4-report.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
