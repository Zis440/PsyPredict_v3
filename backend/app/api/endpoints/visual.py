import base64
import hashlib
import os
import random
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class AssessmentScenario(BaseModel):
    id: str
    type: str
    title: str
    description: str
    image_url: Optional[str] = None
    questions: List[str]


# ---------------------------------------------------------------------------
# Image Loading — searches multiple directories for generated images
# ---------------------------------------------------------------------------

IMAGE_SEARCH_DIRS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "images"),
    r"C:\Users\Saphalya\.gemini\antigravity-ide\brain\1bf6b360-5f6a-405a-b91c-7db26c7ffc0c",
    r"C:\Users\Saphalya\.gemini\antigravity-ide\brain\bc5fae37-1eea-4238-b310-e60dbe39a432",
]


def get_base64_image(filename: str) -> Optional[str]:
    """Search multiple directories for an image starting with `filename` and return base64."""
    for search_dir in IMAGE_SEARCH_DIRS:
        try:
            if not os.path.isdir(search_dir):
                continue
            files = os.listdir(search_dir)
            for f in files:
                if f.startswith(filename) and f.endswith(".png"):
                    filepath = os.path.join(search_dir, f)
                    with open(filepath, "rb") as img_file:
                        b64 = base64.b64encode(img_file.read()).decode("utf-8")
                        return f"data:image/png;base64,{b64}"
        except Exception as e:
            print(f"Failed to load image {filename} from {search_dir}: {e}")
    return None


# ---------------------------------------------------------------------------
# Full Pool of 10 Visual Assessment Scenarios
# ---------------------------------------------------------------------------

ALL_SCENARIOS = [
    # --- Original 5 ---
    {
        "id": "v1",
        "type": "visual",
        "title": "Ambiguous Expression",
        "description": "A person displays a complex, hard-to-read facial expression. Study the image carefully.",
        "image_key": "ambiguous_expression",
        "questions": [
            "What emotion is this person experiencing?",
            "What might have happened right before this moment?",
            "How confident are you in your reading of this expression?"
        ]
    },
    {
        "id": "v2",
        "type": "visual",
        "title": "Distracted Friend",
        "description": "Two people are together, but their attention is divided. Observe the dynamics.",
        "image_key": "distracted_friend",
        "questions": [
            "Describe the dynamic between these two figures.",
            "Is one person seeking connection while the other is avoiding it?",
            "What would you do if you were the person being ignored?"
        ]
    },
    {
        "id": "v3",
        "type": "visual",
        "title": "Dropped Groceries",
        "description": "An everyday mishap in a public setting. Observe how people react.",
        "image_key": "dropped_groceries",
        "questions": [
            "How does the crowd react to the fallen items?",
            "What feelings does this chaotic scene evoke in you?",
            "Would you stop to help? Why or why not?"
        ]
    },
    {
        "id": "v4",
        "type": "visual",
        "title": "Park Distress",
        "description": "A person sits alone in a peaceful outdoor environment, but their body language tells a different story.",
        "image_key": "park_distress",
        "questions": [
            "Why does the person's internal state contrast with the peaceful environment?",
            "What might they be contemplating?",
            "If you walked past this person, would you approach them?"
        ]
    },
    {
        "id": "v5",
        "type": "visual",
        "title": "Workplace Conflict",
        "description": "A tense moment between colleagues in a professional setting.",
        "image_key": "workplace_conflict",
        "questions": [
            "What is the source of the unspoken tension?",
            "How is the rigid structure contributing to the conflict?",
            "What would you do to de-escalate this situation?"
        ]
    },
    # --- New 5 ---
    {
        "id": "v6",
        "type": "visual",
        "title": "Lonely in a Crowd",
        "description": "A person sits alone in a busy, social environment, absorbed in their own world.",
        "image_key": "lonely_in_crowd",
        "questions": [
            "What emotion do you think this person is feeling despite being surrounded by people?",
            "Is this person choosing solitude, or is it involuntary?",
            "Have you ever felt isolated in a crowded room? Describe the feeling."
        ]
    },
    {
        "id": "v7",
        "type": "visual",
        "title": "The Moral Crossroads",
        "description": "A figure stands at a literal fork in the path, facing a difficult choice under pressure.",
        "image_key": "moral_dilemma",
        "questions": [
            "What decision is this person facing?",
            "Which path would you choose, and why?",
            "What internal conflict does this scene represent to you?"
        ]
    },
    {
        "id": "v8",
        "type": "visual",
        "title": "Family Tension",
        "description": "A family gathering where unspoken emotions simmer beneath the surface.",
        "image_key": "family_tension",
        "questions": [
            "What is the source of tension at this table?",
            "Who do you empathize with the most, and why?",
            "How would you mediate this situation if you were present?"
        ]
    },
    {
        "id": "v9",
        "type": "visual",
        "title": "Broken Trust",
        "description": "A scene in a professional setting where one person observes another through a barrier.",
        "image_key": "broken_trust",
        "questions": [
            "What has happened between these two people?",
            "Is the observer feeling guilt, suspicion, or something else?",
            "How does physical separation (the barrier) mirror emotional distance?"
        ]
    },
    {
        "id": "v10",
        "type": "visual",
        "title": "Overwhelmed Student",
        "description": "A young person surrounded by academic pressure while others pass by unaware.",
        "image_key": "overwhelmed_student",
        "questions": [
            "What is this person feeling right now?",
            "Why do you think no one around them has noticed their distress?",
            "What advice would you give this person if they came to you for help?"
        ]
    },
]


# ---------------------------------------------------------------------------
# Per-User Randomization
# ---------------------------------------------------------------------------

def _get_user_seed(user_id: str) -> int:
    """Generate a deterministic seed from user_id so the same user always gets the same set."""
    return int(hashlib.sha256(user_id.encode()).hexdigest(), 16) % (10**9)


@router.get("/scenarios")
async def get_visual_scenarios(
    user_id: str = Query("anonymous", description="User ID for per-user randomization"),
    count: int = Query(5, ge=3, le=10, description="Number of scenarios to return (3-10)")
):
    """
    Returns a randomized subset of visual assessment scenarios.
    Different users get different images in a different order,
    so the assessment feels unique and not like a gimmick.
    The same user_id will always receive the same set (deterministic).
    """
    seed = _get_user_seed(user_id)
    rng = random.Random(seed)

    # Shuffle and pick `count` scenarios deterministically for this user
    pool = list(ALL_SCENARIOS)
    rng.shuffle(pool)
    selected = pool[:count]

    # Build response with base64 images
    scenarios = []
    for s in selected:
        scenarios.append(AssessmentScenario(
            id=s["id"],
            type=s["type"],
            title=s["title"],
            description=s["description"],
            image_url=get_base64_image(s["image_key"]),
            questions=s["questions"],
        ))

    return {"scenarios": scenarios, "total_pool": len(ALL_SCENARIOS), "served": len(scenarios)}
