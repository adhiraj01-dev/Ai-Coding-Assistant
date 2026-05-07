"""
AI Agent - Understands user intent and routes to the correct service.
Follows the Analyze → Retrieve → Reason → Respond pipeline.
"""

import logging
import re
from enum import Enum
from services.llm_service import llm_service
from services.code_analyzer import code_analyzer
from rag.retrieve import retriever

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    DEBUG = "debug"
    EXPLAIN = "explain"
    GENERATE = "generate"
    REFACTOR = "refactor"
    TEST = "test"
    OPTIMIZE = "optimize"
    QUERY = "query"


class Agent:
    """
    Central AI agent that:
    1. Detects user intent from message
    2. Retrieves relevant context via RAG
    3. Routes to appropriate prompt strategy
    4. Returns structured response
    """

    INTENT_PATTERNS = {
        Intent.DEBUG: [
            r"fix", r"error", r"bug", r"traceback", r"exception",
            r"crash", r"broken", r"debug", r"not working", r"fails",
        ],
        Intent.EXPLAIN: [
            r"explain", r"what does", r"how does", r"understand",
            r"what is", r"describe", r"walk me through",
        ],
        Intent.GENERATE: [
            r"generate", r"create", r"write", r"make", r"build",
            r"implement", r"add", r"new function", r"new class",
        ],
        Intent.REFACTOR: [
            r"refactor", r"clean up", r"improve", r"rename",
            r"restructure", r"simplify", r"reorganize",
        ],
        Intent.TEST: [
            r"test", r"unit test", r"pytest", r"spec", r"test case",
            r"edge case", r"coverage",
        ],
        Intent.OPTIMIZE: [
            r"optimize", r"performance", r"slow", r"faster", r"efficient",
            r"speed up", r"bottleneck", r"memory",
        ],
    }

    def detect_intent(self, message: str) -> Intent:
        """
        Detect the user's intent using keyword pattern matching.
        Falls back to general QUERY if no pattern matches.
        """
        message_lower = message.lower()
        scores = {intent: 0 for intent in Intent}

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    scores[intent] += 1

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            logger.info("No intent pattern matched, defaulting to QUERY")
            return Intent.QUERY

        logger.info(f"Detected intent: {best} (score: {scores[best]})")
        return best

    def build_context(self, query: str, code: str = "") -> str:
        """
        Build context string by retrieving relevant code snippets via RAG.
        """
        context_parts = []

        # RAG retrieval from ingested codebase
        try:
            rag_results = retriever.retrieve(query, top_k=3)
            if rag_results:
                context_parts.append("=== Relevant code from your codebase ===")
                for result in rag_results:
                    context_parts.append(f"File: {result['source']}\n{result['content']}")
        except Exception as e:
            logger.warning(f"RAG retrieval failed (codebase may not be ingested yet): {e}")

        # Add directly provided code
        if code.strip():
            lang = code_analyzer.detect_language(code)
            summary = code_analyzer.get_code_summary(code, lang)
            context_parts.append(f"=== Provided code ({summary}) ===\n{code}")

        return "\n\n".join(context_parts) if context_parts else ""

    def run(
        self,
        message: str,
        code: str = "",
        intent_override: Intent = None,
        explain_level: str = "intermediate",
        memory: list = None,
    ) -> dict:
        """
        Main agent entry point.

        Args:
            message: User's natural language query.
            code: Optional code snippet provided by user.
            intent_override: Force a specific intent (used by dedicated endpoints).
            explain_level: Explanation depth (beginner/intermediate/expert).
            memory: Prior conversation turns for context.

        Returns:
            Dict with intent, response, and any extracted code blocks.
        """
        intent = intent_override or self.detect_intent(message)
        context = self.build_context(message, code)

        logger.info(f"Agent running with intent={intent}")

        system_prompt = self._get_system_prompt(intent, explain_level)
        user_message = self._build_user_message(message, code, context, intent)

        # Inject memory if available
        if memory:
            messages = [{"role": "system", "content": system_prompt}]
            for turn in memory[-6:]:  # last 3 exchanges
                messages.append({"role": "user", "content": turn["user"]})
                messages.append({"role": "assistant", "content": turn["assistant"]})
            messages.append({"role": "user", "content": user_message})
            response_text = llm_service.chat_with_history(messages)
        else:
            response_text = llm_service.chat(system_prompt, user_message)

        code_blocks = self._extract_code_blocks(response_text)

        return {
            "intent": intent.value,
            "response": response_text,
            "code_blocks": code_blocks,
        }

    def _get_system_prompt(self, intent: Intent, explain_level: str) -> str:
        """Return intent-specific system prompt."""
        base = (
            "You are an expert AI coding assistant embedded in a developer's IDE. "
            "You are precise, helpful, and always provide working code examples. "
            "Format code in markdown code blocks with language identifiers."
        )

        prompts = {
            Intent.DEBUG: (
                base + "\n\nYour task is to debug code. Always structure your response as:\n"
                "1. **Simple Explanation** - What went wrong in plain English\n"
                "2. **Root Cause** - Technical explanation of why it happened\n"
                "3. **Fixed Code** - The corrected code snippet\n"
                "4. **Prevention** - How to avoid this in future"
            ),
            Intent.EXPLAIN: (
                base + f"\n\nExplain code at the **{explain_level}** level.\n"
                "- Beginner: Use analogies, avoid jargon, step-by-step\n"
                "- Intermediate: Technical but conversational, mention patterns\n"
                "- Expert: Deep dive into implementation, complexity, tradeoffs"
            ),
            Intent.GENERATE: (
                base + "\n\nGenerate clean, production-ready code. Include:\n"
                "- Docstrings and type hints\n"
                "- Error handling\n"
                "- Example usage in comments"
            ),
            Intent.REFACTOR: (
                base + "\n\nRefactor the provided code. Show:\n"
                "1. What you changed and why\n"
                "2. The refactored code\n"
                "3. Key improvements made"
            ),
            Intent.TEST: (
                base + "\n\nGenerate comprehensive unit tests. Include:\n"
                "- Happy path tests\n"
                "- Edge cases\n"
                "- Error/exception tests\n"
                "- Use pytest format"
            ),
            Intent.OPTIMIZE: (
                base + "\n\nOptimize the provided code. Show:\n"
                "1. Performance issues identified\n"
                "2. Time/space complexity analysis\n"
                "3. Optimized version with explanation"
            ),
            Intent.QUERY: base,
        }
        return prompts.get(intent, base)

    def _build_user_message(
        self, message: str, code: str, context: str, intent: Intent
    ) -> str:
        """Compose the full user message with context injection."""
        parts = []
        if context:
            parts.append(f"CONTEXT:\n{context}\n")
        parts.append(f"QUERY: {message}")
        if code and not context:  # avoid duplication if code already in context
            parts.append(f"\nCODE:\n```\n{code}\n```")
        return "\n".join(parts)

    def _extract_code_blocks(self, text: str) -> list[str]:
        """Extract all fenced code blocks from a markdown response."""
        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [m.strip() for m in matches]


# Singleton instance
agent = Agent()
