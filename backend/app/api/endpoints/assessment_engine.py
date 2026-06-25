import json
import random
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.schemas import (
    AssessmentScenario,
    AssessmentType,
    UserSegment,
    PackageType,
    PackageResult,
    DomainScore,
    RiskLevel,
)
from app.data.question_bank import (
    get_validity_items,
    get_interactive_scenarios,
    get_questions_for_package,
    PACKAGE_1_WEIGHTS,
    PACKAGE_3_RECOMMENDATION_BANDS,
    RISK_LEVELS,
    INTERACTIVE_SCENARIOS,
)
from app.services.patient_memory import PatientMemoryEngine

router = APIRouter()
mem = PatientMemoryEngine()


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class RawAnswer(BaseModel):
    question_id: str
    domain: str
    score: int  # 1 to 5 (Likert)
    is_reverse: bool = False
    question_text: str = ""
    raw_response: Any = None

class PackageSubmission(BaseModel):
    user_id: str
    segment: UserSegment
    package_type: PackageType
    answers: List[RawAnswer]
    validity_checks: List[bool] = []

class InteractiveAnswer(BaseModel):
    scenario_id: str
    selected_option: str  # e.g., "A", "B", "C", "D"

class CognitiveAnswer(BaseModel):
    task_id: str
    user_answer: str

class QuestionBankResponse(BaseModel):
    package: int
    segment: str
    total_questions: int
    questions: List[Dict[str, Any]]
    validity_items: List[Dict[str, Any]]
    sjt_scenarios: List[Dict[str, Any]] = []
    ethics_scenarios: List[Dict[str, Any]] = []
    priority_tasks: List[Dict[str, Any]] = []
    attention_tests: List[Dict[str, Any]] = []
    ei_tasks: List[Dict[str, Any]] = []
    logic_tasks: List[Dict[str, Any]] = []
    picture_tasks: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Full Question Bank Endpoint
# ---------------------------------------------------------------------------

