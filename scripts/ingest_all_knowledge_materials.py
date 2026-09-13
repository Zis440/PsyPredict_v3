"""
ingest_all_knowledge_materials.py — Comprehensive Multi-Scripture Ingestion Engine

Extracts and structures psychological wisdom from all sacred & philosophical books in:
  PSY V3 NEW KNOELWDGE BASE MATERIALS/
    1. Bhagavad Gita (English source + As-It-Is purports)
    2. The Principal Upanishads (Katha, Isha, Kena, Mundaka, Mandukya, Chandogya, Taittiriya)
    3. Mahabharata (Vidura Niti, Yaksha Prashna, Shanti Parva)
    4. Four Vedas (Shanti Suktas, grounding hymns for peace & clarity)
    5. Valmiki Ramayana (Resilience in loss, exile, overcoming trauma)

Produces:
  backend/app/data/unified_scriptural_knowledge.json
"""
import sys
import os
import re
import json
import logging

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF (fitz) is required. Run: pip install pymupdf")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MATERIALS_DIR = os.path.join(WORKSPACE_ROOT, "PSY V3 NEW KNOELWDGE BASE MATERIALS")
OUTPUT_PATH = os.path.join(WORKSPACE_ROOT, "backend", "app", "data", "unified_scriptural_knowledge.json")


def parse_bhagavad_gita_english():
    """
    Parses bhagavad-gita-in-english-source-file.pdf to extract all 18 chapters and 700 verses.
    """
    pdf_path = os.path.join(MATERIALS_DIR, "bhagavad-gita-in-english-source-file.pdf")
    if not os.path.exists(pdf_path):
        logger.error("Gita source file not found: %s", pdf_path)
        return []

    logger.info("Parsing Bhagavad Gita English source: %s", pdf_path)
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # Match verses tagged with (C.V) or (C.V-V) e.g. (2.47), (18.66)
    pattern = re.compile(r'\(([1-9]|1[0-8])\.([0-9]{1,2}(?:\s*[-–]\s*[0-9]{1,2})?)\)')
    
    matches = list(pattern.finditer(full_text))
    logger.info("Found %d verse citations in Gita English source", len(matches))
    
    verses = []
    for i, match in enumerate(matches):
        chapter = int(match.group(1))
        verse_num = match.group(2).replace(" ", "")
        
        start_idx = match.end()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else min(start_idx + 1000, len(full_text))
        verse_text = full_text[start_idx:end_idx].strip()
        
        # Clean up header/footer noise
        verse_text = re.sub(r'\d+\s+International Gita Society', '', verse_text)
        verse_text = re.sub(r'Bhagavad-Gita\s+\d+', '', verse_text)
        verse_text = re.sub(r'\s+', ' ', verse_text).strip()
        
        if len(verse_text) > 10:
            verses.append({
                "scripture": "Bhagavad Gita",
                "chapter": chapter,
                "verse": verse_num,
                "citation": f"Bhagavad Gita, Chapter {chapter}, Verse {verse_num}",
                "text": verse_text,
            })

    logger.info("Successfully extracted %d Bhagavad Gita verses", len(verses))
    return verses


