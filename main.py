from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import arxiv
import os
from agents import ResearchAgents
from generator import generate_markdown_report, generate_presentation

# 1. CREATE THE APP FIRST (This fixes the error)
app = FastAPI()

# 2. CREATE FOLDER
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# 3. CONFIGURE MIDDLEWARE (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. MOUNT STATIC FILES (For downloads)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# 5. INITIALIZE AGENTS
# Remember to replace this with your actual key!
agents = ResearchAgents(api_key="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")

db = {} # Simple in-memory storage

@app.post("/research")
async def start_research(topic: str, background_tasks: BackgroundTasks):
    job_id = len(db) + 1
    db[job_id] = {"status": "searching", "topic": topic}
    background_tasks.add_task(run_research_pipeline, job_id, topic)
    return {"job_id": job_id, "message": "Research started!"}

async def run_research_pipeline(job_id, topic):
    try:
        # Search ArXiv
        search = arxiv.Search(query=topic, max_results=3)
        summaries = []
        for result in search.results():
            summary = agents.summarize_paper(result.summary)
            summaries.append(summary)
        
        # Analyze and Generate
        trends = agents.analyze_trends(summaries)
        report = generate_markdown_report(topic, trends, summaries)
        
        ppt_filename = f"presentation_{job_id}.pptx"
        ppt_url_path = generate_presentation(topic, trends, ppt_filename)
        
        db[job_id].update({
            "status": "completed",
            "report": report,
            "ppt_url": f"/outputs/{ppt_filename}"
        })
    except Exception as e:
        db[job_id] = {"status": "error", "message": str(e)}

@app.get("/status/{job_id}")
async def get_status(job_id: int):
    return db.get(job_id, {"error": "Job not found"})