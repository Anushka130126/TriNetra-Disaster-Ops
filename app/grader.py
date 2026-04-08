from typing import Dict, Tuple

def clamp_score(score: float) -> float:
    """
    Ensures the score is strictly between 0 and 1.
    Converts 1.0 to 0.99 and 0.0 to 0.01 to satisfy Phase 2 validation.
    """
    return max(0.01, min(0.99, round(score, 2)))

def grade_action(action: Dict, task_id: str, step: int, remaining_budget: int = 100000) -> Tuple[float, str]:
    score = 0.0
    feedback = ""

    threat_level = str(action.get("threat_level", "")).lower().strip()
    target = str(action.get("deploy_region", "")).lower().strip()
    resources = action.get("resource_allocation", {})
    boats = resources.get("boats", 0)
    ambs = resources.get("ambulances", 0)

    # STRICT BUDGET ENFORCEMENT
    if remaining_budget < 0:
        return 0.01, f"BANKRUPTCY. You overspent the logistics budget by ${abs(remaining_budget):,}. Operation failed."

    if task_id == "triage_basic":
        if threat_level == "high":
            score = 1.0
            feedback = "Excellent. Correctly classified severe threat."
        elif threat_level == "medium":
            score = 0.5
            feedback = "Partial success. Underestimated threat level."
        else:
            score = 0.0
            feedback = "Failed. Ignored critical data."

    elif task_id == "resource_allocation":
        if "odisha" in target:
            if boats >= 10:
                score = 1.0
                feedback = "Optimal allocation. Deployed boat fleet within budget."
            elif boats > 0:
                score = 0.7
                feedback = "Correct region, but insufficient boats allocated for cyclone."
            else:
                score = 0.4
                feedback = "Correct region, but failed to allocate ANY boats."
        else:
            score = 0.0
            feedback = "Critical error. Wrong region."

    elif task_id == "signal_vs_noise":
        if "mumbai" in target:
            if boats >= 5 and ambs >= 5:
                score = 1.0
                feedback = "Outstanding. Ignored fake noise, deployed balanced fleet within budget."
            else:
                score = 0.6
                feedback = "Identified Mumbai crisis, but resource allocation is critically unbalanced."
        elif "assam" in target:
            score = 0.0
            feedback = "Failed Trap. Reacted to noisy sensors."
        else:
            score = 0.0
            feedback = "Failed. Wrong region."

    else:
        score = 0.0
        feedback = "Unknown task ID."

    # Apply efficiency penalty
    penalty = min(0.2, (step - 1) * 0.05)

    # Calculate final score and apply the (0, 1) clamp
    final_score = clamp_score(score - penalty)

    return final_score, feedback