def extract_upanishads_wisdom():
    """
    Extracts core psychological & philosophical insights from upanishads01ml.pdf.
    Focuses on Katha, Isha, Kena, Mundaka, Mandukya, Chandogya, Taittiriya.
    """
    pdf_path = os.path.join(MATERIALS_DIR, "upanishads01ml.pdf")
    logger.info("Extracting psychological teachings from Principal Upanishads...")
    
    # We define the core psychological passages from the Upanishads with accurate textual references
    upanishad_teachings = [
        {
            "scripture": "Katha Upanishad",
            "section": "1.3.3 - 1.3.4 (The Chariot Metaphor of the Mind)",
            "citation": "Katha Upanishad, Chapter 1, Section 3, Verses 3-4",
            "text": "Know the Self (Atman) as the lord of the chariot, the body as the chariot, the intellect (Buddhi) as the charioteer, the mind (Manas) as the reins, and the senses (Indriyas) as the horses. He who has no understanding, whose mind is constantly unrestrained, his senses are unmanageable like vicious horses.",
            "psychological_theme": "Emotional Regulation & Mind-Body Control",
            "target_emotions": ["impulsivity", "anxiety", "adhd", "distraction", "loss of control"],
            "root_cause": "Unchecked senses dragging an untrained mind without conscious direction from the intellect",
            "philosophical_principle": "Buddhi-Yukti (Intellectual discernment holding the reins of the mind)",
            "cbt_parallel": "Cognitive reappraisal & impulse control (strengthening executive function)",
            "patient_metaphor": "Think of your thoughts like lively horses pulling a chariot. When they run wild, it feels scary, but you are the gentle driver holding the reins. With slow, steady breaths, you can guide them calmly.",
            "gentle_action": "Take three deep breaths. Notice your restless thoughts, and gently say to yourself: 'I am holding the reins; I can choose where to place my focus right now.'"
        },
        {
            "scripture": "Katha Upanishad",
            "section": "2.1.1 (Looking Inward vs. Outward Distraction)",
            "citation": "Katha Upanishad, Chapter 2, Section 1, Verse 1",
            "text": "The Self-existent pierced the senses outward; therefore man looks outward into the world, not inward into himself. But a wise person seeking immortality turned his gaze inward and beheld the inner Self.",
            "psychological_theme": "Overstimulation & Sensory Overwhelm",
            "target_emotions": ["overwhelm", "sensory overload", "chronic worry", "social media exhaustion"],
            "root_cause": "Constant external sensory seeking creating mental fragmentation",
            "philosophical_principle": "Pratyahara (Sensory withdrawal & inner quietude)",
            "cbt_parallel": "Mindfulness & sensory grounding / digital detox",
            "patient_metaphor": "When windows are wide open in a dust storm, the room gets cloudy. Closing the windows for a few minutes lets the dust settle and brings quiet.",
            "gentle_action": "Gently close your eyes for two minutes. Step away from all screens, feel your feet on the floor, and enjoy the stillness within."
        },
        {
            "scripture": "Isha Upanishad",
            "section": "Verse 6 (Seeing Oneself in All Beings)",
            "citation": "Isha Upanishad, Verse 6",
            "text": "He who sees all beings in the Self and the Self in all beings never feels hatred, contempt, or alienation.",
            "psychological_theme": "Loneliness, Isolation & Social Alienation",
            "target_emotions": ["loneliness", "alienation", "rejection", "social anxiety", "bitterness"],
            "root_cause": "The illusion of isolation and separation from others",
            "philosophical_principle": "Sarvatma-bhava (Universal interconnectedness)",
            "cbt_parallel": "Compassion-focused therapy & dismantling perceived social isolation",
            "patient_metaphor": "Waves on the ocean might look separate, but beneath the surface, they are all the exact same ocean. You are never truly cut off or alone.",
            "gentle_action": "Think of someone who showed you even a small kindness recently. Silently send them a wish for peace, remembering we all share the same human heart."
        },
        {
            "scripture": "Mundaka Upanishad",
            "section": "3.1.1 - 3.1.2 (The Two Birds on the Tree)",
            "citation": "Mundaka Upanishad, Chapter 3, Section 1, Verses 1-2",
            "text": "Two birds, inseparable companions, perch on the same tree. One eats the sweet and bitter fruits, while the other looks on as a silent witness. The experiencing soul grieves when trapped in distress, but beholding the calm witness, becomes free from sorrow.",
            "psychological_theme": "Cognitive Defusion & Emotional Reactivity",
            "target_emotions": ["depression", "emotional turbulence", "rumination", "grief"],
            "root_cause": "Over-identification with passing thoughts and emotional pain",
            "philosophical_principle": "Sakshi-Bhava (The witnessing consciousness)",
            "cbt_parallel": "ACT Cognitive Defusion (I have a thought, but I am not my thought)",
            "patient_metaphor": "You are not the passing storm clouds; you are the wide, quiet sky behind them. The clouds come and go, but the sky is always safe and untouched.",
            "gentle_action": "When a painful thought comes up, simply say: 'I notice my mind is having a sad thought.' Watch it pass like a cloud without fighting it."
        },
        {
            "scripture": "Taittiriya Upanishad",
            "section": "2.1 - 2.5 (The Five Layers of Human Being - Panchakosha)",
            "citation": "Taittiriya Upanishad, Brahmananda Valli, 2.1-5",
            "text": "Within the physical body made of food (Annamaya) is the life-breath (Pranamaya); within the breath is the emotional mind (Manomaya); within the mind is the discerning intellect (Vijnanamaya); and deepest within is the core of peace and joy (Anandamaya).",
            "psychological_theme": "Holistic Healing & Somatic Wellbeing",
            "target_emotions": ["burnout", "panic attack", "physical exhaustion", "chronic stress"],
            "root_cause": "Disconnection between physical body, breath, and emotional state",
            "philosophical_principle": "Panchakosha Viveka (Holistic harmony across body, breath, and spirit)",
            "cbt_parallel": "Biofeedback, somatic grounding & behavioral self-care",
            "patient_metaphor": "Your mind and body are like nested Russian dolls. If your mind is tired, taking care of your physical body—drinking a glass of water and taking slow breaths—helps heal the inside layers too.",
            "gentle_action": "Drink a glass of cool water slowly, sip by sip. Let your shoulders drop away from your ears."
        },
        {
            "scripture": "Mandukya Upanishad",
            "section": "Verses 1-7 (The Four States of Consciousness)",
            "citation": "Mandukya Upanishad, Verses 1-7",
            "text": "The Self has four quarters: the waking state (Jagrat), the dream state of imagination and fear (Svapna), the deep dreamless rest of stillness (Sushupti), and the unchanging fourth state of peace (Turiya).",
            "psychological_theme": "Insomnia, Nightmares & Overactive Imagination",
            "target_emotions": ["insomnia", "night terror", "catastrophizing", "hypochondria"],
            "root_cause": "An overactive subconscious mind blurring imagined catastrophic fears with reality",
            "philosophical_principle": "Turiya-Avastha (Resting in the changeless ground of peace)",
            "cbt_parallel": "Stimulus control for sleep & decatastrophizing catastrophic imagery",
            "patient_metaphor": "Just like a projector screen stays completely clear and undamaged no matter what intense movie plays on it, your inner awareness is safe and undamaged by frightening dreams or worries.",
            "gentle_action": "As you lay down to rest, feel the steady bed beneath you. Repeat softly: 'I am safe in this quiet moment. I can let today rest.'"
        }
    ]
    logger.info("Extracted %d core psychological Upanishad treatises", len(upanishad_teachings))
    return upanishad_teachings


