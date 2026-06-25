"""
question_bank_clinical.py — PsyPredict Clinical Assessment Items

Derived from validated psychological instruments:
  1. PSS-10 (Cohen, 1983) — Perceived Stress Scale
     Domains: unpredictability, uncontrollability, overload
  2. MBI (Maslach & Jackson) — Maslach Burnout Inventory
     Domains: emotional_exhaustion, depersonalization, personal_accomplishment
  3. WRQoL (Van Laar et al., 2007) — Work-Related Quality of Life Scale
     Domains: job_career_satisfaction, general_wellbeing, home_work_interface,
              control_at_work, working_conditions

Each item has dual-segment variants (Student vs Professional).

Total: 34 items (10 PSS-10 + 12 MBI + 12 WRQoL)
All items are assigned to Package 1 for clinical-depth wellbeing screening.
"""

from typing import List, Dict, Any


# ---------------------------------------------------------------------------
# PSS-10 Inspired — Perceived Stress (10 items)
# Measures how unpredictable, uncontrollable, and overloaded respondents
# feel their lives have been in the last month.
# ---------------------------------------------------------------------------

PSS10_QUESTIONS: List[Dict[str, Any]] = [
    # --- Unpredictability (3 items) ---
    {"id": "p1_pss_01", "domain": "perceived_stress", "subdomain": "unpredictability", "package": 1,
     "text_student": "In the last month, I have often been upset because of something that happened unexpectedly in my academic life.",
     "text_professional": "In the last month, I have often been upset because of something that happened unexpectedly at work.", "is_reverse": False, "is_validity": False},
    {"id": "p1_pss_02", "domain": "perceived_stress", "subdomain": "unpredictability", "package": 1,
     "text_student": "In the last month, I felt that I could not predict what would happen next in my studies.",
     "text_professional": "In the last month, I felt that I could not predict what would happen next in my career.", "is_reverse": False, "is_validity": False},
    {"id": "p1_pss_03", "domain": "perceived_stress", "subdomain": "unpredictability", "package": 1,
     "text_student": "In the last month, I felt confident about my ability to handle unexpected academic challenges.",
     "text_professional": "In the last month, I felt confident about my ability to handle unexpected work challenges.", "is_reverse": True, "is_validity": False},

    # --- Uncontrollability (4 items) ---
    {"id": "p1_pss_04", "domain": "perceived_stress", "subdomain": "uncontrollability", "package": 1,
     "text_student": "In the last month, I often felt that I could not control the important things in my academic life.",
     "text_professional": "In the last month, I often felt that I could not control the important things in my work life.", "is_reverse": False, "is_validity": False},
    {"id": "p1_pss_05", "domain": "perceived_stress", "subdomain": "uncontrollability", "package": 1,
     "text_student": "In the last month, I felt that things in my studies were going my way.",
     "text_professional": "In the last month, I felt that things at work were going my way.", "is_reverse": True, "is_validity": False},
    {"id": "p1_pss_06", "domain": "perceived_stress", "subdomain": "uncontrollability", "package": 1,
     "text_student": "In the last month, I have been angered because academic outcomes were outside my control.",
     "text_professional": "In the last month, I have been angered because workplace outcomes were outside my control.", "is_reverse": False, "is_validity": False},
    {"id": "p1_pss_07", "domain": "perceived_stress", "subdomain": "uncontrollability", "package": 1,
     "text_student": "In the last month, I felt I was on top of my academic responsibilities.",
     "text_professional": "In the last month, I felt I was on top of my professional responsibilities.", "is_reverse": True, "is_validity": False},

    # --- Overload (3 items) ---
    {"id": "p1_pss_08", "domain": "perceived_stress", "subdomain": "overload", "package": 1,
     "text_student": "In the last month, I found that difficulties in my studies were piling up so high that I could not overcome them.",
     "text_professional": "In the last month, I found that problems at work were piling up so high that I could not overcome them.", "is_reverse": False, "is_validity": False},
    {"id": "p1_pss_09", "domain": "perceived_stress", "subdomain": "overload", "package": 1,
     "text_student": "In the last month, I have been able to control irritations in my academic life.",
     "text_professional": "In the last month, I have been able to control irritations in my work life.", "is_reverse": True, "is_validity": False},
    {"id": "p1_pss_10", "domain": "perceived_stress", "subdomain": "overload", "package": 1,
     "text_student": "In the last month, I felt nervously stressed about my academic obligations.",
     "text_professional": "In the last month, I felt nervously stressed about my professional obligations.", "is_reverse": False, "is_validity": False},
]


