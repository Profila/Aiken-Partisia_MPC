#!/usr/bin/env python3
"""Generate stakeholder sign-off PDF for Milestone 1."""

import sys, unittest.mock
# Work around broken cryptography C extension in this environment
for mod in ['cryptography', 'cryptography.hazmat', 'cryptography.hazmat.primitives',
            'cryptography.hazmat.primitives.serialization',
            'cryptography.hazmat.primitives.serialization.pkcs12',
            'cryptography.hazmat.primitives._serialization',
            'cryptography.hazmat.primitives.hashes',
            'cryptography.hazmat.bindings', 'cryptography.hazmat.bindings._rust']:
    sys.modules[mod] = unittest.mock.MagicMock()

from fpdf import FPDF
import os

class SignOffPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Project Catalyst #1200045 - Stakeholder Sign-Off", align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


pdf = SignOffPDF()
pdf.set_auto_page_break(auto=True, margin=25)
pdf.add_page()

# Title
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 14, "Stakeholder Sign-Off", align="C")
pdf.ln(10)

pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 8, "MPC as a Layer 2 Service to Cardano", align="C")
pdf.ln(16)

# Horizontal rule
pdf.set_draw_color(200, 200, 200)
pdf.line(20, pdf.get_y(), 190, pdf.get_y())
pdf.ln(10)

# Project Overview
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 8, "Project Overview")
pdf.ln(10)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(40, 40, 40)
overview = (
    "This project, funded under Project Catalyst (Proposal #1200045), is a joint effort "
    "between Profila AG and Partisia Blockchain to build a cross-chain integration that "
    "enables privacy-preserving Multi-Party Computation (MPC) as a Layer 2 service to "
    "the Cardano blockchain."
)
pdf.multi_cell(0, 6, overview)
pdf.ln(4)

scope = (
    "The implementation connects an Aiken smart contract on Cardano with a Partisia "
    "Blockchain MPC smart contract via a relay service. Users can initiate MPC computation "
    "requests on Cardano, have them processed through Partisia's MPC engine with encrypted "
    "secret inputs, and receive results back on-chain - all without exposing private data."
)
pdf.multi_cell(0, 6, scope)
pdf.ln(8)

# Milestones
pdf.set_font("Helvetica", "B", 13)
pdf.cell(0, 8, "Milestones")
pdf.ln(10)

milestones = [
    ("Milestone 1", "Aiken smart contract on Cardano preprod testnet with MPC initiation "
     "functionality, unit tests, documentation, and video demo."),
    ("Milestone 2", "Partisia Blockchain MPC smart contract and relay service connecting "
     "Cardano to Partisia, with deployment evidence and video demo."),
    ("Milestone 3", "Secret input submission to Partisia MPC contract with privacy-preserving "
     "computation, on-chain evidence, and video demo."),
    ("Milestone 4", "End-to-end result flow from MPC computation back to Cardano with "
     "closeout report and final video demo."),
]

for title, desc in milestones:
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, title)
    pdf.ln(7)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 5.5, desc)
    pdf.ln(4)

pdf.ln(4)

# Repository
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 8, "Repository")
pdf.ln(10)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(40, 40, 40)
pdf.cell(0, 6, "https://github.com/Profila/Aiken-Partisia_MPC")
pdf.ln(12)

# Sign-off statement
pdf.set_draw_color(200, 200, 200)
pdf.line(20, pdf.get_y(), 190, pdf.get_y())
pdf.ln(10)

pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 8, "Sign-Off Agreement")
pdf.ln(10)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(40, 40, 40)
statement = (
    "By signing below, both parties confirm that they have reviewed the deliverables "
    "for this project and approve the implementation as meeting the agreed-upon scope "
    "and acceptance criteria for all milestones."
)
pdf.multi_cell(0, 6, statement)
pdf.ln(16)

# Signature blocks
def signature_block(pdf, party_name, y_start):
    pdf.set_y(y_start)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 7, party_name)
    pdf.ln(20)

    pdf.set_draw_color(0, 0, 0)
    pdf.line(20, pdf.get_y(), 110, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(90, 5, "Signature")
    pdf.ln(12)

    pdf.set_draw_color(0, 0, 0)
    pdf.line(20, pdf.get_y(), 110, pdf.get_y())
    pdf.ln(2)
    pdf.cell(90, 5, "Name and Title")
    pdf.ln(12)

    pdf.set_draw_color(0, 0, 0)
    pdf.line(20, pdf.get_y(), 110, pdf.get_y())
    pdf.ln(2)
    pdf.cell(90, 5, "Date")
    pdf.ln(8)

y = pdf.get_y()
signature_block(pdf, "On behalf of Profila AG", y)

y2 = pdf.get_y() + 6
signature_block(pdf, "On behalf of Partisia Blockchain", y2)

# Output
out_path = os.path.join(os.path.dirname(__file__), "stakeholder-signoff.pdf")
pdf.output(out_path)
print(f"PDF generated: {out_path}")
