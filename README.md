# Indian Telecom Forensic Analysis & Triage Toolkit (ITF-KIT)

A dedicated digital forensics and investigative triage tool for analyzing Indian telephone numbers, landlines, telecom circles, and Call Detail Records (CDR).

---

## Capabilities

1. **Single Number Deep Triage:**
   - Validates numbers according to the Department of Telecommunications (DoT) National Numbering Plan.
   - Formats numbers in E.164, National, and International standards.
   - Identifies Line Classification (Mobile Cellular, PSTN Landline, Toll-Free, VoIP, UAN).
   - Maps to the official **22 Indian Telecom Circles / LSAs** (Category Metro, A, B, C) with Circle HQs.
   - Identifies original carrier network prefix allocation (Airtel, Jio, Vi, BSNL, MTNL).
   - Resolves Landline STD area codes across all major Indian cities.
   - Identifies Indian statutory emergency numbers (112, 100, 108, 1090, 1930 Cyber Fraud Helpline).

2. **Batch Phone Number Analysis:**
   - Process multiple phone numbers from text/CSV inputs.
   - Fast triage and structured forensic exports (JSON).

3. **Call Detail Record (CDR) & Cell Tower Analyzer:**
   - Parses CDR logs to extract call duration stats, incoming/outgoing volume, and frequency matrices.
   - Aggregates and ranks the most frequently visited cell site / tower identifiers (CGI / LAC-CellID).

4. **Investigative & Legal Reference:**
   - Documentation and guidance for Section 91 CrPC / Section 94 BNSS legal notices to Telecom Service Provider (TSP) Nodal Officers.
   - CEIR IMEI tracking integration notes and Cybercrime 1930 portal reporting references.

---

## How to Run

### Option 1: Web Dashboard (Interactive GUI)
Double-click `Run-TelecomForensics-Web.bat` in the workspace root, or run:
```bash
python apps/IndiaTelecomForensics/web_app.py
```
Open your browser at: `http://127.0.0.1:8899`

### Option 2: Command Line Interface (CLI)
Double-click `Run-TelecomForensics-CLI.bat` in the workspace root, or run:
```bash
python apps/IndiaTelecomForensics/cli.py
```
