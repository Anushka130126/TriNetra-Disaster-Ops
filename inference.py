import os
import json
import time
import textwrap
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load the secret keys
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

TASKS = ["triage_basic", "resource_allocation", "signal_vs_noise"]
BENCHMARK = "disaster-response-ops"
MAX_STEPS = 3
SERVER_URL = "http://127.0.0.1:7860"

# --- AGENT 1: THE INTEL ANALYST ---
INTEL_PROMPT = textwrap.dedent("""
You are Agent Alpha: The Lead Intelligence Analyst.
Read the provided Observation (SITREP and Telemetry).
Your ONLY job is to filter out noisy/fake sensor data and identify the TRUE crisis.
Write a concise, 2-sentence Tactical Brief for the Commander.
State exactly what the real threat is, how severe it is, and the EXACT PROPER NOUN REGION NAME found in the SITREP.
Do not discuss resources or budgets.
""")

# --- AGENT 2: THE LOGISTICS COMMANDER ---
COMMANDER_PROMPT = textwrap.dedent("""
You are Agent Beta: The Logistics Commander.
You will receive a Tactical Brief from your Intel Analyst and an Observation JSON detailing available resources.
CRITICAL CONSTRAINT: You have a strict $100,000 Logistics Budget.
Costs: Boats = $5000, Ambulances = $2000, Food Kits = $50. Do NOT exceed the budget.
TACTICAL DOCTRINE: Coastal Cyclones/Floods require massive boat deployments (10+). Prioritize heavy equipment over food.
Respond ONLY with a valid JSON object matching exactly this schema:
{
  "threat_level": "low" | "medium" | "high",
  "deploy_region": "Copy the exact region name from the Intel Brief",
  "budget_scratchpad": "Show your math step-by-step: (boats * 5000) + (amb * 2000) + (food * 50) = Total. Verify it is <= 100000.",
  "resource_allocation": {"boats": 0, "ambulances": 0, "food_kits": 0},
  "reasoning": "Brief logical justification based on the Intel Brief"
}
""")

def run_task(task_id: str):
    print(f"[START] task={task_id} env={BENCHMARK} model={MODEL_NAME}")

    response = requests.get(f"{SERVER_URL}/reset?scenario_id={task_id}")
    obs_dict = response.json()

    success = False
    total_score = 0.0
    rewards = []

    # SPEED UP: Wait just 0.5s for the map to reset
    time.sleep(0.5)

    for step_num in range(1, MAX_STEPS + 1):
        user_msg = json.dumps(obs_dict, indent=2)
        action_json = None

        try:
            # ==========================================
            # STEP 1: AGENT ALPHA (INTEL) GATHERS DATA
            # ==========================================
            intel_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": INTEL_PROMPT},
                    {"role": "user", "content": f"Raw Observation Data:\n{user_msg}"}
                ],
                temperature=0.3,
            )
            tactical_brief = intel_response.choices[0].message.content.strip()
            print(f"\n   [AGENT ALPHA - INTEL BRIEF]: {tactical_brief}\n")

            # ==========================================
            # STEP 2: AGENT BETA (COMMANDER) EXECUTES
            # ==========================================
            commander_payload = f"Intel Brief:\n{tactical_brief}\n\nAvailable Resources & Budget:\n{user_msg}"

            # Robustness: 3-Attempt Retry Loop for the JSON generation
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    cmd_response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": COMMANDER_PROMPT},
                            {"role": "user", "content": commander_payload}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.1,
                    )

                    raw_content = cmd_response.choices[0].message.content.strip()

                    if raw_content.startswith("```json"):
                        raw_content = raw_content[7:-3]
                    elif raw_content.startswith("```"):
                        raw_content = raw_content[3:-3]

                    action_json = json.loads(raw_content.strip())
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(2) # Keep this at 2s just in case the API rate-limits us

            if not action_json:
                raise ValueError("Commander failed to generate valid JSON.")

            # ==========================================
            # STEP 3: SEND TO ENVIRONMENT
            # ==========================================
            action_str = json.dumps(action_json, separators=(',', ':'))
            step_resp = requests.post(f"{SERVER_URL}/step", json=action_json)
            step_data = step_resp.json()

            obs_dict = step_data["observation"]
            reward = step_data["reward"]
            done = step_data["done"]
            info = step_data["info"]

            rewards.append(reward)
            print(f"[STEP] step={step_num} action={action_str} reward={reward:.2f} done={str(done).lower()}")

            # SPEED UP: Wait just 0.5s for the map to fly to the new target
            time.sleep(1)

            if done:
                success = info.get("success", False)
                total_score = reward
                break

        except Exception as e:
            error_msg = str(e).replace('\n', ' ')
            print(f"[STEP] step={step_num} FAILED error='{error_msg}'")
            rewards.append(0.0)
            break

    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={len(rewards)} score={total_score:.2f} rewards={rewards_str}")

if __name__ == "__main__":
    for task in TASKS:
        run_task(task)