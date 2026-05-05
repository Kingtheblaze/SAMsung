# ContextDiff 🔍
> AI-powered code review that understands *intent*, not just syntax.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## What is ContextDiff?

ContextDiff is a **multi-agent AI system** that performs deep Pull Request reviews by:
- Reading your entire repository (README, architecture docs, past commits)
- Parsing diffs at the AST level to detect behavioral contract violations
- Mapping security risks to OWASP Top 10 with confidence scores
- Posting structured findings as GitHub inline comments

**Unlike traditional linters**, ContextDiff understands *why* code was written a certain way and flags changes that break documented contracts.

## Architecture

1. **Agent 1: Context Collector**: Fetches README, Architecture docs, and related files via call graph to build a semantic map.
2. **Agent 2: Diff Analyzer**: Parses AST trees to detect behavioral contract violations (e.g., signature changes, return type shifts).
3. **Agent 3: Security Auditor**: Uses RAG over OWASP knowledge base to flag vulnerabilities with high confidence.
4. **Agent 4: Report Synthesizer**: Aggregates findings and generates a unified health score and inline GitHub comments.

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **AI**: Claude 3.5 Sonnet via Anthropic API
- **Agents**: LangChain + LangGraph
- **AST**: tree-sitter
- **Vector Store**: ChromaDB
- **Frontend**: React + Vite + Tailwind CSS + shadcn/ui

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```bash
ANTHROPIC_API_KEY=your_key
GITHUB_TOKEN=your_token
```

## Team
Built by **Team Gen AI** for the Gen AI Research track.