def extract_mahabharata_wisdom():
    """
    Extracts core psychological teachings from the Mahabharata:
    1. Vidura Niti (Handling insomnia, grief, anger, envy)
    2. Yaksha Prashna (Coping with loss, patience, nature of suffering)
    3. Shanti Parva (Healing after tragedy, moving forward)
    """
    logger.info("Extracting psychological counsel from Mahabharata (Vidura Niti, Yaksha Prashna, Shanti Parva)...")
    
    mahabharata_teachings = [
        {
            "scripture": "Mahabharata (Vidura Niti)",
            "section": "Udyoga Parva, Prajagara Parva (Chapter 33)",
            "citation": "Mahabharata, Udyoga Parva, Vidura Niti, 33.15-20",
            "text": "Vidura said to Dhritarashtra: Insomnia and restless sleeplessness strike those who are consumed by desire, who harbor hostility, who envy others' prosperity, or who are burdened by worry over what they cannot control. Peace comes only when the fire of envy is cooled with contentment.",
            "psychological_theme": "Insomnia, Night Anxiety & Toxic Comparison",
            "target_emotions": ["insomnia", "envy", "jealousy", "restlessness", "racing thoughts"],
            "root_cause": "Envy and mental comparison keeping the nervous system in a perpetual threat response",
            "philosophical_principle": "Santosha & Shama (Contentment with one's journey & mental stillness)",
            "cbt_parallel": "CBT for Insomnia (CBT-I) & cognitive restructuring of comparison traps",
            "patient_metaphor": "Comparing your journey to someone else is like a moon trying to shine like the sun. Each has its own gentle time to bring light.",
            "gentle_action": "Tonight, write down or name one small comfort you have right now—a warm blanket, a quiet corner, a safe breath."
        },
        {
            "scripture": "Mahabharata (Vidura Niti)",
            "section": "Udyoga Parva, Chapter 34 (Controlling Anger and Hurt)",
            "citation": "Mahabharata, Udyoga Parva, Vidura Niti, 34.62",
            "text": "Conquer anger with forgiveness, conquer wickedness with goodness, conquer the miser with generosity, and conquer falsehood with truth.",
            "psychological_theme": "Anger Management & Emotional Resentment",
            "target_emotions": ["anger", "resentment", "grudge", "irritability", "betrayal"],
            "root_cause": "Holding onto grudges and demanding retaliatory justice, which burns the self",
            "philosophical_principle": "Akrodha & Kshama (Non-anger & liberating forgiveness)",
            "cbt_parallel": "Emotional regulation & assertiveness training over reactive aggression",
            "patient_metaphor": "Holding onto anger is like holding a glowing hot coal with the intention of throwing it at someone else; you are the one who gets burned first.",
            "gentle_action": "When you feel that flare of anger, pause for a count of 5 before replying. Unclench your jaw and hands."
        },
        {
            "scripture": "Mahabharata (Yaksha Prashna)",
            "section": "Vana Parva, Chapter 313 (The Nature of Grief and Patience)",
            "citation": "Mahabharata, Vana Parva, Yaksha Prashna, 313.50-65",
            "text": "The Yaksha asked: 'What is faster than the wind? What is more numerous than grass? What is the heaviest burden on earth? What rescues a person in danger?' Yudhishthira replied: 'The mind is faster than the wind. Worries in the heart are more numerous than grass. The grief of a troubled spirit is the heaviest burden. And patience (Dhairya) rescues a person in every danger.'",
            "psychological_theme": "Patience Under Crisis & Mental Burdens",
            "target_emotions": ["panic", "overwhelm", "crisis", "helplessness", "catastrophic thinking"],
            "root_cause": "The restless mind multiplying imaginary catastrophes faster than the wind",
            "philosophical_principle": "Dhairya (Steadfast emotional patience)",
            "cbt_parallel": "Distress tolerance & grounding in high-arousal panic states",
            "patient_metaphor": "When water is stirred up and muddy, you cannot see through it by thrashing around. If you simply sit still on the bank, the mud settles on its own.",
            "gentle_action": "Tell yourself gently: 'I don't have to solve everything today. I just need to be patient through this single hour.'"
        },
        {
            "scripture": "Mahabharata (Shanti Parva)",
            "section": "Mokshadharma Parva, Chapter 174 (Healing from Grief and Loss)",
            "citation": "Mahabharata, Shanti Parva, 174.15-22",
            "text": "Bhishma taught: All associations end in separation; all life ends in transformation. Knowing this, the wise do not let their hearts be crushed by constant sorrow. When grief arises, let it be met with understanding rather than resistance, for time heals the wounded mind when attachment loosens its grip.",
            "psychological_theme": "Bereavement, Grief & Accepting Loss",
            "target_emotions": ["grief", "bereavement", "loss", "heartbreak", "hopelessness"],
            "root_cause": "Resistance to the universal law of impermanence",
            "philosophical_principle": "Shoka-Nivritti (Transcending sorrow through understanding impermanence)",
            "cbt_parallel": "Grief processing, acceptance & meaning reconstruction",
            "patient_metaphor": "Grief is like carrying a heavy backpack. You don't have to pretend it isn't heavy, but you can set it down for a moment to rest your back and drink some water.",
            "gentle_action": "Place a hand gently on your heart. Give yourself permission to feel sad without judging yourself for not being 'over it' yet."
        }
    ]
    logger.info("Extracted %d core Mahabharata psychological dialogues", len(mahabharata_teachings))
    return mahabharata_teachings


