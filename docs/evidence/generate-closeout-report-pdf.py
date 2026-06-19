#!/usr/bin/env python3
"""Generate Final Closeout Report PDF from closeout-report.json (same content, PDF format)."""

import sys, unittest.mock
for mod in ['cryptography', 'cryptography.hazmat', 'cryptography.hazmat.primitives',
            'cryptography.hazmat.primitives.serialization',
            'cryptography.hazmat.primitives.serialization.pkcs12',
            'cryptography.hazmat.primitives._serialization',
            'cryptography.hazmat.primitives.hashes',
            'cryptography.hazmat.bindings', 'cryptography.hazmat.bindings._rust']:
    sys.modules[mod] = unittest.mock.MagicMock()

from fpdf import FPDF
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "closeout-report.json")
OUT = os.path.join(HERE, "closeout-report.pdf")

def _chunks(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)] or [""]

def _s(t):
    if t is None: return ""
    return (str(t)
            .replace("—", "-").replace("–", "-")
            .replace("‘", "'").replace("’", "'")
            .replace("“", '"').replace("”", '"')
            .replace("…", "...").replace(" ", " "))

with open(SRC) as f:
    data = json.load(f)


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 7, "Final Closeout Report | Catalyst #1200045", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, _s(title))
        self.ln(10)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 7, _s(title))
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, _s(text))
        self.ln(2)

    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, _s(text))
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(5)
        self.multi_cell(0, 5.5, f"- {_s(text)}")
        self.ln(0.5)

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
            self.cell(widths[i], 6.5, _s(col), border=1, align=a)
        self.ln()


pdf = ReportPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# Cover / metadata
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 14, "Final Closeout Report", align="C")
pdf.ln(8)
pdf.set_font("Helvetica", "", 13)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 8, _s(data["title"]), align="C")
pdf.ln(4)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, f"Project ID: {data['project_id']}   |   Fund: {data['fund']}", align="C")
pdf.ln(5)
pdf.cell(0, 6, f"Proposer: {data['proposer']}", align="C")
pdf.ln(5)
pdf.cell(0, 6, f"Date: {data['date']}", align="C")
pdf.ln(8)
pdf.hr()

# Executive Summary
pdf.section_title("1. Executive Summary")
pdf.body_text(data["executive_summary"])
pdf.hr()

# Milestones
pdf.section_title("2. Milestones")
w = [12, 60, 22, 76]
pdf.table_header(["ID", "Title", "Status", "Key Evidence"], w)
for m in data["milestones"]:
    evidence = m["evidence"][0] if m["evidence"] else ""
    pdf.table_row([m["id"], m["title"], m["status"], evidence], w, ["C", "L", "C", "L"])
pdf.ln(3)

for m in data["milestones"]:
    pdf.sub_title(f"{m['id']} - {m['title']}  [{m['status']}]")
    pdf.bold_text("Deliverables:")
    for d in m["deliverables"]:
        pdf.bullet(d)
    pdf.bold_text("Evidence:")
    for e in m["evidence"]:
        pdf.bullet(e)
    pdf.ln(1)
pdf.hr()

# Architecture
pdf.section_title("3. Architecture")
arch = data["architecture"]
for layer_key, layer_label in [("layer_1", "Layer 1"), ("bridge", "Bridge"), ("layer_2", "Layer 2")]:
    layer = arch[layer_key]
    pdf.sub_title(f"{layer_label}")
    for k, v in layer.items():
        pdf.body_text(f"{k.replace('_', ' ').title()}: {v}")
pdf.hr()

# Key Achievements
pdf.section_title("4. Key Achievements")
for a in data["key_achievements"]:
    pdf.bullet(a)
pdf.ln(2)
pdf.hr()

# Technical Notes
pdf.section_title("5. Technical Notes")
for k, v in data["technical_notes"].items():
    pdf.sub_title(k.replace("_", " ").title())
    pdf.body_text(v)
pdf.hr()

# Test Summary
pdf.section_title("6. Test Summary")
ts = data["test_summary"]
w2 = [50, 25, 25, 70]
pdf.table_header(["Suite", "Total", "Passed", "Framework"], w2)
pdf.table_row(
    ["Aiken (Cardano)", str(ts["aiken_tests"]["total"]), str(ts["aiken_tests"]["passed"]), "aiken check"],
    w2, ["L", "C", "C", "L"],
)
pdf.table_row(
    ["PBC (Rust)", str(ts["pbc_tests"]["total"]), str(ts["pbc_tests"]["passed"]), "cargo test"],
    w2, ["L", "C", "C", "L"],
)
total = ts["aiken_tests"]["total"] + ts["pbc_tests"]["total"]
passed = ts["aiken_tests"]["passed"] + ts["pbc_tests"]["passed"]
pdf.table_row(["Total", str(total), str(passed), "All passing"], w2, ["L", "C", "C", "L"])
pdf.ln(3)

pdf.sub_title("Aiken Tests")
for t in ts["aiken_tests"]["test_names"]:
    pdf.bullet(t)
pdf.ln(1)
pdf.sub_title("PBC Tests")
for t in ts["pbc_tests"]["test_names"]:
    pdf.bullet(t)
pdf.hr()

# Videos
pdf.section_title("7. Videos")
video_labels = {
    "pcv_final_closeout": "Final Closeout Video (Catalyst PCV)",
    "m1_aiken_contract": "M1 - Aiken Contract",
    "m2_pbc_contract_relay": "M2 - PBC Contract + Relay",
    "m3_secret_inputs": "M3 - Secret Inputs",
    "m4_result_closeout": "M4 - Result & Closeout",
    "combined_m1_m4": "Combined M1-M4 End-to-End",
}
for key, url in data["videos"].items():
    pdf.link_line(f"{video_labels.get(key, key)}:", url)
pdf.hr()

# Repository
pdf.section_title("8. Repository")
repo = data["repository"]
pdf.link_line("URL:", repo["url"])
pdf.body_text(f"Branch: {repo['branch']}")
pdf.body_text(f"Files: {repo['total_files']}")
pdf.hr()

# Future Work
pdf.section_title("9. Future Work")
for f in data["future_work"]:
    pdf.bullet(f)
pdf.ln(4)
pdf.hr()

pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 6, "Profila AG x Partisia Blockchain", align="C")
pdf.ln(5)
pdf.cell(0, 6, "Project Catalyst Fund 13 - Proposal #1200045", align="C")

pdf.output(OUT)
print(f"PDF generated: {OUT}")
