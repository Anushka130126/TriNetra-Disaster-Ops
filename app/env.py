import time
import random
from typing import Tuple, Dict, Any
from .models import Observation, Action, ResourceState
from .grader import grade_action

class DisasterEnv:
    def __init__(self):
        self.current_task = "triage_basic"
        self.step_count = 1
        self.ui_state = {}
        self.last_obs = None
        self.reset()

    def _generate_procedural_data(self, task_id: str) -> dict:
            """Procedurally generates infinite variations of the scenarios."""
            if task_id == "triage_basic":
                rain = random.randint(180, 350)
                return {
                    "region": "Himachal Pass", "lat": 31.1048, "lon": 77.1734,
                    "forecast": f"Torrential Rain ({rain}mm/24h)",
                    "severity": round(random.uniform(0.75, 0.95), 2),
                    "population": random.randint(10000, 20000),
                    "resources": {"boats": 0, "ambulances": 15, "food_kits": 500},
                    # FIX: Added "at Himachal Pass"
                    "report": f"SITREP: High-altitude sensors at Himachal Pass indicate {rain}mm rainfall. Mudslide risk critical. LOGISTICS BUDGET: $100,000. Deployment Costs: Boats $5k, Ambulances $2k, Food $50.",
                    "telemetry": {"terrain": "Steep Gradient", "soil_moisture": f"{random.randint(90, 99)}%", "river_level": "Warning"}
                }
            elif task_id == "resource_allocation":
                wind = random.randint(130, 180)
                return {
                    "region": "Odisha Coast", "lat": 20.2724, "lon": 85.8338,
                    "forecast": f"Category {random.randint(3, 5)} Cyclone",
                    "severity": round(random.uniform(0.85, 0.98), 2),
                    "population": random.randint(40000, 60000),
                    "resources": {"boats": 30, "ambulances": 15, "food_kits": 1000},
                    # FIX: Added "on the Odisha Coast"
                    "report": f"SITREP: Cyclone landfall imminent on the Odisha Coast. Wind speeds {wind}km/h. LOGISTICS BUDGET: $100,000. Deployment Costs: Boats $5k, Ambulances $2k, Food $50.",
                    "telemetry": {"terrain": "Coastal Lowland", "wind_speed": f"{wind}km/h", "surge_height": f"{random.uniform(2.5, 4.5):.1f}m"}
                }
            else: # signal_vs_noise
                return {
                    "region": "Mumbai Basin", "lat": 19.0760, "lon": 72.8777,
                    "forecast": "Mixed Weather Front",
                    "severity": round(random.uniform(0.70, 0.85), 2),
                    "population": random.randint(100000, 150000),
                    "resources": {"boats": 20, "ambulances": 25, "food_kits": 800},
                    # FIX: Added "Mumbai Basin"
                    "report": "SITREP: Conflicting data. Assam sensors spiking (Satellite: 0mm rain). Mumbai Basin drainage telemetry showing critical failure. LOGISTICS BUDGET: $100,000. Deployment Costs: Boats $5k, Ambulances $2k, Food $50.",
                    "telemetry": {"Assam_Sensors": "ERRATIC_HIGH", "Assam_Rain": "0mm", "Mumbai_Drainage": "CRITICAL_FAIL", "Mumbai_Rain": f"{random.randint(150, 220)}mm"}
                }

    def reset(self, task_id: str = "triage_basic") -> Observation:
        self.current_task = task_id
        self.step_count = 1
        data = self._generate_procedural_data(task_id)

        self.last_obs = Observation(
            task_id=self.current_task, step=self.step_count,
            intelligence_report=data["report"], telemetry_data=data["telemetry"],
            available_resources=ResourceState(**data["resources"]), last_action_feedback=None
        )

        self.ui_state = {
            "region": data["region"], "coords": [data["lat"], data["lon"]],
            "forecast": data["forecast"], "severity": data["severity"],
            "population": data["population"], "casualties": 0,
            "resources": data["resources"], "step": self.step_count,
            "budget": 100000,  # THE NEW BUDGET TRACKER
            "last_action": None,
            "history": [{"step": 0, "severity": data["severity"], "score": 0.0}]
        }
        return self.last_obs

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        action_dict = getattr(action, "model_dump", action.dict)()
        resources_used = action_dict.get("resource_allocation", {})

        # Calculate Financial Cost
        boats_deployed = resources_used.get("boats", 0)
        amb_deployed = resources_used.get("ambulances", 0)
        food_deployed = resources_used.get("food_kits", 0)
        total_cost = (boats_deployed * 5000) + (amb_deployed * 2000) + (food_deployed * 50)

        # Deduct from budget
        self.ui_state["budget"] -= total_cost

        # Pass budget context to grader
        score, feedback = grade_action(action_dict, self.current_task, self.step_count, self.ui_state["budget"])

        # Procedural Consequences Math
        lives_saved = (boats_deployed * 25) + (amb_deployed * 15)
        vulnerable_pop = int(self.ui_state["population"] * self.ui_state["severity"] * 0.05)

        if score < 0.5:
            new_casualties = max(0, vulnerable_pop - lives_saved)
            self.ui_state["casualties"] += (new_casualties + int(vulnerable_pop * random.uniform(0.01, 0.05)))
            self.ui_state["severity"] = min(1.0, self.ui_state["severity"] + 0.08)
        else:
            self.ui_state["severity"] = max(0.1, self.ui_state["severity"] - 0.15)

        self.ui_state["step"] = self.step_count
        self.ui_state["last_action"] = {
            "decision": action_dict.get("threat_level", "N/A").upper(),
            "target_region": action_dict.get("deploy_region", "N/A"),
            "resources": resources_used, "cost": total_cost,
            "score": score, "feedback": [feedback]
        }

        self.ui_state["history"].append({"step": self.step_count, "severity": self.ui_state["severity"], "score": score})
        budget_str = f" | BANK BALANCE: ${self.ui_state['budget']:,}"
        self.last_obs.last_action_feedback = feedback + budget_str
        self.last_obs.step = self.step_count

        done = True if self.step_count >= 3 or score >= 1.0 or self.ui_state["budget"] < 0 else False
        self.step_count += 1
        info = {"task_id": self.current_task, "success": bool(score >= 0.8), "feedback": feedback}

        return self.last_obs, score, done, info

    def state(self) -> Dict[str, Any]:
        return self.ui_state