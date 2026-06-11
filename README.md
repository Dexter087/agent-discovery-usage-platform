# Agent Discovery and Usage Platform

## Overview

This is a simplified Agent Discovery and Usage platform built using Python and FastAPI. The system allows agents to be registered, searched, and tracked when one agent uses another agent. It uses simple in-memory storage to keep the implementation easy to understand and run locally.

## Features

- Add a new agent using `POST /agents`
- List all registered agents using `GET /agents`
- Search agents by name or description using `GET /search?q=...`
- Log usage between agents using `POST /usage`
- View total usage per target agent using `GET /usage-summary`
- Prevent duplicate usage counting using `request_id`
- Handle missing fields, unknown target agents, and invalid usage values
- Generate simple tags from agent descriptions without using an LLM

## Tech Stack

- Python
- FastAPI
- Uvicorn
- In-memory storage using Python dictionaries, lists, and sets

## How to Run Locally

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn main:app --reload
```

3. Open the FastAPI testing page in your browser:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### 1. Add Agent

`POST /agents`

Sample request:

```json
{
  "name": "DocParser",
  "description": "Extracts structured data from PDFs",
  "endpoint": "https://api.example.com/parse"
}
```

### 2. List Agents

`GET /agents`

Returns all registered agents.

### 3. Search Agents

`GET /search?q=pdf`

Searches agents by name or description. The search is case-insensitive.

### 4. Log Usage

`POST /usage`

Sample request:

```json
{
  "caller": "AgentA",
  "target": "DocParser",
  "units": 10,
  "request_id": "abc123"
}
```

If the same `request_id` is sent again, the system ignores the second request and does not count the usage again.

### 5. Usage Summary

`GET /usage-summary`

Sample response:

```json
{
  "usage_summary": {
    "DocParser": 10
  }
}
```

## Edge Cases Handled

- Missing fields return an error.
- Empty values return an error.
- Usage for an unknown target agent returns an error.
- Negative or zero usage units return an error.
- Duplicate `request_id` values are ignored to avoid double counting.

## Bonus: Simple Tag Generation

The system includes simple keyword extraction from the agent description. For example:

```text
Extracts structured data from PDFs
```

can generate tags such as:

```json
["extraction", "pdf"]
```

This is done using basic text processing instead of an LLM.

## Design Question 1: How would you extend this system to support billing without double charging?

To support billing, I would use `request_id` as an idempotency key for every billable request. Before adding a charge, the system would check whether the same `request_id` has already been processed. If it already exists, the system would return the previous result instead of creating a new charge. In a real system, billing records should be stored in a database with a unique constraint on `request_id`. This would prevent duplicate billing even if the same request is retried because of a network issue.

## Design Question 2: How would you store this data if scale increases to 100K agents?

If the system grows to 100K agents, I would move from in-memory storage to a database. Agents could be stored in an `agents` table, while usage records could be stored in a separate `usage_logs` table. I would add indexes on fields like agent name, description, and request ID to make search and duplicate checks faster. For better search, I would later use full-text search instead of simple string matching. Frequently used results could also be cached to reduce database load.
