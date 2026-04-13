# **TriNetra: Autonomous Crisis Operations Engine**

<p align="center">
  <img src="https://img.shields.io/badge/OpenEnv-Compliant-green" />
  <img src="https://img.shields.io/badge/Docker-Ready-blue" />
  <img src="https://img.shields.io/badge/Deploy-HuggingFace-orange" />
  <img src="https://img.shields.io/badge/Scoring-Deterministic-critical" />
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent-purple" />
</p>

<p align="center">
  <b>A high-fidelity multi-agent simulation for evaluating AI decision-making in high-stakes disaster response.</b>
</p>

<p align="center">
  🚀 <b>Live Demo:</b> <a href="https://huggingface.co/spaces/Anushka070426/TriNetra-Disaster-Ops">Try TriNetra in Action</a>
</p>

---

## 🌍 Overview

**TriNetra** is a precision-built, OpenEnv-compliant simulation environment designed to stress-test AI agents in real-world crisis scenarios.

It places agents in the role of an **Emergency Operations Director**, forcing them to cut through noisy, conflicting data streams—IoT telemetry, satellite inputs, and situational reports—to make **life-critical decisions under a strict $100,000 budget constraint**.

This isn’t just reasoning.  
It’s survival logic under pressure.

---

## 📡 Environment Specifications

### **Observation Space**

The environment emits a structured **Pydantic JSON state** containing:

- `task_id` — Active mission identifier  
- `intelligence_report` — High-level SITREP with regional context  
- `telemetry_data` — Raw sensor data (wind speed, soil moisture, drainage, etc.)  
- `available_resources` — Inventory (boats, ambulances, food kits)  
- `logistics_budget` — Remaining funds (initial: $100,000)

---

### **Action Space**

Agents must respond with a strictly typed JSON object:

- `threat_level` — Classification (`low`, `medium`, `high`)  
- `deploy_region` — Target geographical area extracted from SITREP  
- `budget_scratchpad` — Chain-of-Thought math ensuring total ≤ $100,000  
  - Unit Costs:
    - Boats: $5,000  
    - Ambulances: $2,000  
    - Food Kits: $50  
- `resource_allocation` — Mapping of resources to quantities  
- `reasoning` — Concise justification for decisions  

---

## 🎯 Task Descriptions

TriNetra includes three procedurally generated tasks with deterministic scoring (0.0 – 1.0):

1. **triage_basic (Easy)**  
   Classify threats using terrain and weather data, prioritizing correct response types.

2. **resource_allocation (Medium)**  
   Allocate resources optimally without exceeding budget constraints.

3. **signal_vs_noise (Hard)**  
   Identify critical low-signal threats while ignoring misleading high-noise data.

---

## 📊 Baseline Performance

**Model:** `Qwen/Qwen2.5-72B-Instruct`  
**Architecture:** Multi-Agent Swarm  

| Task | Difficulty | Score |
|------|----------|------|
| triage_basic | Easy | 1.00 |
| resource_allocation | Medium | 1.00 |
| signal_vs_noise | Hard | 1.00 |

> **Note:** Any budget violation results in an immediate **0.0 score**.

---

## 🏗️ System Architecture

- **Agent Alpha (Intelligence):** Filters noise and extracts critical insights  
- **Agent Beta (Logistics):** Performs cost-aware planning and deployment  
- **Procedural Engine:** Randomizes environment variables to prevent overfitting  

---

## 💻 Setup & Usage

### **1. Installation**

```bash
git clone https://github.com/username/trinetra.git
cd trinetra
pip install uv
uv sync
```

---

### **2. Configuration**

Create a `.env` file:

```env
HF_TOKEN=your_huggingface_token
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
API_BASE_URL=https://router.huggingface.co/v1
```

---

### **3. Running the Engine**

```bash
# Terminal 1: Start backend + UI
python -m server.app
```

Access dashboard at: http://localhost:7860

```bash
# Terminal 2: Run AI agents
python inference.py
```

---

### **4. Docker Deployment**

```bash
docker build -t trinetra-engine .
docker run -p 7860:7860 --env-file .env trinetra-engine
```

---

## 👥 Team

- **Vaibhav Sharma** — https://github.com/Nutricalboii  
- **Anushka Rawat** — https://github.com/Anushka130126  
- **Devesh Khurana** — https://github.com/DeveshKhurana1-oss  