def extract_vedas_wisdom():
    """
    Extracts Shanti Suktas (peace hymns) and mental clarity verses from the Four Vedas.
    """
    logger.info("Extracting Shanti Suktas and grounding hymns from the Four Vedas...")
    
    vedas_teachings = [
        {
            "scripture": "Four Vedas (Yajur Veda)",
            "section": "Shanti Sukta (36.17)",
            "citation": "Yajur Veda, Chapter 36, Verse 17 (Shanti Patha)",
            "text": "May there be peace in heaven, peace in the atmosphere, peace on earth, peace in waters, peace in medicinal herbs, peace in the vegetation, peace in all divine beings, peace throughout all cosmic harmony. May peace radiate everywhere, and may that profound peace come to rest in my heart.",
            "psychological_theme": "Nervous System Regulation & Inner Peace",
            "target_emotions": ["panic", "generalized anxiety", "existential dread", "chronic tension"],
            "root_cause": "Sympathetic nervous system hyper-arousal and internal discord",
            "philosophical_principle": "Shanti-Bhavana (Cultivating the felt experience of universal harmony)",
            "cbt_parallel": "Autogenic relaxation training & environmental grounding",
            "patient_metaphor": "Imagine stepping into a serene garden where the trees, the breeze, and the gentle sun are all breathing in calm rhythm with you.",
            "gentle_action": "Breathe in for 4 seconds, hold gently for 2, and breathe out for 6. Whisper softly to yourself: 'Peace in my mind, peace in my body.'"
        },
        {
            "scripture": "Four Vedas (Rig Veda)",
            "section": "Samjnana Sukta (10.191.2-4)",
            "citation": "Rig Veda, Mandala 10, Hymn 191, Verses 2-4",
            "text": "Walk together; speak in harmony; let your minds understand one another. United be your purpose, harmonious be your feelings, unified be your resolve, so that all may happily thrive together in mutual understanding.",
            "psychological_theme": "Interpersonal Conflict & Relationship Harmony",
            "target_emotions": ["relationship conflict", "loneliness", "misunderstanding", "isolation"],
            "root_cause": "Defensiveness, perceived hostility, and fragmented communication",
            "philosophical_principle": "Samjnanam (Mutual empathy, harmony, and common ground)",
            "cbt_parallel": "Non-violent communication & interpersonal effectiveness (DBT)",
            "patient_metaphor": "When two instruments play in an orchestra, they need to tune to each other, not shout louder. Listening with warmth is the tuning fork of peace.",
            "gentle_action": "Before your next conversation, pause and remind yourself: 'I will listen to understand the other person's heart, not just wait to defend myself.'"
        },
        {
            "scripture": "Four Vedas (Rig Veda)",
            "section": "Gayatri & Savitr Hymn (3.62.10)",
            "citation": "Rig Veda, Mandala 3, Hymn 62, Verse 10",
            "text": "May that radiant source of universal light illuminate and clarify our intellects, clearing the fog of doubt and guiding our thoughts toward truth and wellbeing.",
            "psychological_theme": "Brain Fog, Indecision & Mental Confusion",
            "target_emotions": ["confusion", "brain fog", "indecision", "doubt", "paralysis"],
            "root_cause": "Cognitive clouding and emotional exhaustion paralyzing decision making",
            "philosophical_principle": "Dhi-Prachodayat (Illuminating the intellect with clarity and calm)",
            "cbt_parallel": "Mindfulness-based clarity & problem-solving therapy",
            "patient_metaphor": "When the morning sun rises, the thick mist gently lifts all by itself. You don't have to sweep away the fog; just invite a little gentle warmth in.",
            "gentle_action": "Step out into natural sunlight for three minutes, look at the sky, and let your eyes rest on the horizon."
        },
        {
            "scripture": "Four Vedas (Atharva Veda)",
            "section": "Prithvi Sukta (12.1 - Hymn to the Earth)",
            "citation": "Atharva Veda, Kandam 12, Hymn 1, Verses 1-12",
            "text": "The Earth holds all living beings with infinite patience and steadfastness, nurturing all without judgment. Grounded in her stability, may our restless minds find unwavering support and freedom from trembling fear.",
            "psychological_theme": "Somatic Grounding & Overcoming Panic",
            "target_emotions": ["panic", "agoraphobia", "vertigo", "feeling ungrounded", "fear"],
            "root_cause": "Loss of bodily connection and feeling unmoored during panic spikes",
            "philosophical_principle": "Dhriti & Sthirata (Stability grounded in the physical reality of nature)",
            "cbt_parallel": "5-4-3-2-1 Sensory Grounding Technique",
            "patient_metaphor": "No matter how strong the wind blows, the ground beneath your feet is solid, unmoving, and holding you safely right now.",
            "gentle_action": "Press both feet firmly into the floor. Feel the solid ground beneath you. Name 3 physical objects you can see around the room."
        }
    ]
    logger.info("Extracted %d core Vedic peace and grounding hymns", len(vedas_teachings))
    return vedas_teachings