@router.get("/questions/{package_num}", response_model=QuestionBankResponse)
async def get_question_bank(
    package_num: int,
    segment: UserSegment = Query(UserSegment.PROFESSIONAL),
):
    """Serve static questions and interactive scenarios based on package."""
    if package_num not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Package must be 1, 2, or 3.")
        
    all_questions = get_questions_for_package(package_num, segment.value)
    questions = []
    
    if package_num == 1:
        # Scaled-down blueprint (total 22 core items)
        required_counts = {
            "stress": 4, "burnout": 4, "emotional_wellbeing": 4,
            "distress": 4, "sleep": 3, "work_life": 3,
            "perceived_stress": 4, "burnout_clinical": 4, "quality_of_life": 4
        }
        # Group by domain
        domain_groups = {}
        for q in all_questions:
            domain_groups.setdefault(q["domain"], []).append(q)
            
        # Sample according to blueprint
        for dom, count in required_counts.items():
            if dom in domain_groups:
                pool = domain_groups[dom]
                if len(pool) <= count:
                    questions.extend(pool)
                else:
                    questions.extend(random.sample(pool, count))
    else:
        # Fallback for P2/P3 - sample 50% for now
        questions = random.sample(all_questions, max(1, len(all_questions) // 2))
    
    all_validity = get_validity_items(segment.value)
    if package_num == 1:
        validity = random.sample(all_validity, min(5, len(all_validity)))
    else:
        validity = random.sample(all_validity, min(10, len(all_validity)))
        
    # Get interactive tasks based on package requirements
    all_sjt = get_interactive_scenarios("sjt", segment.value)
    all_ethics = get_interactive_scenarios("ethics", segment.value)
    all_priority = get_interactive_scenarios("priority", segment.value)
    all_attention = INTERACTIVE_SCENARIOS.get("attention_tests", [])
    all_ei = INTERACTIVE_SCENARIOS.get("emotional_intelligence", [])
    all_logic = INTERACTIVE_SCENARIOS.get("logic_reasoning", [])
    all_picture = INTERACTIVE_SCENARIOS.get("picture_description", [])
    
    sjt_scenarios = []
    ethics_scenarios = []
    priority_tasks = []
    attention_tests = []
    ei_tasks = []
    logic_tasks = []
    picture_tasks = []
    
    if package_num == 1:
        sjt_scenarios = random.sample(all_sjt, min(5, len(all_sjt)))
        picture_tasks = all_picture  # Give them all picture tasks
    elif package_num == 2:
        sjt_scenarios = all_sjt[:10]
        ethics_scenarios = all_ethics[:5]
        priority_tasks = all_priority[:5]
        attention_tests = all_attention[:3]
        ei_tasks = all_ei[:5]
        picture_tasks = all_picture
    elif package_num == 3:
        sjt_scenarios = all_sjt[:15]
        ethics_scenarios = all_ethics[:5]
        priority_tasks = all_priority[:5]
        attention_tests = all_attention[:3]
        logic_tasks = all_logic[:5]
        picture_tasks = all_picture
        
    total_q = (len(questions) + len(validity) + len(sjt_scenarios) + len(ethics_scenarios) + 
               len(priority_tasks) + len(attention_tests) + len(ei_tasks) + len(logic_tasks) + len(picture_tasks))
               
    return QuestionBankResponse(
        package=package_num,
        segment=segment.value,
        total_questions=total_q,
        questions=questions,
        validity_items=validity,
        sjt_scenarios=sjt_scenarios,
        ethics_scenarios=ethics_scenarios,
        priority_tasks=priority_tasks,
        attention_tests=attention_tests,
        ei_tasks=ei_tasks,
        logic_tasks=logic_tasks,
        picture_tasks=picture_tasks,
    )


# ---------------------------------------------------------------------------
# Contextual SJT & Writing Endpoints
# ---------------------------------------------------------------------------

@router.get("/sjt", response_model=AssessmentScenario)
async def get_random_sjt(segment: UserSegment = Query(...)):
    """Return a random SJT scenario tailored to segment."""
    scenarios = get_interactive_scenarios("sjt", segment.value)
    if not scenarios:
        raise HTTPException(status_code=404, detail="No SJT scenarios for this segment.")
    s = random.choice(scenarios)
    return AssessmentScenario(
        id=s["id"],
        type=AssessmentType.SJT,
        title=s["title"],
        description=s["description"],
        questions=[f"{k}) {v}" for k, v in s.get("options", {}).items()] or [s.get("description", "")],
    )

@router.get("/writing", response_model=AssessmentScenario)
async def get_random_writing(segment: UserSegment = Query(...)):
    """Return a random Writing scenario tailored to segment."""
    # Writing tasks are shared across segments in the bank but contextualized at the prompt level
    bank = [
        {"id": "write_001_pro", "title": "Career Failure", "description": "Reflect on a time you failed at an important project at work.", "questions": ["Write about a failure.", "What did you learn?"]} if segment == UserSegment.PROFESSIONAL else
        {"id": "write_001_stu", "title": "Academic Setback", "description": "Reflect on a time you failed an important exam or class.", "questions": ["Write about a failure.", "How did it make you feel?"]},
        {"id": "write_002_pro", "title": "Proudest Moment", "description": "Describe your proudest professional achievement.", "questions": ["What made it special?", "How did others react?"]} if segment == UserSegment.PROFESSIONAL else
        {"id": "write_002_stu", "title": "Proudest Moment", "description": "Describe your proudest academic achievement.", "questions": ["What made it special?", "How did others react?"]},
    ]
    s = random.choice(bank)
    return AssessmentScenario(id=s["id"], type=AssessmentType.WRITING, title=s["title"], description=s["description"], questions=s["questions"])


# ---------------------------------------------------------------------------
# Ethics Scenarios Endpoint
# ---------------------------------------------------------------------------

@router.get("/ethics")
async def get_ethics_scenarios(segment: UserSegment = Query(...)):
    """Return ethics dilemma scenarios for the given segment."""
    scenarios = get_interactive_scenarios("ethics", segment.value)
    return {"segment": segment.value, "scenarios": scenarios}


# ---------------------------------------------------------------------------
# Priority Ranking Tasks Endpoint
# ---------------------------------------------------------------------------

@router.get("/priority")
async def get_priority_tasks(segment: UserSegment = Query(...)):
    """Return priority ranking tasks for the given segment."""
    tasks = get_interactive_scenarios("priority", segment.value)
    return {"segment": segment.value, "tasks": tasks}


# ---------------------------------------------------------------------------
# Attention & Focus Tests Endpoint
# ---------------------------------------------------------------------------

@router.get("/attention")
async def get_attention_tests():
    """Return cognitive attention & focus tests (segment-neutral)."""
    return {"tasks": INTERACTIVE_SCENARIOS.get("attention_tests", [])}


# ---------------------------------------------------------------------------
# Logic & Reasoning Tasks Endpoint
# ---------------------------------------------------------------------------

@router.get("/logic")
async def get_logic_tasks(segment: UserSegment = Query(UserSegment.PROFESSIONAL)):
    """Return logic & reasoning tasks with segment-appropriate text."""
    tasks = INTERACTIVE_SCENARIOS.get("logic_reasoning", [])
    text_key = f"text_{segment.value}"
    answer_key = f"correct_answer_{segment.value}"
    result = []
    for t in tasks:
        result.append({
            "id": t["id"],
            "type": t["type"],
            "text": t.get(text_key, t.get("text_professional", "")),
            "correct_answer": t.get(answer_key, t.get("correct_answer_professional", "")),
        })
    return {"segment": segment.value, "tasks": result}


# ---------------------------------------------------------------------------
# Emotional Intelligence Tasks Endpoint
# ---------------------------------------------------------------------------

@router.get("/emotional-intelligence")
async def get_ei_tasks(segment: UserSegment = Query(UserSegment.PROFESSIONAL)):
    """Return EI tasks with segment-appropriate text."""
    tasks = INTERACTIVE_SCENARIOS.get("emotional_intelligence", [])
    text_key = f"text_{segment.value}"
    result = []
    for t in tasks:
        item = {
            "id": t["id"],
            "type": t["type"],
            "text": t.get(text_key, t.get("text_professional", "")),
            "measures": t.get("measures", []),
        }
        if "options" in t:
            item["options"] = t["options"]
            item["correct"] = t.get("correct", "")
        result.append(item)
    return {"segment": segment.value, "tasks": result}


# ---------------------------------------------------------------------------
# Scoring Engine
# ---------------------------------------------------------------------------

@router.post("/score", response_model=PackageResult)
async def score_package(submission: PackageSubmission):
    """
    Process raw Likert answers and use LLM to compute Confidence % and Evidence gathering.
    """
    # 1. Validity Check
    validity_score = 100.0
    if submission.validity_checks:
        passed = sum(1 for v in submission.validity_checks if v)
        validity_score = (passed / len(submission.validity_checks)) * 100

    # 2. Dynamic Scoring via LLM
    answers_text = "\n".join([f"Domain: {a.domain} | Score: {a.score}/5 (Reverse: {a.is_reverse})" for a in submission.answers])
    
    prompt = f"""
    You are an expert psychological evaluator. Analyze these assessment responses for a {submission.segment.value}.
    The user's validity score on hidden items was {validity_score}%.
    
    Responses:
    {answers_text}
    
    Generate a JSON object containing the computed metric scores (0-100) and a highly detailed psychometric profile.
    For the domains array, you MUST output a score, a confidence percentage (based on the validity score and variance of answers), and textual evidence.
    
    You must also include a "detailed_report" object containing deep insights extracted from the user's free-text responses (like picture descriptions and situational judgments).
    
    Output strictly in this JSON format:
    {{
      "domains": [
        {{
          "domain_name": "Drive/Decision-Making",
          "score": 60,
          "confidence": 88,
          "evidence": ["Evidence 1", "Evidence 2"]
        }}
      ],
      "detailed_report": {{
        "role_fitment_score": 62.6,
        "growth_potential_score": 65.0,
        "executive_summary": [
          "Role fit is not recommended.",
          "Strong energy supports role success."
        ],
        "key_strengths": [
          "Energy/Social Confidence - extraversion enhances engagement."
        ],
        "development_areas": [
          "Learning/Adaptability - lower score may reduce comfort with change."
        ],
        "coworking_insights": {{
          "Communication Style": "Good",
          "Collaboration Style": "Moderate",
          "Decision Making Behaviour": "Good"
        }},
        "personality_insights": {{
          "Energizers": ["High-energy interactions", "Motivating team vibes"],
          "Drainers": ["Slow response under stress"],
          "Blind Spots": ["Hesitation in fast decisions"]
        }}
      }}
    }}
    """
    
    from app.config import get_settings
    from groq import AsyncGroq
    settings = get_settings()
    
    try:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
            
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        
        parsed = json.loads(content.strip())
        domain_list = parsed.get("domains", [])
        detailed_report_data = parsed.get("detailed_report", None)
        
        domain_scores = []
        for d in domain_list:
            domain_scores.append(DomainScore(
                domain_name=d.get("domain_name", "Unknown"),
                score=d.get("score", 50.0),
                confidence=d.get("confidence", 85.0),
                evidence=d.get("evidence", [])
            ))
            
        detailed_report = None
        if detailed_report_data:
            from app.schemas import DetailedPDFReport
            detailed_report = DetailedPDFReport(**detailed_report_data)
            
    except Exception as e:
        print("LLM Error in scoring:", e)
        # Fallback to math
        domain_totals = {}
        domain_counts = {}
        for ans in submission.answers:
            val = (6 - ans.score) if ans.is_reverse else ans.score
            domain_totals[ans.domain] = domain_totals.get(ans.domain, 0) + val
            domain_counts[ans.domain] = domain_counts.get(ans.domain, 0) + 1
        domain_scores = []
        for dom, total in domain_totals.items():
            max_possible = domain_counts[dom] * 5
            norm = (total / max_possible) * 100 if max_possible > 0 else 0
            domain_scores.append(DomainScore(domain_name=dom, score=round(norm, 2), confidence=validity_score, evidence=["Fallback mathematical calculation"]))
        detailed_report = None

    # 3. Final Risk Level (simplified for brevity)
    avg_score = sum(ds.score for ds in domain_scores) / len(domain_scores) if domain_scores else 0
    if avg_score >= 80:
        final_risk = RiskLevel.CRITICAL if submission.package_type == PackageType.PACKAGE_1_WELLBEING else RiskLevel.MINIMAL
    elif avg_score >= 60:
        final_risk = RiskLevel.HIGH if submission.package_type == PackageType.PACKAGE_1_WELLBEING else RiskLevel.LOW
    else:
        final_risk = RiskLevel.MODERATE

    raw_ans_list = []
    for ans in submission.answers:
        raw_ans_list.append({
            "question_id": ans.question_id,
            "domain": ans.domain,
            "question_text": ans.question_text,
            "score": ans.score,
            "is_reverse": ans.is_reverse,
            "raw_response": ans.raw_response
        })

    # Save to database for later master reporting
    mem.save_assessment_results(submission.user_id, submission.package_type.value, raw_ans_list)

    return PackageResult(
        user_id=submission.user_id,
        package_type=submission.package_type,
        segment=submission.segment,
        timestamp=datetime.datetime.utcnow().isoformat(),
        validity_score=round(validity_score, 2),
        domain_scores=domain_scores,
        final_risk_level=final_risk,
        detailed_report=detailed_report,
        raw_answers=raw_ans_list,
    )



# ---------------------------------------------------------------------------
# SJT Scoring Endpoint
# ---------------------------------------------------------------------------

@router.post("/score/sjt")
async def score_sjt(answers: List[InteractiveAnswer], segment: UserSegment = Query(...)):
    """Score SJT responses using the predefined scoring rubrics."""
    scenarios = get_interactive_scenarios("sjt", segment.value)
    scenario_map = {s["id"]: s for s in scenarios}
    total = 0
    max_total = 0
    details = []
    for ans in answers:
        scenario = scenario_map.get(ans.scenario_id)
        if not scenario:
            continue
        scoring = scenario.get("scoring", {})
        score = scoring.get(ans.selected_option.upper(), 0)
        max_score = max(scoring.values()) if scoring else 5
        total += score
        max_total += max_score
        details.append({
            "scenario_id": ans.scenario_id,
            "selected": ans.selected_option,
            "score": score,
            "max": max_score,
            "measures": scenario.get("measures", []),
        })
    normalized = (total / max_total * 100) if max_total > 0 else 0
    return {
        "total_score": total,
        "max_score": max_total,
        "normalized_score": round(normalized, 2),
        "details": details,
    }


# ---------------------------------------------------------------------------
# Cognitive Task Scoring Endpoint
# ---------------------------------------------------------------------------

@router.post("/score/cognitive")
async def score_cognitive(answers: List[CognitiveAnswer]):
    """Score attention and logic tasks."""
    all_tasks = INTERACTIVE_SCENARIOS.get("attention_tests", []) + INTERACTIVE_SCENARIOS.get("logic_reasoning", [])
    task_map = {t["id"]: t for t in all_tasks}
    correct = 0
    total = len(answers)
    details = []
    for ans in answers:
        task = task_map.get(ans.task_id)
        if not task:
            continue
        expected = task.get("correct_answer", task.get("correct_answer_professional", ""))
        is_correct = ans.user_answer.strip().lower() == expected.strip().lower()
        if is_correct:
            correct += 1
        details.append({
            "task_id": ans.task_id,
            "user_answer": ans.user_answer,
            "correct_answer": expected,
            "is_correct": is_correct,
        })
    accuracy = (correct / total * 100) if total > 0 else 0
    return {
        "correct": correct,
        "total": total,
        "accuracy": round(accuracy, 2),
        "details": details,
    }
