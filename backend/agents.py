# ==========================================================
#
# Multi-Agent Orchestrator
#
# Agents
#
# 1. Router Agent
# 2. PDF Agent
# 3. Web Agent
# 4. Answer Agent
# 5. Citation Agent
#
# ==========================================================

import json
import time

from concurrent.futures import ThreadPoolExecutor

from tavily import TavilyClient

from langchain_google_genai import ChatGoogleGenerativeAI

from rag import RAGPipeline
from memory import ConversationMemory

from prompts import ROUTER_PROMPT, ANSWER_PROMPT

from config import GOOGLE_API_KEY, TAVILY_API_KEY, GEMINI_MODEL, TEMPERATURE


class AgentOrchestrator:

    def __init__(self):

        self.rag = RAGPipeline()

        self.uploaded_documents = sorted({

            parent["source"]

            for parent in self.rag.parent_store.values()

        })

        self.memory = ConversationMemory()

        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            timeout=120,
        )

        self.tavily = TavilyClient(api_key=TAVILY_API_KEY)

        self._executor = ThreadPoolExecutor(max_workers=2)

    # ======================================================
    # Safe Gemini Call
    # ======================================================
    

    RETRYABLE_MARKERS = (
        "timeout",
        "timed out",
        "connection",
        "503",
        "502",
        "500",
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
        "INTERNAL",
    )

    def _is_retryable(self, error_text):

        lowered = error_text.lower()

        return any(

            marker.lower() in lowered

            for marker in self.RETRYABLE_MARKERS

        )

    def invoke_llm(self, prompt):

        for attempt in range(3):

            try:

                start = time.time()

                response = self.llm.invoke(prompt)

                print(f"Gemini Response Time : {round(time.time()-start,2)} sec")

                return response

            except Exception as e:

                error_text = str(e)

                if "PerDay" in error_text or "GenerateRequestsPerDayPerProjectPerModel" in error_text:

                    
                    print(

                        "Gemini call failed — DAILY FREE-TIER QUOTA EXHAUSTED. "
                        "This will not succeed on retry until the quota resets "
                        "(or billing is enabled). See "
                        "https://ai.dev/usage?tab=rate-limit"
                    )

                    raise RuntimeError(

                        "Gemini daily free-tier quota exhausted for "
                        f"'{self.llm.model}'. Check "
                        "https://ai.dev/usage?tab=rate-limit or enable "
                        "billing to continue."
                    ) from e

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:

                    print(

                        f"Gemini Attempt {attempt+1} Failed — RATE LIMIT / QUOTA "
                        f"EXCEEDED (429). This is a Google API quota issue, not a "
                        f"pipeline bug. Check https://ai.dev/usage?tab=rate-limit "
                        f"and https://ai.google.dev/gemini-api/docs/rate-limits"
                    )

                else:

                    print(f"Gemini Attempt {attempt+1} Failed: {error_text}")

               
                if not self._is_retryable(error_text):

                    print(

                        "Gemini call failed with a non-retryable error — "
                        "failing immediately instead of retrying."
                    )

                    raise e

                if attempt == 2:

                    raise e

                time.sleep(1.5)

    # ======================================================
    # Router Agent
    # ======================================================

    def router_agent(self, query, use_web=True):

        print("\n🧠 Router Agent")

        # ------------------------------------------
        # No PDFs uploaded
        # ------------------------------------------

        if len(self.uploaded_documents) == 0:

            if use_web:

                return {
                    "pdf_agent": False,
                    "web_agent": True,
                    "reason": "No PDF uploaded. Searching the web."
                }

            return {
                "pdf_agent": False,
                "web_agent": False,
                "reason": "No PDF uploaded and web search disabled."
            }

        # ------------------------------------------
        # User enabled Web Search
        # ------------------------------------------

        if use_web:

            return {
                "pdf_agent": True,
                "web_agent": True,
                "reason": "User enabled live web search."
            }

        # ------------------------------------------
        # Default
        # ------------------------------------------

        return {
            "pdf_agent": True,
            "web_agent": False,
            "reason": "Using uploaded PDFs only."
        }


    # ======================================================
    # PDF Agent
    # ======================================================

    def pdf_agent(self, query):

        print("\n📄 PDF Agent Activated")

        context, results = self.rag.retrieve_context(query)

        # Get unique PDF sources from retrieved child chunks
        sources = sorted({

            metadata["source"]

            for metadata in results["metadatas"][0]

        })

        print("\nRetrieved Sources:")

        for meta in results["metadatas"][0]:
            print(meta["source"])

        return {

            "context": context,

            "results": results,

            "sources": sources

        }


    # ======================================================
    # Web Agent
    # ======================================================


    def web_agent(self, query):

        print("\n🌐 Web Agent Activated")

        try:

            results = self.tavily.search(query=query, max_results=3)

        except Exception as e:

            print("Tavily Error:", e)

            return {"context": "", "sources": []}

        web_context = ""

        web_sources = []

        for item in results["results"]:

            web_context += f"Title : {item['title']}\n"

            web_context += item["content"]

            web_context += "\n\n"

            web_sources.append({"title": item["title"], "url": item["url"]})

        return {"context": web_context, "sources": web_sources}
    


    # ======================================================
    # Answer Agent
    # ======================================================

    def answer_agent(
        self,
        query,
        pdf_output,
        web_output,
        conversation_history
    ):

        print("\n🤖 Answer Agent Activated")

        prompt = ANSWER_PROMPT.format(

            conversation_history=conversation_history,

            query=query,

            pdf_context=pdf_output["context"],

            web_context=web_output["context"]

        )

        print("=" * 60)
        print(f"Prompt chars      : {len(prompt)}")
        print(f"PDF context chars : {len(pdf_output['context'])}")
        print(f"Web context chars : {len(web_output['context'])}")
        print(f"History chars     : {len(conversation_history)}")
        print("=" * 60)

       
        
        response = self.invoke_llm(prompt)

        answer = response.content

        # If Gemini returns a list instead of plain text
        if isinstance(answer, list):

            final_answer = ""

            for item in answer:

                if isinstance(item, dict):
                    final_answer += item.get("text", "")

            answer = final_answer

        return {
            "answer": answer
        }


    # ======================================================
    # Citation Agent
    # ======================================================

    def citation_agent(

        self,

        pdf_output,

        web_output

    ):

        print("\n📚 Citation Agent Activated")

        return {

            "pdf_sources": pdf_output["sources"],

            "web_sources": web_output["sources"]

        }
    

    # ======================================================
    # Main Orchestrator
    # ======================================================
    
    def run(self, question, use_web=True):

        query = question

        print("\n🚀 Starting Multi-Agent Pipeline")

        decision = self.router_agent(query, use_web=use_web)

        pdf_output = {

            "context": "",

            "results": None,

            "sources": []

        }

        web_output = {

            "context": "",

            "sources": []

        }

        # --------------------------
        # PDF Agent + Web Agent (parallel)
        # --------------------------

        pdf_future = None
        web_future = None

        if decision["pdf_agent"]:

            pdf_future = self._executor.submit(self.pdf_agent, query)

        if decision["web_agent"]:

            web_future = self._executor.submit(self.web_agent, query)

        if pdf_future is not None:

            pdf_output = pdf_future.result()

        if web_future is not None:

            web_output = web_future.result()

        # --------------------------
        # Conversation Memory
        # --------------------------

        history = self.memory.get_history()

        # --------------------------
        # Final Answer
        # --------------------------

        answer = self.answer_agent(

            query,

            pdf_output,

            web_output,

            history

        )

        self.memory.add_message(

            query,

            answer["answer"]

        )

        references = self.citation_agent(

            pdf_output,

            web_output

        )

        pdf_output = None
        web_output = None

        import gc
        gc.collect()

        print("\n✅ Pipeline Finished")

        return {

            "status": "success",

            "question": query,

            "answer": answer["answer"],

            "references": references,

            "used_pdf": decision["pdf_agent"],

            "used_web": decision["web_agent"],

            "router_reason": decision["reason"]

        }