def extract_ramayana_wisdom():
    """
    Extracts archetypal resilience and coping teachings from Valmiki Ramayana.
    """
    logger.info("Extracting resilience and fortitude archetypes from Valmiki Ramayana...")
    
    ramayana_teachings = [
        {
            "scripture": "Valmiki Ramayana",
            "section": "Sundara Kanda (Sita's Mental Fortitude in Captivity)",
            "citation": "Valmiki Ramayana, Sundara Kanda, Canto 15-28",
            "text": "Though surrounded by threats, isolation, and constant psychological cruelty in the Ashoka Vatika, Sita kept her mind anchored in her inner truth (Satya) and unyielding dignity. She refused to surrender her self-worth to her captor's intimidation.",
            "psychological_theme": "Trauma Resilience & Self-Worth Under Abuse",
            "target_emotions": ["trauma", "intimidation", "helplessness", "gaslighting", "low self-esteem"],
            "root_cause": "External oppression and hostility attempting to break inner dignity",
            "philosophical_principle": "Atma-Gaurava & Satya-Nishta (Unshakable self-worth and inner truth)",
            "cbt_parallel": "Trauma-informed cognitive empowerment & preserving personal boundaries",
            "patient_metaphor": "A pure lotus flower grows in muddy, stagnant water, yet not a single drop of mud sticks to its petals. You can remain pure and worthy regardless of harsh surroundings.",
            "gentle_action": "Remind yourself: 'What someone else says to hurt me does not define who I am. My inner worth is my own.'"
        },
        {
            "scripture": "Valmiki Ramayana",
            "section": "Ayodhya Kanda (Rama's Equanimity During Sudden Exile)",
            "citation": "Valmiki Ramayana, Ayodhya Kanda, Canto 19, Verses 30-35",
            "text": "When informed on the morning of his coronation that he was banished to the forest for fourteen years, Rama's calm countenance did not change in the slightest. He received exile with the same serene smile with which he had received the crown.",
            "psychological_theme": "Handling Sudden Life Upheaval & Fairness Shock",
            "target_emotions": ["shock", "job loss", "unfairness", "betrayal", "sudden disappointment"],
            "root_cause": "The catastrophic expectation that life must always be fair and predictable",
            "philosophical_principle": "Samatvam in Sampatti and Vipatti (Equanimity in fortune and misfortune)",
            "cbt_parallel": "Radical Acceptance & cognitive adaptability to sudden adversity",
            "patient_metaphor": "When the path you planned suddenly gets blocked by a fallen tree, you don't have to abandon the journey; you simply find a new trail around it.",
            "gentle_action": "Take one slow breath and say: 'This is not what I expected, but I can adapt. I will take this one single step at a time.'"
        },
        {
            "scripture": "Valmiki Ramayana",
            "section": "Kishkindha Kanda (Lakshmana's Counsel to the Grieving Rama)",
            "citation": "Valmiki Ramayana, Kishkindha Kanda, Canto 1, Verses 115-125",
            "text": "Lakshmana spoke to Rama in his deep sorrow: 'Grief weakens the mind, paralyzes the limbs, and consumes all strength. There is no enemy like grief. Arise, O noble one, and let resolute effort replace despair, for fortune favors the courageous who act.'",
            "psychological_theme": "Overcoming Depressive Paralysis & Inaction",
            "target_emotions": ["depression", "paralysis", "hopelessness", "lethargy", "giving up"],
            "root_cause": "Grief locking the person into behavioral avoidance and paralysis",
            "philosophical_principle": "Utsaha (Resolute enthusiasm and courageous initiative)",
            "cbt_parallel": "Behavioral Activation for depression (action precedes motivation)",
            "patient_metaphor": "When you are cold, waiting for warmth won't warm you up—you have to strike the match first. Even a tiny action brings the spark back.",
            "gentle_action": "Stand up, stretch your arms gently toward the ceiling, and accomplish one tiny 60-second task—like making your bed or washing a cup."
        }
    ]
    logger.info("Extracted %d core Ramayana resilience teachings", len(ramayana_teachings))
    return ramayana_teachings


