from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ReportSynthesizer:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)

    def synthesize_report(self, all_findings: list) -> dict:
        """
        Aggregates findings from all agents and produces a unified report.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a code review synthesizer. Given findings from multiple specialized agents (Context, Diff, Security),
            produce a unified report:
            1. Overall PR health score (0-100)
            2. Risk level (LOW/MEDIUM/HIGH/CRITICAL)
            3. Severity-ranked findings with:
               - Confidence scores
               - File + line number
               - Suggested fixes
            
            Output as JSON:
            {{
              "overall_score": 85,
              "risk_level": "MEDIUM",
              "findings": [...],
              "agent_chain": [
                {{"agent": "Context Collector", "reasoning": "..."}},
                ...
              ]
            }}"""),
            ("user", "Findings:\n{findings}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"findings": json.dumps(all_findings, indent=2)})

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            report = json.loads(content)
        except Exception as e:
            print(f"Error parsing ReportSynthesizer response: {e}")
            # Fallback report
            report = {
                "overall_score": 0,
                "risk_level": "UNKNOWN",
                "findings": all_findings,
                "agent_chain": []
            }

        # Double check overall score calculation if LLM didn't provide a good one
        if "overall_score" not in report or report["overall_score"] == 0:
            critical_count = len([f for f in all_findings if f.get("severity") == "CRITICAL"])
            high_count = len([f for f in all_findings if f.get("severity") == "HIGH"])
            score = max(0, 100 - (critical_count * 30) - (high_count * 15))
            report["overall_score"] = score
            report["risk_level"] = "CRITICAL" if critical_count > 0 else ("HIGH" if high_count > 0 else "MEDIUM")

        return report

if __name__ == "__main__":
    # synthesizer = ReportSynthesizer()
    # print(synthesizer.synthesize_report([]))
    pass
