import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field

# --- 1. SEARCH TOOL ---
class SatyaSearchTool(BaseTool):
    name: str = "Internet Search"
    description: str = "Search the web."

    def _run(self, query: str) -> str:
        print(f"\n🔎 SEARCHING: {query}") 
        try:
            with DDGS() as ddgs:
                # Fetch 6 results to give the 70B model plenty of context
                results = list(ddgs.text(query, max_results=6))
            if not results: return "No results found."
            return str(results)
        except Exception as e:
            return f"Error: {e}"

search_tool = SatyaSearchTool()

# --- 2. LLM SETUP (Using env var for security) ---
llm_groq = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0,
    # 🚨 CRITICAL FIX: Add a long timeout for network stability
    request_timeout=45, 
    # SECURE: Reads from the .env file (or terminal export)
    api_key=os.getenv("GROQ_API_KEY") 
)

# --- 3. OUTPUT FORMAT ---
class SatyaScore(BaseModel):
    claim_summary: str = Field(..., description="Short summary of facts.")
    verdict: str = Field(..., description="'VERIFIED' or 'MISINFORMATION'.")
    trust_score: int = Field(..., description="0-100 score.")
    evidence: list[str] = Field(..., description="Extract 2-3 http links.")

# --- 4. AGENTS ---
triage_agent = Agent(
    role="Intake Officer",
    goal="Pass everything to the verifier.",
    backstory="You are the intake officer. You pass all claims forward.",
    llm=llm_groq,
    verbose=True
)

verifier_agent = Agent(
    role="Benevolent Investigator",
    goal="Find evidence that SUPPORTS the user's claim.",
    backstory="You are a helpful researcher. You know users make typos or use loose language (like 'banned' instead of 'withdrawn'). Your job is to verify the CORE EVENT, not nitpick words.",
    tools=[search_tool],
    llm=llm_groq,
    verbose=True
)

# --- 5. TASKS (BENEVOLENT INSTRUCTIONS) ---
triage_task = Task(
    description="Analyze '{input_claim}'. Extract the search query.",
    agent=triage_agent,
    expected_output="Search query string."
)

verification_task = Task(
    description=(
        "1. SEARCH: '{input_claim}'.\n"
        "2. ANALYZE: Look for the core event. \n"
        "   - Example: If user says 'RBI banned 2000 notes' and news says 'RBI withdraws 2000 notes', that is a MATCH.\n"
        "   - Example: If user says 'Chandrayaan landed' and news confirms it, that is a MATCH.\n"
        "3. SCORING RULE: \n"
        "   - If the event basically happened: Score **100** (VERIFIED).\n"
        "   - Only give **0** (MISINFORMATION) if it is a complete hoax.\n"
        "4. EVIDENCE: Copy URLs."
    ),
    agent=verifier_agent,
    context=[triage_task],
    output_pydantic=SatyaScore,
    expected_output="A SatyaScore object."
)

# --- 6. CREW ---
satya_crew = Crew(
    agents=[triage_agent, verifier_agent],
    tasks=[triage_task, verification_task],
    process=Process.sequential
)

def run_satya_scan(claim_text):
    try:
        result = satya_crew.kickoff(inputs={'input_claim': claim_text})
        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic.dict()
        elif hasattr(result, 'to_dict'):
             return result.to_dict()
        return result
    except Exception as e:
        return {"error": str(e)}