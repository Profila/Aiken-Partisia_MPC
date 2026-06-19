# Closeout Video Script & Walkthrough Plan

**Project:** Catalyst Fund 13 — Proposal #1200045 — *MPC as a Layer 2 Service to Cardano*
**Parties:** Profila AG × Partisia Blockchain
**Purpose:** Project Closeout Video (PCV) for Catalyst final milestone resubmission.

This document is the source script and recording plan for the new closeout video. It is preserved in the repo so the deliverable is reproducible.

---

## 1. Catalyst PCV requirements (from Catalyst guidelines)

The video must:

- Be **2–5 minutes**, **720p or 1080p**, publicly hosted on YouTube.
- Cover four elements:
  1. **Challenge entered, approach proposed, funding received** — what we applied for, what we proposed, what we got.
  2. **Progress, milestones/KPIs, learnings, scope adherence** — once funded, how it went; what was met, what was not.
  3. **Demonstration of project outputs** — clear evidence of the software/dApp that was built.
  4. **What's next / commercialisation** — future plans, follow-on funding sought, exploitation.

---

## 2. Recording approach — screen walkthrough of the live project website

The cleanest path is a **screen recording of `https://cardano-catalyst.profila.com/`** (or `docs/poc-evidence.html` as a local fallback), with voiceover. The site already contains the architecture, milestones, on-chain identifiers, dataset, results, privacy proof, and evidence trail. No demo footage needs to be re-shot.

### Pre-record check on the live site

Before recording, confirm the live site shows the values below. If anything is stale, redeploy first.

| Item | Expected value |
|---|---|
| Project title | MPC as a Layer 2 Service to Cardano |
| Catalyst ID | #1200045 |
| Milestones | M1, M2, M3, M4 — all marked Complete |
| Test counts | Aiken 6/6, PBC 11/11 (17 total) |
| MPC result | 5 (5 of 5 users > 18) |
| Cardano TX | `50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57` |
| PBC contract | `039ed9214602f2a93eb05411f852fa78a476607634` |
| Cardano script address | `addr_test1wzut662xhd8e4jq97fpdsml2pyqerejwzfg24red2n7gceczhkwaz` |
| Closeout report link | `docs/evidence/closeout-report.pdf` (PDF, not JSON) |
| YouTube IDs present | QRj4tAt23Aw, lC_2EG6gxX0, psm2lMU7n1o, 2YYvELDzrGo, jwwfdTSUS2w |

### Recording setup

1. Browser at **1920×1080**, clean profile, no bookmarks bar.
2. Tab 1: `https://cardano-catalyst.profila.com/` (primary).
3. Tab 2: `https://preprod.cardanoscan.io/transaction/50d28fd2bd263a84485b45280afd19bb4c3e20c24e9a4b52b6eac20418d53a57`
4. Tab 3: `https://browser.testnet.partisiablockchain.com/contracts/039ed9214602f2a93eb05411f852fa78a476607634`
5. Recorder: OBS / Loom / QuickTime — **1080p, microphone on**.

---

## 3. Final script (~4 min)

### 0:00–0:15 — Open (title section of the site)

> "Hi, I'm [name] from Profila. This is the project closeout video for Catalyst Fund 13, proposal #1200045 — *MPC as a Layer 2 Service to Cardano* — a joint build by Profila AG and Partisia Blockchain. In the next four minutes I'll walk through what we proposed, what we built, what we learned, and what's next."

### 0:15–1:00 — Element 1: Challenge, approach, funding

*Scroll to **Cross-Chain Privacy Architecture** + **From Data Request to Privacy-Preserving Result***

> "We entered the *Cardano Partners and Real World Integrations* challenge under Fund 13. The problem we set out to solve: Cardano dApps can anchor identity and ownership on-chain, but they can't run private analytics over personal data without exposing it. Our proposal was to bridge Cardano to Partisia Blockchain's MPC infrastructure. An Aiken validator on Cardano coordinates the request, an off-chain relay forwards it, and a ZK MPC contract on Partisia computes an aggregate result over encrypted user inputs. No individual data ever touches a public ledger or log. We received [insert ADA amount] in funding across four milestones."

### 1:00–2:00 — Element 2: Progress, milestones, learnings

*Scroll to **Four Milestones — All Complete** cards*

> "We delivered all four milestones on testnet.
>
> M1 — Aiken validator on Cardano Preprod, 6 unit tests passing, MPC request recorded as inline datum.
>
> M2 — Partisia ZK MPC contract in Rust, 11 unit tests passing, and a TypeScript relay polling Blockfrost and bridging requests to Partisia.
>
> M3 — A 50-user synthetic dataset and five real on-chain ZK secret-input transactions submitted through Partisia's TypeScript SDK, with verified privacy.
>
> M4 — MPC computation triggered across four nodes, on-chain aggregate result of 5 — all five submitted users over age 18 — fetched live from Partisia's REST API and displayed to the initiator.
>
> Biggest learning: Partisia's CLI transaction tool currently returns HTTP 400 on testnet, so we moved to the TypeScript SDK and the browser for contract deployment and computation triggering — that pattern is now documented in the repo. ZK MPC across four nodes also needs about 100 million gas, which we sized through trial. Scope-wise, we delivered everything in the SoW; nothing was descoped. 17 of 17 tests pass."