# ---------------------------------------------------------------------------
# MBI Inspired — Clinical Burnout (12 items)
# Measures the three classical dimensions of the Maslach Burnout model:
# emotional exhaustion, depersonalization, and personal accomplishment.
# ---------------------------------------------------------------------------

MBI_QUESTIONS: List[Dict[str, Any]] = [
    # --- Emotional Exhaustion (4 items) ---
    {"id": "p1_mbi_01", "domain": "burnout_clinical", "subdomain": "emotional_exhaustion", "package": 1,
     "text_student": "I feel emotionally drained from my studies at the end of most days.",
     "text_professional": "I feel emotionally drained from my work at the end of most days.", "is_reverse": False, "is_validity": False},
    {"id": "p1_mbi_02", "domain": "burnout_clinical", "subdomain": "emotional_exhaustion", "package": 1,
     "text_student": "I feel used up when I wake up in the morning and have to face another day of classes.",
     "text_professional": "I feel used up when I wake up in the morning and have to face another day of work.", "is_reverse": False, "is_validity": False},
    {"id": "p1_mbi_03", "domain": "burnout_clinical", "subdomain": "emotional_exhaustion", "package": 1,
     "text_student": "Studying all day is really a strain for me.",
     "text_professional": "Working with people all day is really a strain for me.", "is_reverse": False, "is_validity": False},
    {"id": "p1_mbi_04", "domain": "burnout_clinical", "subdomain": "emotional_exhaustion", "package": 1,
     "text_student": "I feel like I am at the end of my rope academically.",
     "text_professional": "I feel like I am at the end of my rope professionally.", "is_reverse": False, "is_validity": False},

    # --- Depersonalization (4 items) ---
    {"id": "p1_mbi_05", "domain": "burnout_clinical", "subdomain": "depersonalization", "package": 1,
     "text_student": "I feel I treat some classmates as if they were impersonal objects.",
     "text_professional": "I feel I treat some colleagues or clients as if they were impersonal objects.", "is_reverse": False, "is_validity": False},
    {"id": "p1_mbi_06", "domain": "burnout_clinical", "subdomain": "depersonalization", "package": 1,
     "text_student": "I have become more callous toward people since starting this program.",
     "text_professional": "I have become more callous toward people since starting this job.", "is_reverse": False, "is_validity": False},
    {"id": "p1_mbi_07", "domain": "burnout_clinical", "subdomain": "depersonalization", "package": 1,
     "text_student": "I worry that my academic struggles are making me emotionally detached.",
     "text_professional": "I worry that this job is hardening me emotionally.", "is_reverse": False, "is_validity": False},
    {"id": "p1_mbi_08", "domain": "burnout_clinical", "subdomain": "depersonalization", "package": 1,
     "text_student": "I do not really care what happens to some of my classmates or group members.",
     "text_professional": "I do not really care what happens to some of my clients or colleagues.", "is_reverse": False, "is_validity": False},

    # --- Personal Accomplishment (4 items — positive = reverse-scored) ---
    {"id": "p1_mbi_09", "domain": "burnout_clinical", "subdomain": "personal_accomplishment", "package": 1,
     "text_student": "I can easily understand how my classmates feel about things.",
     "text_professional": "I can easily understand how my colleagues feel about things.", "is_reverse": True, "is_validity": False},
    {"id": "p1_mbi_10", "domain": "burnout_clinical", "subdomain": "personal_accomplishment", "package": 1,
     "text_student": "I deal very effectively with the problems of my fellow students.",
     "text_professional": "I deal very effectively with the problems of my clients and team members.", "is_reverse": True, "is_validity": False},
    {"id": "p1_mbi_11", "domain": "burnout_clinical", "subdomain": "personal_accomplishment", "package": 1,
     "text_student": "I feel I am positively influencing other students' lives through my efforts.",
     "text_professional": "I feel I am positively influencing other people's lives through my work.", "is_reverse": True, "is_validity": False},
    {"id": "p1_mbi_12", "domain": "burnout_clinical", "subdomain": "personal_accomplishment", "package": 1,
     "text_student": "I feel exhilarated after working closely with my classmates.",
     "text_professional": "I feel exhilarated after working closely with my team.", "is_reverse": True, "is_validity": False},
]


