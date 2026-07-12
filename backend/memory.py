# ==========================================================
# Conversation Memory
#
# Stores recent conversations so the Answer Agent
# can answer follow-up questions.
#
# ==========================================================

from collections import deque


class ConversationMemory:

    def __init__(self, max_history=5, max_answer_chars=600):

        self.history = deque(maxlen=max_history)

        self.max_answer_chars = max_answer_chars

    # ======================================================
    # Add Conversation
    # ======================================================

    def add_message(self, question, answer):

        if len(answer) > self.max_answer_chars:

            stored_answer = answer[: self.max_answer_chars].rstrip() + " ...[truncated]"

        else:

            stored_answer = answer

        self.history.append({

            "question": question,

            "answer": stored_answer

        })

    # ======================================================
    # Get Conversation History
    # ======================================================

    def get_history(self):

        if not self.history:

            return ""

        conversation = ""

        for turn in self.history:

            conversation += (

                f"User: {turn['question']}\n"

                f"Assistant: {turn['answer']}\n\n"

            )

        return conversation

    # ======================================================
    # Clear Conversation
    # ======================================================

    def clear(self):

        self.history.clear()