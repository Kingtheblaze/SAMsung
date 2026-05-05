from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

from backend.agents.context import ContextCollector
from backend.agents.diff import DiffAnalyzer
from backend.agents.security import SecurityAuditor
from backend.agents.synthesis import ReportSynthesizer
from backend.utils.github_client import GitHubClient
import json

app = FastAPI(title="ContextDiff")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
context_collector = ContextCollector()
diff_analyzer = DiffAnalyzer()
security_auditor = SecurityAuditor()
report_synthesizer = ReportSynthesizer()
github_client = GitHubClient()

# Store reports in memory for hackathon demo
reports = {}
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

async def run_pipeline(pr_url: str):
    print(f"Starting pipeline for {pr_url} (Mock Mode: {MOCK_MODE})")
    
    pr_id = pr_url.split("/")[-1]
    
    if MOCK_MODE:
        import asyncio
        await asyncio.sleep(3)
        report = {
            "overall_score": 72,
            "risk_level": "MEDIUM",
            "findings": [
                {
                    "severity": "HIGH",
                    "confidence": 91,
                    "category": "OWASP-A03:Injection",
                    "file": "src/api/user_service.py",
                    "line": 45,
                    "message": "Raw SQL query detected. Potential SQL injection via user input.",
                    "fix": "Use parameterized queries or an ORM like SQLAlchemy."
                },
                {
                    "severity": "MEDIUM",
                    "confidence": 78,
                    "category": "BehavioralContractViolation",
                    "file": "src/auth/manager.py",
                    "line": 122,
                    "message": "Function validate_token() now returns None instead of throwing AuthError, breaking 2 downstream callers.",
                    "fix": "Update callers to handle None or restore the exception throwing behavior."
                }
            ],
            "agent_chain": [
                {"agent": "Context Collector", "reasoning": "Identified database access layer and authentication modules as high-risk areas."},
                {"agent": "Diff Analyzer", "reasoning": "Detected signature change in validate_token() that deviates from documented ARCHITECTURE.md contract."},
                {"agent": "Security Auditor", "reasoning": "Flagged raw string formatting in SQL query as a potential OWASP-A03 violation."}
            ]
        }
        reports[pr_id] = report
        print(f"Mock report generated for PR {pr_id}")
        return

    # 1. Fetch Diff
    diff = github_client.fetch_pr_diff(pr_url)
    if not diff:
        print("Failed to fetch diff")
        return

    # 2. Collect Context
    context = context_collector.collect_context(pr_url, diff)
    
    # 3. Analyze Diff & Audit Security
    diff_findings = diff_analyzer.analyze_diff(diff, context)
    security_findings = security_auditor.audit_security(diff)
    
    # 4. Synthesize Report
    all_findings = diff_findings + security_findings
    report = report_synthesizer.synthesize_report(all_findings)
    
    # Store report
    reports[pr_id] = report
    print(f"Report generated for PR {pr_id}: {report['overall_score']}/100")

@app.get("/")
async def root():
    return {"message": "ContextDiff API is running"}

@app.get("/api/reviews/{pr_id}")
async def get_review(pr_id: str):
    return reports.get(pr_id, {"status": "not_found"})

@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    action = payload.get("action")
    
    if action in ["opened", "synchronize", "reopened"]:
        pr_data = payload.get("pull_request")
        if pr_data:
            pr_url = pr_data.get("url")
            background_tasks.add_task(run_pipeline, pr_url)
            return {"status": "processing", "pr": pr_url}
            
    return {"status": "ignored", "action": action}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
