"""
Code Analyzer Service - Analyzes code for metrics, structure, and issues.
"""

import ast
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """
    Static analysis utilities for Python and general code.
    Provides context enrichment before sending code to the LLM.
    """

    def detect_language(self, code: str, filename: str = "") -> str:
        """Detect programming language from filename or content heuristics."""
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".kt": "Kotlin",
            ".swift": "Swift",
            ".sh": "Bash",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
        }
        if filename:
            for ext, lang in ext_map.items():
                if filename.endswith(ext):
                    return lang

        # Heuristic detection
        if "def " in code and "import " in code:
            return "Python"
        if "function " in code or "const " in code or "let " in code:
            return "JavaScript"
        if "public class " in code or "System.out.println" in code:
            return "Java"

        return "Unknown"

    def extract_python_structure(self, code: str) -> dict:
        """
        Parse Python code and extract structural information.

        Returns:
            Dict with classes, functions, imports, and line count.
        """
        structure = {
            "classes": [],
            "functions": [],
            "imports": [],
            "line_count": len(code.splitlines()),
            "errors": [],
        }
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    structure["classes"].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    structure["functions"].append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            structure["imports"].append(alias.name)
                    else:
                        structure["imports"].append(node.module or "")
        except SyntaxError as e:
            structure["errors"].append(str(e))
            logger.warning(f"Syntax error while parsing Python code: {e}")
        return structure

    def count_complexity(self, code: str) -> int:
        """
        Estimate cyclomatic complexity by counting branch keywords.
        A rough heuristic — not a full AST-based calculation.
        """
        keywords = ["if ", "elif ", "else:", "for ", "while ", "try:", "except", "case "]
        return sum(code.count(kw) for kw in keywords)

    def extract_error_info(self, error_message: str) -> dict:
        """
        Parse a Python traceback or error message into structured components.

        Returns:
            Dict with error_type, line_number, and message.
        """
        info = {"error_type": None, "line_number": None, "message": error_message}

        # Match "ErrorType: message"
        type_match = re.search(r"(\w+Error|\w+Exception): (.+)", error_message)
        if type_match:
            info["error_type"] = type_match.group(1)
            info["message"] = type_match.group(2)

        # Match "line X"
        line_match = re.search(r"line (\d+)", error_message)
        if line_match:
            info["line_number"] = int(line_match.group(1))

        return info

    def get_code_summary(self, code: str, language: str) -> str:
        """
        Generate a brief textual summary of the code for context injection.
        """
        lines = code.splitlines()
        summary_parts = [
            f"Language: {language}",
            f"Lines: {len(lines)}",
        ]
        if language == "Python":
            structure = self.extract_python_structure(code)
            if structure["classes"]:
                summary_parts.append(f"Classes: {', '.join(structure['classes'])}")
            if structure["functions"]:
                summary_parts.append(f"Functions: {', '.join(structure['functions'])}")
            complexity = self.count_complexity(code)
            summary_parts.append(f"Estimated complexity: {complexity}")

        return " | ".join(summary_parts)


# Singleton instance
code_analyzer = CodeAnalyzer()