# ---------------------------------------------------------------------------
# WRQoL Inspired — Quality of Life (12 items)
# Measures dimensions of work-related quality of life that affect overall
# wellbeing, satisfaction, and psychological health.
# ---------------------------------------------------------------------------

WRQOL_QUESTIONS: List[Dict[str, Any]] = [
    # --- Job/Career Satisfaction (3 items) ---
    {"id": "p1_qol_01", "domain": "quality_of_life", "subdomain": "job_career_satisfaction", "package": 1,
     "text_student": "I am satisfied with the overall quality of my academic experience.",
     "text_professional": "I am satisfied with the overall quality of my working life.", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_02", "domain": "quality_of_life", "subdomain": "job_career_satisfaction", "package": 1,
     "text_student": "I feel that my current course of study will lead to a fulfilling career.",
     "text_professional": "I feel that my current job provides opportunities for career growth.", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_03", "domain": "quality_of_life", "subdomain": "job_career_satisfaction", "package": 1,
     "text_student": "I feel my academic achievements are appropriately recognized by my institution.",
     "text_professional": "I feel my contributions at work are appropriately recognized and rewarded.", "is_reverse": True, "is_validity": False},

    # --- General Wellbeing (2 items) ---
    {"id": "p1_qol_04", "domain": "quality_of_life", "subdomain": "general_wellbeing", "package": 1,
     "text_student": "I feel good about myself as a student most of the time.",
     "text_professional": "I feel good about myself as a professional most of the time.", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_05", "domain": "quality_of_life", "subdomain": "general_wellbeing", "package": 1,
     "text_student": "My studies leave me feeling physically and emotionally unwell.",
     "text_professional": "My work demands leave me feeling physically and emotionally unwell.", "is_reverse": False, "is_validity": False},

    # --- Home-Work Interface (3 items) ---
    {"id": "p1_qol_06", "domain": "quality_of_life", "subdomain": "home_work_interface", "package": 1,
     "text_student": "My academic schedule allows me enough time to meet family and social obligations.",
     "text_professional": "My work schedule allows me enough time to meet family and social obligations.", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_07", "domain": "quality_of_life", "subdomain": "home_work_interface", "package": 1,
     "text_student": "The demands of my studies rarely interfere with my home and personal life.",
     "text_professional": "The demands of my job rarely interfere with my home and personal life.", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_08", "domain": "quality_of_life", "subdomain": "home_work_interface", "package": 1,
     "text_student": "I feel guilty about the time my studies take away from my loved ones.",
     "text_professional": "I feel guilty about the time my work takes away from my loved ones.", "is_reverse": False, "is_validity": False},

    # --- Control at Work (2 items) ---
    {"id": "p1_qol_09", "domain": "quality_of_life", "subdomain": "control_at_work", "package": 1,
     "text_student": "I feel I have a say in decisions that affect my academic experience.",
     "text_professional": "I feel I have a say in decisions that affect my job and working conditions.", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_10", "domain": "quality_of_life", "subdomain": "control_at_work", "package": 1,
     "text_student": "I feel powerless to influence my academic environment or policies.",
     "text_professional": "I feel powerless to influence my workplace environment or policies.", "is_reverse": False, "is_validity": False},

    # --- Working Conditions (2 items) ---
    {"id": "p1_qol_11", "domain": "quality_of_life", "subdomain": "working_conditions", "package": 1,
     "text_student": "I am satisfied with the physical conditions of my study environment (library, classrooms, labs).",
     "text_professional": "I am satisfied with the physical conditions of my workplace (office, facilities, equipment).", "is_reverse": True, "is_validity": False},
    {"id": "p1_qol_12", "domain": "quality_of_life", "subdomain": "working_conditions", "package": 1,
     "text_student": "I feel safe and supported in my campus environment.",
     "text_professional": "I feel safe and supported in my workplace environment.", "is_reverse": True, "is_validity": False},
]


# ---------------------------------------------------------------------------
# Combined Clinical Questions for Export
# ---------------------------------------------------------------------------

CLINICAL_QUESTIONS: List[Dict[str, Any]] = PSS10_QUESTIONS + MBI_QUESTIONS + WRQOL_QUESTIONS
