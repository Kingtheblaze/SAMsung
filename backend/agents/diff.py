from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import json
import os
from dotenv import load_dotenv

load_dotenv()

class DiffAnalyzer:
    def __init__(self):
        self.PY_LANGUAGE = Language(tspython.language())
        self.parser = Parser(self.PY_LANGUAGE)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    def parse_ast(self, code: str):
        if not code:
            return ""
        tree = self.parser.parse(bytes(code, "utf8"))
        return tree.root_node.sexp()

    def analyze_diff(self, diff: str, context: dict) -> list:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AST-level code reviewer. Given:
            1. The code diff (text-based)
            2. Repository context (architecture docs, related files)
            
            Detect behavioral contract violations:
            - Function signature changes (params added/removed)
            - Return type changes (throws → null, object → primitive)
            - Call graph mutations (new dependencies, removed calls)
            
            For each finding, output as JSON:
            {{
              "severity": "CRITICAL|HIGH|MEDIUM|LOW",
              "confidence": 0-100,
              "category": "BehavioralContractViolation",
              "file": "path/to/file.py",
              "line": 142,
              "message": "getUserById() now returns null instead of raising UserNotFoundError, breaking 3 downstream callers."
            }}
            
            Output a list of findings in JSON format."""),
            ("user", "Diff:\n{diff}\n\nContext:\n{context}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "diff": diff,
            "context": json.dumps(context.get("related_content", {}), indent=2)
        })

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            findings = json.loads(content)
            if not isinstance(findings, list):
                findings = [findings]
        except Exception as e:
            print(f"Error parsing DiffAnalyzer response: {e}")
            findings = []

        return findings