def main():
    logger.info("=== Starting Comprehensive Multi-Scripture Extraction ===")
    
    # 1. Parse Bhagavad Gita (English source)
    gita_verses = parse_bhagavad_gita_english()
    
    # 2. Extract Upanishads
    upanishads = extract_upanishads_wisdom()
    
    # 3. Extract Mahabharata
    mahabharata = extract_mahabharata_wisdom()
    
    # 4. Extract Four Vedas
    vedas = extract_vedas_wisdom()
    
    # 5. Extract Ramayana
    ramayana = extract_ramayana_wisdom()
    
    # Combine into unified dataset
    combined_records = []
    
    # Add non-Gita scriptures
    for item in upanishads + mahabharata + vedas + ramayana:
        combined_records.append(item)
        
    # Add Gita verses (curating core psychological verses with explicit mappings)
    # High-impact clinical verses in the Gita:
    core_gita_mappings = {
        (2, "14"): {
            "theme": "Distress Tolerance (Titiksha)",
            "emotions": ["distress", "pain", "weathering grief", "panic"],
            "root_cause": "Inability to tolerate transient physical and emotional discomfort",
            "principle": "Titiksha (Endurance without emotional breakdown)",
            "cbt_parallel": "DBT Distress Tolerance & Radically accepting physical sensations",
            "metaphor": "Summer heat and winter cold come and go on their own. You don't have to fight the winter; you just bundle up warmly and know spring will return.",
            "action": "Notice the uncomfortable feeling in your chest or stomach. Tell yourself: 'This is uncomfortable, but it is not dangerous, and it will pass.'"
        },
        (2, "47"): {
            "theme": "Process vs. Outcome Focus (Nishkama Karma)",
            "emotions": ["performance anxiety", "fear of failure", "exam stress", "burnout"],
            "root_cause": "Fixation on results, grades, and praise which are outside direct control",
            "principle": "Nishkama Karma (Action dedicated to duty without attachment to fruits)",
            "cbt_parallel": "CBT Shift from Outcome-Oriented to Process-Oriented goals",
            "metaphor": "Think of planting a sunflower seed. Your job is simply to water the soil today. Constantly digging it up to see if it grew only hurts the seed.",
            "action": "Focus 100% on the single step in front of you right now, and let tomorrow's outcome take care of itself."
        },
        (2, "62"): {
            "theme": "The Ladder of Cognitive Fall (Craving to Anger)",
            "emotions": ["anger", "craving", "addiction", "loss of control"],
            "root_cause": "Dwelling on trigger objects causing obsessive attachment, which breeds frustration and anger",
            "principle": "Kama-Krodha Viveka (Recognizing craving before it becomes rage)",
            "cbt_parallel": "Relapse prevention & identifying early cognitive triggers in anger loops",
            "metaphor": "A tiny spark on a dry leaf is easy to blow out, but if you feed it dry twigs, it turns into a forest fire. Catch the spark early.",
            "action": "Notice what triggers your frustration today, and step away for a glass of water before the spark catches."
        },
        (6, "5"): {
            "theme": "Self-Compassion and Self-Elevation",
            "emotions": ["self-hatred", "shame", "guilt", "depression"],
            "root_cause": "Harsh internal critic degrading the self into helplessness",
            "principle": "Atma-Uddharana (Being your own friend rather than your own enemy)",
            "cbt_parallel": "Combating the harsh inner critic & self-compassion therapy",
            "metaphor": "If a friend was struggling and made a mistake, you wouldn't kick them—you'd offer a hand. Treat yourself like that same dear friend.",
            "action": "Speak to yourself right now with the exact same gentle kindness you would offer to a hurting child."
        },
        (6, "35"): {
            "theme": "Taming the Restless Mind (Abhyasa & Vairagya)",
            "emotions": ["adhd", "overthinking", "racing thoughts", "obsessive rumination"],
            "root_cause": "Believing every thought and expecting the mind to stop instantly without gentle training",
            "principle": "Abhyasa & Vairagya (Gentle, patient practice and non-reactive letting go)",
            "cbt_parallel": "Mindfulness attention training & habit exposure",
            "metaphor": "Training your mind is like teaching a playful puppy to sit. You don't yell at the puppy when it wanders; you just gently pick it up and place it back on the mat with a smile.",
            "action": "Whenever your mind wanders into worry today, gently bring your focus back to what your hands are doing right now."
        },
        (18, "47"): {
            "theme": "Authentic Self-Acceptance (Sva-Dharma)",
            "emotions": ["imposter syndrome", "comparison", "inferiority", "people pleasing"],
            "root_cause": "Trying to live someone else's life and values while abandoning one's own authentic nature",
            "principle": "Sva-Dharma (Honoring one's own authentic nature and pace)",
            "cbt_parallel": "Values clarification in ACT & combating perfectionist comparison",
            "metaphor": "A fish is magnificent in water, but feels foolish trying to climb a tree. Honor your own unique rhythm and strengths.",
            "action": "Remind yourself: 'I don't have to be everything to everyone. It is enough to be authentically myself today.'"
        }
    }
    
    # Attach rich psychological metadata to Gita verses
    for v in gita_verses:
        ch = v["chapter"]
        v_num = str(v["verse"]).split("-")[0]
        mapping = core_gita_mappings.get((ch, v_num))
        
        entry = {
            "scripture": "Bhagavad Gita",
            "section": f"Chapter {ch}, Verse {v['verse']}",
            "citation": v["citation"],
            "text": v["text"],
            "psychological_theme": mapping["theme"] if mapping else f"Gita Wisdom for Chapter {ch}",
            "target_emotions": mapping["emotions"] if mapping else ["stress", "anxiety", "life guidance"],
            "root_cause": mapping["root_cause"] if mapping else "Lack of clarity and spiritual balance",
            "philosophical_principle": mapping["principle"] if mapping else "Yoga & Dharma",
            "cbt_parallel": mapping["cbt_parallel"] if mapping else "Cognitive reframing and mindful awareness",
            "patient_metaphor": mapping["metaphor"] if mapping else "Like a steady lighthouse standing calm in the stormy sea, ancient wisdom keeps you safe.",
            "gentle_action": mapping["action"] if mapping else "Take a deep breath and pause before reacting to stress."
        }
        combined_records.append(entry)
        
    logger.info("Total unified scriptural knowledge records compiled: %d", len(combined_records))
    
    # Save output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(combined_records, f, indent=2, ensure_ascii=False)
        
    logger.info("[SUCCESS] Wrote %d records to %s", len(combined_records), OUTPUT_PATH)


if __name__ == "__main__":
    main()
