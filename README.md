# **TriNetra: Autonomous Crisis Operations Engine**

**TriNetra** is a high-fidelity, multi-agent simulation environment built on the openenv framework. It serves as a rigorous testing ground for AI agents handling high-stakes disaster response scenarios.

## **🌍 Environment Overview and Motivation**

TriNetra is a high-fidelity, real-world OpenEnv simulation designed to evaluate autonomous AI agents on crisis triage, constrained resource allocation, and signal-vs-noise intelligence gathering.

Disaster response coordinators face severe cognitive load. They must parse conflicting IoT telemetry, satellite weather data, and limited resource pools to make life-or-death decisions while adhering to strict financial limits. This environment models the exact tasks a human Emergency Ops Director performs: filtering false-positive sensor data ("noise") from actual infrastructure failures ("signal") and deploying physical assets (boats, ambulances) within a strict $100,000 operational budget.

## **📡 Definitions of Action and Observation Spaces**

### **Observation Space**

The environment emits a strict Pydantic JSON state containing:

* task\_id: The current active task.  
* intelligence\_report: A text-based SITREP containing regional data and constraints.  
* telemetry\_data: Raw, localized sensor readings (e.g., wind speed, soil moisture, drainage capacity).  
* available\_resources: Exact counts of boats, ambulances, and food kits.  
* logistics\_budget: The rolling financial constraint (starting at $100,000).

### **Action Space**

The agent must reply with a strictly typed Pydantic JSON object:

* threat\_level: Classification (low, medium, high).  
* deploy\_region: The targeted geographical proper noun extracted from the SITREP.  
* budget\_scratchpad: Chain-of-Thought (CoT) mathematical reasoning proving the deployment costs (Boats: $5k, Ambulances: $2k, Food: $50) are \<= 100000\.  
* resource\_allocation: Dictionary mapping resources to deployment counts.  
* reasoning: A brief logical justification for the tactical action.

## **🎯 Task Descriptions with Expected Difficulty Levels**

This environment features 3 procedurally generated tasks spanning increasing difficulty. Each task utilizes a clear, deterministic, and reproducible programmatic grader that assigns scores between 0.0 and 1.0.

* **triage\_basic (Easy):** Evaluates if the agent can correctly classify a severe threat based on terrain and weather data (e.g., Mountain Landslide) and prioritize medical evacuation over heavy water equipment.  
* **resource\_allocation (Medium):** Evaluates spatial reasoning and constraint satisfaction. The agent must match specific resource types (boats vs. ambulances) to specific topological threats (Coastal Cyclone) without triggering a bankruptcy penalty (exceeding the $100k budget).  
* **signal\_vs\_noise (Hard):** Evaluates trap avoidance and adversarial data filtering. The agent receives blaring, high-urgency alerts from a region with safe weather data, alongside quiet telemetry showing critical drainage failure in another region. The agent must ignore the noise and deploy strictly to the true crisis.

## **📊 Baseline Performance Scores**

Baseline evaluation was conducted using the Multi-Agent Swarm architecture running on the Qwen/Qwen2.5-72B-Instruct model via the Hugging Face Inference API. The architecture decouples intelligence gathering (Agent Alpha) from logistical mathematics (Agent Beta).

| Task | Difficulty | Score (0.0 \- 1.0) |
| :---- | :---- | :---- |
| triage\_basic | Easy | **1.00** |
| resource\_allocation | Medium | **1.00** |
| signal\_vs\_noise | Hard | **1.00** |

*Note: The programmatic grader penalizes incorrect regions, improper resource matching, and budget overruns. The baseline model successfully navigated all constraints to achieve perfect reproducible scores across the procedural generations.*

## **🏗️ System Architecture & Mechanics**

To mitigate LLM hallucination and cognitive overload, TriNetra employs a Multi-Agent Swarm architecture.

* **Agent Alpha (Intelligence):** Filters sensor noise and outputs structured situational briefs.  
* **Agent Beta (Logistics):** Uses Chain-of-Thought mathematical scratchpads to calculate costs and deploy assets within budget.

The environment relies on a Procedural Generation Engine to synthesize variables (weather, topology, sensor failure) ensuring infinite replayability, preventing models from memorizing static benchmarks.

## **💻 Setup and Usage Instructions**

### **1\. Local Setup and Installation**

This project uses uv for fast, deterministic dependency resolution.

\# Clone the repository  
git clone \[https://github.com/username/trinetra.git\](https://github.com/username/trinetra.git)  
cd trinetra

\# Install uv if you haven't already  
pip install uv

\# Sync and install dependencies  
uv sync

### **2\. Configure Credentials**

Create a .env file in the root directory. *(Do not commit this file).*

HF\_TOKEN=your\_huggingface\_token  
MODEL\_NAME=Qwen/Qwen2.5-72B-Instruct  
API\_BASE\_URL=\[https://router.huggingface.co/v1\](https://router.huggingface.co/v1)

### **3\. Running the Environment**

Launch the backend engine and live WebSockets dashboard in your first terminal:

python \-m server.app

*Navigate to http://localhost:7860 to view the Live Telemetry UI.*

### **4\. Running Baseline Inference**

In a second terminal, execute the AI swarm to evaluate the model against the environment:

python inference.py

### **5\. Docker / Hugging Face Spaces Deployment**

The project is containerized for secure, non-root execution, explicitly tailored for Hugging Face Spaces.

\# Build the Docker image  
docker build \-t trinetra-engine .

\# Run the container (Exposed on port 7860 for HF Spaces)  
docker run \-p 7860:7860 \--env-file .env trinetra-engine

**Note:** The Grader's financial constraints are intentionally punishing. Overspending immediately results in a 0.0 score for the run to ensure only mathematically capable and logically sound models achieve mission success.