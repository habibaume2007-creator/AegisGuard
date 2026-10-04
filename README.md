<div align="center">

# 🛡️ AegisGuard

### AI-Assisted Vulnerability Detection, Remediation & Verification

**Finds • Proves • Fixes • Verifies — with a human in control**

<br>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Security_UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-5B4BFF?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)
![RAG](https://img.shields.io/badge/RAG-TF--IDF-7C3AED?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-Verification-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Memory-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

<br>

### 🚀 From Vulnerability Detection to Verified Remediation

AegisGuard combines **static analysis, multi-agent AI, RAG, automated verification, long-term memory, and human approval** into one application-security workflow.

---

### 🧭 Project Navigator

[![Overview](https://img.shields.io/badge/Overview-Project-2563EB?style=for-the-badge)](#overview)
[![Problem](https://img.shields.io/badge/Problem-Security_Gap-DC2626?style=for-the-badge)](#the-problem)
[![Solution](https://img.shields.io/badge/Solution-AegisGuard-16A34A?style=for-the-badge)](#the-solution)
[![Workflow](https://img.shields.io/badge/Core-Workflow-0EA5E9?style=for-the-badge)](#core-workflow)
[![Features](https://img.shields.io/badge/Features-Core_Capabilities-9333EA?style=for-the-badge)](#key-features)

[![Tech Stack](https://img.shields.io/badge/Tech_Stack-Architecture-0891B2?style=for-the-badge)](#technology-stack)
[![Architecture](https://img.shields.io/badge/System-Architecture-4F46E5?style=for-the-badge)](#system-architecture)
[![Backend Flow](https://img.shields.io/badge/Backend-Connections-0F766E?style=for-the-badge)](#how-the-backend-components-connect)
[![Multi Agent](https://img.shields.io/badge/Multi--Agent-LangGraph-7C3AED?style=for-the-badge)](#multi-agent-workflow)
[![RAG](https://img.shields.io/badge/RAG-Knowledge_Layer-D97706?style=for-the-badge)](#rag-implementation)

[![Vulnerabilities](https://img.shields.io/badge/Vulnerability-Coverage-B91C1C?style=for-the-badge)](#supported-vulnerabilities)
[![Project Structure](https://img.shields.io/badge/Project-Structure-475569?style=for-the-badge)](#project-structure)
[![Requirements](https://img.shields.io/badge/Requirements-Environment-64748B?style=for-the-badge)](#requirements)
[![Setup](https://img.shields.io/badge/Setup-Installation-475569?style=for-the-badge)](#installation--setup)

[![Run](https://img.shields.io/badge/Run-Application-0284C7?style=for-the-badge)](#run-the-application)
[![Demo](https://img.shields.io/badge/Live_Demo-Launch-16A34A?style=for-the-badge)](#live-demo)
[![Security](https://img.shields.io/badge/Security-Notes-B91C1C?style=for-the-badge)](#security-notes)
[![Roadmap](https://img.shields.io/badge/Roadmap-Future-0284C7?style=for-the-badge)](#future-roadmap)
[![Team](https://img.shields.io/badge/Team-AegisGuard-7C3AED?style=for-the-badge)](#team)
[![Philosophy](https://img.shields.io/badge/Security-Philosophy-111827?style=for-the-badge)](#security-philosophy)

---

### ⚡ Core Security Flow

**TRIAGE → EXPLOIT → CONFIRM → PATCH → VERIFY → HUMAN APPROVAL**

| 🔍 Detect | 🧪 Prove | 🧠 Retrieve | 🔧 Patch | ✅ Verify | 👤 Approve |
|---|---|---|---|---|---|
| Static Analysis | Exploit Test | RAG Guidance | Gemini | Pytest | Human Review |

> **AI may propose the fix. Evidence should verify it. Humans should approve it.**

</div>

---

## Overview

AegisGuard is an AI-assisted application-security prototype designed to move beyond traditional vulnerability detection.

Traditional security tools often focus on:

**Detect → Report**

AegisGuard extends that workflow to:

**Detect → Prove → Retrieve Security Knowledge → Patch → Verify → Remember → Human Approve**

The platform combines:

- 🛡️ Static source-code analysis
- 🤖 Multi-agent workflow orchestration
- 🧠 Retrieval-Augmented Generation
- 🧪 AI-generated security tests
- 🔧 AI-assisted remediation
- ✅ Automated verification
- 💾 Persistent security memory
- 👤 Human-in-the-loop approval

AegisGuard demonstrates how AI can support a more structured, test-driven, and evidence-based remediation workflow while keeping the final decision under human control.

---

## The Problem

Finding a vulnerability is only the beginning.

Traditional security scanners may identify risky code, but developers still need to:

- Determine whether the issue is actually exploitable
- Understand the vulnerable execution path
- Reproduce the vulnerability
- Research the correct remediation
- Write a secure patch
- Test whether the patch blocks the attack
- Ensure existing functionality still works
- Review and approve the final code change

AI coding assistants can generate fixes quickly, but an AI-generated patch should not be considered secure simply because it looks correct.

**A security fix must be verified.**

---

## The Solution

AegisGuard provides a structured remediation pipeline:

**TRIAGE → EXPLOIT → CONFIRM → PATCH → VERIFY → HUMAN APPROVAL**

AegisGuard attempts to answer six key questions:

1. **Where is the risky code?**
2. **Can the vulnerability be reproduced?**
3. **What security guidance is relevant?**
4. **What remediation should be proposed?**
5. **Does the remediation actually work?**
6. **Should a human approve the final change?**

---

## Core Workflow

### 1. Triage

AegisGuard analyzes Python source code using static analysis.

The triage stage uses:

- Python AST
- Vulnerability pattern detection
- Function analysis
- Route / entry-point detection
- NetworkX call graph analysis
- Reachability analysis

The goal is to identify the vulnerability type, the vulnerable function, and whether the risky function can be reached from an application route or entry point.

### 2. Exploit Generation

For trusted demonstration samples, AegisGuard uses AI to generate a targeted security regression test.

The generated test attempts to reproduce the suspected vulnerability.

### 3. Confirmation

The generated exploit test is executed.

If the expected security failure occurs, the finding can be treated as confirmed.

**Static Finding → Generated Security Test → Expected Failure → Vulnerability Confirmed**

### 4. Patch Generation

Once a vulnerability is confirmed, AegisGuard retrieves relevant security guidance through RAG and provides that context to the AI model before patch generation.

The patch stage can use:

- Vulnerable source code
- Detected vulnerability type
- Retrieved defensive guidance
- Previous successful fixes
- Previous failed attempts

### 5. Verification

AegisGuard does not stop after generating a patch.

The proposed remediation is validated using:

- Security regression test
- Original regression tests
- Static security re-check

A successful remediation should satisfy:

- ✅ Original attack is blocked
- ✅ Existing functionality still works
- ✅ Vulnerable static pattern is no longer detected

### Core Concept

**🔴 RED → PATCH → 🟢 GREEN**

- **RED:** Vulnerability reproduced
- **PATCH:** Remediation proposed
- **GREEN:** Attack blocked and regression tests pass

### 6. Human Approval

Even after automated verification, the final decision remains with the human reviewer.

**AI Suggestion → Automated Verification → Human Review → Approval**

---

## Key Features

- 🛡️ Static security scanning
- 📁 Python file and ZIP project upload
- 🤖 Multi-agent remediation workflow
- 🧠 RAG-grounded security guidance
- 🧪 AI-generated exploit tests
- 🔧 AI-assisted patch generation
- ✅ Automated security verification
- 🧾 Regression testing
- 💾 Long-term security memory
- 👤 Human-in-the-loop approval
- 📊 Run history
- 💬 Security Assistant

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| User Interface | **Streamlit** | Security dashboard, project upload, assistant, run history |
| Agent Orchestration | **LangGraph** | Multi-agent workflow, state, routing, retries |
| AI | **Google Gemini** | Exploit-test and patch generation |
| AI Integration | **LangChain Google GenAI** | Connects the application to Gemini |
| Static Analysis | **Python AST** | Source-code parsing and risky-pattern detection |
| Graph Analysis | **NetworkX** | Call graph and reachability analysis |
| RAG | **TF-IDF** | Retrieves relevant security guidance |
| Knowledge Base | **Markdown files** | Stores defensive security notes |
| Testing | **Pytest** | Security tests and regression verification |
| Memory | **SQLite** | Stores previous runs, fixes, failures, and outcomes |
| Demo Applications | **Flask** | Trusted sample applications |
| UI Theme | **Custom CSS + Streamlit Theme** | Professional dashboard styling |

---

## System Architecture

```mermaid
flowchart TD
    U[User] --> UI[Streamlit Interface]

    UI --> LG[LangGraph Multi-Agent Workflow]

    LG --> SA[Static Analysis]
    LG --> AI[Google Gemini]
    LG --> RAG[RAG Security Knowledge]

    SA --> AST[Python AST]
    SA --> NX[NetworkX Call Graph]

    RAG --> TFIDF[TF-IDF Retrieval]
    TFIDF --> KB[Markdown Security Knowledge Base]

    AI --> EX[Exploit Test Generation]
    AI --> PG[Patch Generation]

    AST --> LG
    NX --> LG
    KB --> AI

    EX --> TEST[Pytest Verification]
    PG --> TEST

    TEST --> MEM[SQLite Long-Term Memory]
    MEM --> LG

    TEST --> HUMAN[Human Approval]
```

---

## How the Backend Components Connect

AegisGuard is built as a connected remediation workflow rather than as a collection of independent libraries. Each backend component has a specific responsibility and passes its output to the next stage.

### Backend Integration Flow

```mermaid
flowchart LR
    U[User] --> UI[Streamlit UI]

    UI --> LG[LangGraph Multi-Agent Orchestration]

    LG --> SA[Static Analysis]
    LG --> EA[Exploit Agent]
    LG --> PA[Patch Agent]

    SA --> AST[Python AST]
    AST --> NX[NetworkX Reachability]
    NX --> LG

    EA --> GEM1[Google Gemini]
    GEM1 --> ET[Generated Exploit Test]

    PA --> RAG[TF-IDF RAG]
    RAG --> KB[Markdown Security Knowledge Base]
    KB --> GEM2[Google Gemini]
    GEM2 --> PATCH[Generated Patch]

    ET --> TEST[Pytest Verification]
    PATCH --> TEST

    TEST --> VERIFY[Verification Result]

    VERIFY --> MEM[SQLite Long-Term Memory]
    MEM --> LG

    VERIFY --> HUMAN[Human Approval]
```

### Component-to-Component Connection

| Component | Connects To | Purpose |
|---|---|---|
| **Streamlit** | LangGraph | Sends user actions, selected samples, uploads, and workflow requests to the backend |
| **LangGraph** | Workflow stages | Controls state, routing, retries, and transitions |
| **Python AST** | Triage / NetworkX | Parses Python source code and identifies risky patterns |
| **NetworkX** | LangGraph | Builds call relationships and helps determine reachability |
| **Google Gemini** | Exploit Agent | Generates targeted security regression tests |
| **TF-IDF RAG** | Patch Agent | Retrieves vulnerability-specific defensive guidance |
| **Markdown Knowledge Base** | RAG | Stores defensive security knowledge |
| **Google Gemini** | Patch Agent | Uses source code, RAG guidance, and context to propose remediation |
| **Pytest** | Verification Agent | Runs exploit tests and original regression tests |
| **Static Re-check** | Verification Agent | Checks whether the insecure code pattern remains |
| **SQLite** | LangGraph / Patch Context | Stores previous successes, failures, attempts, and verification outcomes |
| **Human Approval** | Final Workflow Stage | Keeps the final remediation decision under developer control |

### Complete Backend Flow

**User → Streamlit UI → LangGraph → Triage / Static Analysis → Python AST + NetworkX → Exploit Agent + Gemini → Vulnerability Confirmation → RAG Retrieval → Security Knowledge Base → Patch Agent + Gemini → Generated Patch → Pytest + Static Re-check → Verification Result → SQLite Memory → Human Approval**

### How RAG Connects to Patch Generation

**Detected Vulnerability → TF-IDF Search → Relevant Security Note → Vulnerable Source Code + Retrieved Guidance + Previous Memory → Google Gemini → Grounded Patch Suggestion**

### How Verification Connects Back to the Workflow

**Generated Patch → Exploit Test + Regression Tests + Static Re-check → Verification Result**

If verification succeeds:

**PASS → Ready for Human Approval**

If verification fails:

**FAIL → Retry / Escalate**

> **AegisGuard's backend is a closed remediation loop: Analyze → Prove → Retrieve → Patch → Verify → Remember → Approve.**

---

## Multi-Agent Workflow

AegisGuard uses **LangGraph** to divide the remediation process into specialized stages.

**Triage Agent → Exploit Agent → Confirmation → Patch Agent → Verification Agent → Record / Memory → Human Approval**

### Triage Agent

Responsible for:

- Detecting supported vulnerabilities
- Identifying the vulnerable function
- Determining the vulnerability type
- Inspecting reachability

### Exploit Agent

Responsible for:

- Generating targeted security regression tests
- Attempting to demonstrate the weakness

### Confirmation Stage

Responsible for:

- Running the generated security test
- Confirming whether the expected vulnerability behavior occurs

### Patch Agent

Responsible for:

- Retrieving relevant security guidance
- Using previous memory where appropriate
- Generating a proposed remediation

### Verification Agent

Responsible for:

- Re-running the exploit test
- Running original regression tests
- Performing the static re-check

### Memory Stage

Stores:

- Vulnerability type
- Function
- Exploit test
- Proposed patch
- Verification result
- Previous failures
- Successful fixes

---

## RAG Implementation

AegisGuard uses **Retrieval-Augmented Generation (RAG)** primarily during patch generation and in the Security Assistant.

### RAG Flow

**Detected Vulnerability → Query Security Knowledge Base → TF-IDF Retrieval → Relevant Security Guidance → Guidance + Vulnerable Code → Gemini → Grounded Patch Suggestion**

The local knowledge base contains security guidance for topics such as:

- SQL Injection
- Path Traversal
- Cross-Site Scripting
- Unsafe Deserialization

This allows the AI model to receive vulnerability-specific defensive guidance before producing a remediation.

RAG is also used in the **Security Assistant**, allowing questions to be answered using the local security knowledge base.

---

## Supported Vulnerabilities

The current prototype includes trusted demonstration scenarios for:

- SQL Injection
- Path Traversal
- Cross-Site Scripting (XSS)

The security knowledge base also includes defensive guidance for:

- Unsafe Deserialization

> AegisGuard is a prototype and should not be presented as a complete replacement for mature SAST, DAST, or enterprise application-security platforms.

---

## Project Structure

```text
AegisGuard/
│
├── app.py
├── agent.py
├── assistant.py
├── check_setup.py
├── config.py
├── graph_builder.py
├── memory.py
├── project_loader.py
├── rag.py
├── sandbox.py
├── scanner.py
├── ui_common.py
│
├── .streamlit/
│   └── config.toml
│
├── views/
│   ├── demo.py
│   ├── assistant.py
│   ├── memory_page.py
│   └── team.py
│
├── knowledge/
│   ├── aegisguard_overview.md
│   ├── path_traversal.md
│   ├── sql_injection.md
│   ├── unsafe_deserialization.md
│   └── xss.md
│
├── samples/
│   ├── path_traversal/
│   ├── sql_injection/
│   └── xss/
│
├── requirements.txt
├── .env.example
├── .gitignore
├── about.json
└── README.md
```

---

## Requirements

### Recommended Environment

- Python **3.12**
- pip
- Git
- Internet connection for Gemini API access

### Main Python Dependencies

- `langgraph`
- `langchain-google-genai`
- `networkx`
- `flask`
- `pytest`
- `streamlit`
- `python-dotenv`
- `docker`

All dependencies are listed in `requirements.txt`.

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/habibaume2007-creator/AegisGuard.git
cd AegisGuard
```

### 2. Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify:

```powershell
python --version
```

Expected:

```text
Python 3.12.x
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`.

Example:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=your_primary_model_here
GEMINI_FALLBACK_MODEL=your_fallback_model_here
USE_DOCKER=false
MAX_ATTEMPTS=3
LOW_TOKEN_MODE=true
```

> Never commit your real `.env` file or API key to GitHub.

### 5. Verify the Setup

```powershell
python check_setup.py
```

A successful setup should verify:

- Package imports
- Environment configuration
- Regression tests
- Sandbox behavior
- Gemini connectivity

---

## Run the Application

Start AegisGuard with:

```powershell
streamlit run app.py
```

Streamlit should open the application in your browser.

---

## Live Demo

### 🌐 Live Application

**Coming soon**

Replace this after deployment with your Streamlit deployment URL.

### 💻 GitHub Repository

https://github.com/habibaume2007-creator/AegisGuard

---

## Security Notes

AegisGuard distinguishes between trusted demonstration samples and uploaded third-party projects.

### Trusted Bundled Samples

Can use the complete workflow:

**Detect → Exploit → Confirm → Patch → Verify**

### Uploaded Third-Party Projects

When isolated sandboxing is unavailable:

**Upload → Safe Extraction → Static Analysis → Security Findings**

Unknown uploaded projects are not intended to be executed directly in local mode.

This reduces the risk of running untrusted source code.

---

## Future Roadmap

Planned improvements include:

- GitHub Pull Request integration
- CI/CD security integration
- Docker/cloud sandbox isolation
- Additional vulnerability classes
- Multi-language source-code analysis
- More advanced RAG
- Improved security memory
- Automated secure remediation workflows
- More advanced reporting
- Security policy integration

---

## Team

### AegisGuard Team

Developed for the **Final Term Hackathon — Aspire Pakistan Cohort 11**

| Member | Role |
|---|---|
| Team Leader | Agent workflow, backend integration, architecture |
| Team Member | UI/UX |
| Team Member | Testing / Documentation |
| Team Member | Presentation / Demo |

Replace these placeholders with your actual team members and roles.

---

## Security Philosophy

> **AI may propose the fix. Evidence should verify it. Humans should approve it.**

AegisGuard is built around the principle that AI can assist application security, but verification and human oversight should remain central to the remediation process.

---

## Final Vision

Traditional workflow:

**Detect → Alert → Manual Investigation**

AegisGuard workflow:

**Detect → Prove → Retrieve Security Knowledge → Generate Fix → Verify → Remember → Human Approves**

---

<div align="center">

# 🛡️ AegisGuard

### From vulnerability detection to verified remediation.

</div>
