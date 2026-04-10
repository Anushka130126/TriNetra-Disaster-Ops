<h1 align="center">TriNetra: Autonomous Crisis Operations Engine</h1>

<p align="center">
  <img src="https://img.shields.io/badge/OpenEnv-Compliant-green" />
  <img src="https://img.shields.io/badge/Docker-Ready-blue" />
  <img src="https://img.shields.io/badge/Deploy-HuggingFace-orange" />
  <img src="https://img.shields.io/badge/Scoring-Deterministic-critical" />
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent-purple" />
</p>

<p align="center">
  A structured environment for evaluating AI decision-making in high-stakes disaster response scenarios
</p>

---

## Overview

TriNetra is a high-fidelity OpenEnv environment designed to evaluate how AI agents make decisions in disaster response scenarios involving uncertainty, limited resources, and conflicting signals.

The environment models real-world crisis operations where agents must distinguish signal from noise and allocate resources under strict constraints. The focus is on evaluating decision processes across multiple steps, not isolated outputs.

---

## Environment Motivation

Disaster response coordinators operate under severe cognitive load:

- Multiple data sources (IoT telemetry, weather signals, reports) may conflict  
- Infrastructure conditions evolve rapidly  
- Resource pools are limited  
- Decisions must be made under strict financial constraints  

TriNetra models the role of an Emergency Operations Director by:

- filtering false-positive sensor data ("noise") from real failures ("signal")  
- deploying physical assets such as boats and ambulances  
- operating within a fixed budget of 100,000  

---

## Observation Space

The environment emits a structured Pydantic JSON state:

- `task_id` — current task  
- `intelligence_report` — situational summary (SITREP)  
- `telemetry_data` — localized sensor data (weather, terrain, drainage)  
- `available_resources` — boats, ambulances, food kits  
- `logistics_budget` — financial constraint (starting at 100,000)  

---

## Action Space

The agent must return a structured Pydantic JSON response:

- `threat_level` — low / medium / high  
- `deploy_region` — region extracted from SITREP  
- `budget_scratchpad` — cost calculation (Boats: 5k, Ambulances: 2k, Food: 50)  
- `resource_allocation` — deployment plan  
- `reasoning` — concise justification  

---

## Tasks

TriNetra includes three procedurally generated tasks with deterministic grading:

### triage_basic (Easy)
- Classify threat using terrain and weather data  
- Prioritize appropriate response  

### resource_allocation (Medium)
- Match resources to scenario  
- Stay within strict budget constraints  

### signal_vs_noise (Hard)
- Filter misleading high-urgency alerts  
- Identify subtle but critical failures  
- Deploy resources only to the true crisis  

---

## Evaluation

Scores range from **0.0 to 1.0**, based on:

- threat classification accuracy  
- resource allocation correctness  
- adherence to budget constraints  
- ability to distinguish signal from noise  

### Constraints

- incorrect region → penalty  
- incorrect resource → penalty  
- exceeding budget → score = 0.0  

---

## Baseline Performance

Model: `Qwen/Qwen2.5-72B-Instruct`  
Execution: Hugging Face Inference API  

| Task | Difficulty | Score |
|------|-----------|------|
| triage_basic | Easy | 1.00 |
| resource_allocation | Medium | 1.00 |
| signal_vs_noise | Hard | 1.00 |

Results are deterministic and reproducible.

---

## System Architecture

TriNetra uses a Multi-Agent Swarm architecture:

- **Agent Alpha (Intelligence):** filters signals and extracts relevant insights  
- **Agent Beta (Logistics):** performs cost-aware reasoning and deployment  

### Procedural Generation Engine

- dynamically generates scenarios  
- varies weather, terrain, and sensor conditions  
- prevents memorization of static benchmarks  

---

## Setup

### Clone Repository
git clone https://github.com/username/trinetra.git
cd trinetra


---

### Install Dependencies
pip install uv
uv sync


---

### Configure Environment

Create a `.env` file:
HF_TOKEN=your_huggingface_token
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
API_BASE_URL=https://router.huggingface.co/v1


---

## Run Environment
python -m server.app


Open in browser:
http://localhost:7860


---

## Run Inference
python inference.py


---

## Docker Deployment
docker build -t trinetra-engine .
docker run -p 7860:7860 --env-file .env trinetra-engine


---

## Repository Structure
app/ environment logic and grader
frontend/ dashboard interface
server/ backend service
inference.py evaluation script
openenv.yaml environment specification
Dockerfile container setup


---

## Design Focus

TriNetra evaluates:

- decision-making under uncertainty  
- filtering conflicting signals  
- resource prioritization under constraints  
- consistency across sequential steps  

---

## Notes

- scoring is deterministic  
- evaluation is reproducible  
- financial constraints are strictly enforced  

---

## Team

<p align="left">
  <b>Vaibhav Sharma</b><br>
  <a href="https://github.com/Nutricalboii">Nutricalboii</a>
</p>

<br>

<p align="leftr">
  <b>Anushka Rawat</b><br>
  <a href="https://github.com/Anushka130126">Anushka130126</a>
</p>

<br>

<p align="left">
  <b>Devesh Khurana</b><br>
  <a href="https://github.com/DeveshKhurana1-oss">DeveshKhurana1-oss</a>
</p>
