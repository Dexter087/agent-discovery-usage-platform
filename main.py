from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re


app = FastAPI(title="Agent Discovery and Usage Platform")


# In-memory storage
agents = {}
usage_logs = []
usage_summary = {}
processed_request_ids = set()


class AgentInput(BaseModel):
    name: str
    description: str
    endpoint: str


class UsageInput(BaseModel):
    caller: str
    target: str
    units: int
    request_id: str


def extract_tags(description):
    """
    Simple keyword extraction without using an LLM.
    """
    stopwords = {
        "the", "a", "an", "and", "or", "to", "from", "of", "in", "on",
        "for", "with", "data", "structured"
    }

    words = re.findall(r"[a-zA-Z0-9]+", description.lower())
    tags = []

    for word in words:
        if word in stopwords:
            continue

        if word in ["pdf", "pdfs"]:
            tag = "pdf"
        elif word in ["extract", "extracts", "extraction", "extracting"]:
            tag = "extraction"
        elif word in ["summarize", "summarizes", "summary", "summarization"]:
            tag = "summarization"
        else:
            tag = word

        if tag not in tags:
            tags.append(tag)

    return tags


@app.get("/")
def home():
    return {
        "message": "Agent Discovery and Usage Platform is running.",
        "docs": "Open /docs to test the API."
    }


@app.post("/agents")
def add_agent(agent_input: AgentInput):
    name = agent_input.name.strip()
    description = agent_input.description.strip()
    endpoint = agent_input.endpoint.strip()

    if name == "" or description == "" or endpoint == "":
        raise HTTPException(
            status_code=400,
            detail="Name, description, and endpoint cannot be empty."
        )

    if name in agents:
        raise HTTPException(
            status_code=400,
            detail="Agent already exists."
        )

    agent = {
        "name": name,
        "description": description,
        "endpoint": endpoint,
        "tags": extract_tags(description)
    }

    agents[name] = agent

    return {
        "message": "Agent added successfully.",
        "agent": agent
    }


@app.get("/agents")
def list_agents():
    return {
        "agents": list(agents.values())
    }


@app.get("/search")
def search_agents(q: str):
    query = q.lower()
    results = []

    for agent in agents.values():
        name_match = query in agent["name"].lower()
        description_match = query in agent["description"].lower()

        if name_match or description_match:
            results.append(agent)

    return {
        "query": q,
        "results": results
    }


@app.post("/usage")
def log_usage(usage_input: UsageInput):
    caller = usage_input.caller.strip()
    target = usage_input.target.strip()
    request_id = usage_input.request_id.strip()
    units = usage_input.units

    if caller == "" or target == "" or request_id == "":
        raise HTTPException(
            status_code=400,
            detail="Caller, target, and request_id cannot be empty."
        )

    if units <= 0:
        raise HTTPException(
            status_code=400,
            detail="Units must be a positive integer."
        )

    if target not in agents:
        raise HTTPException(
            status_code=404,
            detail="Target agent does not exist."
        )

    if request_id in processed_request_ids:
        return {
            "message": "Duplicate request_id. Usage was not counted again."
        }

    processed_request_ids.add(request_id)

    usage_record = {
        "caller": caller,
        "target": target,
        "units": units,
        "request_id": request_id
    }

    usage_logs.append(usage_record)

    if target not in usage_summary:
        usage_summary[target] = 0

    usage_summary[target] += units

    return {
        "message": "Usage logged successfully.",
        "usage": usage_record
    }


@app.get("/usage-summary")
def get_usage_summary():
    return {
        "usage_summary": usage_summary
    }