### 2:00–3:15 — Element 3: Live demonstration

*Scroll to **Live Contract State — Decoded from Binary***. Click into the Cardano Preprod and Partisia Testnet tabs to show real on-chain state. Then briefly switch to the Cardanoscan and Partisia browser tabs to prove the on-chain data is live, not mocked.

> "Here's the live state. This is the Cardano Preprod transaction that initiated the MPC query — you can see the inline datum on Cardanoscan. And here's the Partisia contract, with state fields decoded directly from the on-chain binary: administrator, dataset ID, query type, and the aggregate result — 5 — with `computation_complete = true`. No individual ages, no raw data, just the aggregate."

*Scroll to **Computation Results** + **Zero Individual Data Exposed***

> "Five of five submitted users were over 18. The Computation Results section shows the value the initiator sees; the Privacy section confirms that across contract state, the secret tab, the logs, and the relay output, zero individual data is exposed."

### 3:15–3:40 — Element 4: What's next

*Scroll to **Complete Evidence Trail***

> "What's next: a Cardano result callback so the MPC result writes back to a Cardano UTxO, multi-query support to run several MPC computations in parallel, and a mainnet deployment on both Cardano and Partisia with real Profila user data under explicit consent. Profila will integrate this as part of our consented-data marketplace. We're evaluating follow-on Catalyst funding for the mainnet hardening and audit phase."

### 3:40–4:00 — Close

> "All deliverables, on-chain transactions, the full closeout report, and this video link are public in the GitHub repo and in the milestone PoA. Thanks to Catalyst, the Cardano community, and the Partisia team. — Profila AG."

---

## 4. Reusing existing video footage (optional B-roll)

If you prefer to cut clips rather than do a continuous screen-record, the five existing videos cover everything. Suggested cuts:

| Source video | Use as |
|---|---|
| `combined_m1_m4` (jwwfdTSUS2w) | ~60–75 s end-to-end demo for Element 3 |
| `m1_aiken_contract` (QRj4tAt23Aw) | `aiken check` 6/6 passing shot for Element 2 (M1) |
| `m2_pbc_contract_relay` (lC_2EG6gxX0) | architecture diagram + `cargo test` 11/11 for Element 1 & 2 (M2) |
| `m3_secret_inputs` (psm2lMU7n1o) | 5 secret TXs on PBC browser + privacy verification for Element 2 (M3) |
| `m4_result_closeout` (2YYvELDzrGo) | `show_result.ts` terminal + HTML result page for Element 3 |

---

## 5. Compliance map — script section → PCV requirement

| Script timestamp | PCV element | Catalyst-required content covered |
|---|---|---|
| 0:00–0:15 | Intro | Identity, project, funding round |
| 0:15–1:00 | 1 | Challenge name, problem, proposed approach, technical solutions, funding received |
| 1:00–2:00 | 2 | Progress, milestone-by-milestone achievement, KPI status (17/17 tests), learnings (CLI→SDK pivot, gas sizing), scope adherence (nothing descoped) |
| 2:00–3:15 | 3 | Live demonstration of the built software on real testnet state |
| 3:15–3:40 | 4 | Next steps, commercialisation (Profila marketplace integration), further funding (Catalyst follow-on) |
| 3:40–4:00 | Close | Pointers to evidence repo + closeout report |

Duration: ~4:00 (within 2–5 min). Quality: record and export at 1080p.

---

## 6. After recording — upload & repo updates

1. Upload to YouTube as **Public**, 1080p. Title suggestion: `Catalyst F13 #1200045 Closeout — MPC as a Layer 2 Service to Cardano (Profila × Partisia)`.
2. Copy the new YouTube URL.
3. Update `docs/evidence/closeout-report.json` — set `videos.pcv` (or replace `videos.m4_result_closeout`) to the new URL.
4. Regenerate the PDF: `python3 docs/evidence/generate-closeout-report-pdf.py`.
5. Update the PoA "Final closeout video" link to the new URL.
6. Commit and push.

---

## 7. Resubmission checklist (Catalyst final milestone)

- [ ] M1, M2, M3 PoAs resubmitted **unchanged** (per reviewer instruction).
- [ ] M4 PoA resubmitted with `closeout-report.pdf` link (no longer `.json`).
- [ ] `docs/evidence/closeout-report.pdf` downloadable on `main` branch.
- [ ] `docs/evidence/milestone-4-report.pdf` matches the SoW-mapped 7-criteria layout.
- [ ] New PCV video uploaded, public, 1080p, 2–5 min, covers all four elements above.
- [ ] PoA "Final closeout video" link updated to new PCV URL.
- [ ] Stakeholder sign-off PDF (`docs/Profila & Partisia Sign-off.pdf`) referenced.
