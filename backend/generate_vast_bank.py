import os
import json
import asyncio
from dotenv import load_dotenv

# Load env vars to get GROQ_API_KEY
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("GROQ_API_KEY not found in .env")
    exit(1)

from groq import AsyncGroq
client = AsyncGroq(api_key=groq_api_key)

BASE_QUESTIONS = {
    "stress": [
        {"id": "s1", "text": "In the last month, how often have you been upset because of something that happened unexpectedly?", "is_reverse": False},
        {"id": "s2", "text": "In the last month, how often have you felt that you were unable to control the important things in your life?", "is_reverse": False},
        {"id": "s3", "text": "In the last month, how often have you felt nervous and stressed?", "is_reverse": False},
        {"id": "s4", "text": "In the last month, how often have you felt confident about your ability to handle your personal problems?", "is_reverse": True},
        {"id": "s5", "text": "In the last month, how often have you felt that things were going your way?", "is_reverse": True},
        {"id": "s6", "text": "In the last month, how often have you found that you could not cope with all the things that you had to do?", "is_reverse": False},
        {"id": "s7", "text": "In the last month, how often have you been able to control irritations in your life?", "is_reverse": True},
        {"id": "s8", "text": "In the last month, how often have you felt that you were on top of things?", "is_reverse": True},
        {"id": "s9", "text": "In the last month, how often have you been angered because of things that happened that were outside of your control?", "is_reverse": False},
        {"id": "s10", "text": "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?", "is_reverse": False},
    ],
    "burnout": [
        {"id": "b1", "text": "I feel emotionally drained by my work.", "is_reverse": False},
        {"id": "b2", "text": "Working with people all day long requires a great deal of effort.", "is_reverse": False},
        {"id": "b3", "text": "I feel like my work is breaking me down.", "is_reverse": False},
        {"id": "b4", "text": "I feel frustrated by my work.", "is_reverse": False},
        {"id": "b5", "text": "I feel I work too hard at my job.", "is_reverse": False},
        {"id": "b6", "text": "It stresses me too much to work in direct contact with people.", "is_reverse": False},
        {"id": "b7", "text": "I feel like I’m at the end of my rope.", "is_reverse": False},
        {"id": "b8", "text": "I often feel exhausted at the end of the day.", "is_reverse": False},
    ],
    "wellbeing": [
        {"id": "w1", "text": "I’ve been feeling optimistic about the future", "is_reverse": True},
        {"id": "w2", "text": "I’ve been feeling useful", "is_reverse": True},
        {"id": "w3", "text": "I’ve been feeling relaxed", "is_reverse": True},
        {"id": "w4", "text": "I’ve been feeling interested in other people", "is_reverse": True},
        {"id": "w5", "text": "I’ve had energy to spare", "is_reverse": True},
        {"id": "w6", "text": "I’ve been dealing with problems well", "is_reverse": True},
        {"id": "w7", "text": "I’ve been thinking clearly", "is_reverse": True},
        {"id": "w8", "text": "I’ve been feeling good about myself", "is_reverse": True},
        {"id": "w9", "text": "I’ve been feeling confident", "is_reverse": True},
        {"id": "w10", "text": "I’ve been able to make up my own mind about things", "is_reverse": True},
        {"id": "w11", "text": "I’ve been feeling cheerful", "is_reverse": True},
    ],
    "distress": [
        {"id": "d1", "text": "I experience nervousness or shakiness inside", "is_reverse": False},
        {"id": "d2", "text": "I feel suddenly scared for no reason", "is_reverse": False},
        {"id": "d3", "text": "I feel fearful", "is_reverse": False},
        {"id": "d4", "text": "I experience spells of terror or panic", "is_reverse": False},
        {"id": "d5", "text": "I feel so restless I can't sit still", "is_reverse": False},
        {"id": "d6", "text": "I worry more than I would like.", "is_reverse": False},
        {"id": "d7", "text": "I have difficulty concentrating.", "is_reverse": False},
        {"id": "d8", "text": "I become irritated easily.", "is_reverse": False},
        {"id": "d9", "text": "My thoughts sometimes feel difficult to control.", "is_reverse": False},
        {"id": "d10", "text": "I feel mentally exhausted.", "is_reverse": False},
    ],
    "recovery": [
        {"id": "r1", "text": "I wake up feeling refreshed.", "is_reverse": True},
        {"id": "r2", "text": "I get enough sleep most nights.", "is_reverse": True},
        {"id": "r3", "text": "I feel physically rested.", "is_reverse": True},
        {"id": "r4", "text": "I struggle to fall asleep.", "is_reverse": False},
        {"id": "r5", "text": "I wake up frequently during the night.", "is_reverse": False},
        {"id": "r6", "text": "Fatigue affects my daily performance.", "is_reverse": False},
    ],
    "work_life": [
        {"id": "wl1", "text": "My current working hours / patterns suit my personal circumstances", "is_reverse": True},
        {"id": "wl2", "text": "My employer provides adequate flexibility for me to fit work in around my family life", "is_reverse": True},
        {"id": "wl3", "text": "I have enough time for personal activities.", "is_reverse": True},
        {"id": "wl4", "text": "My work allows me to maintain a healthy lifestyle.", "is_reverse": True},
        {"id": "wl5", "text": "I can disconnect from work during personal time.", "is_reverse": True},
        {"id": "wl6", "text": "Work often interferes with my personal life.", "is_reverse": False},
        {"id": "wl7", "text": "I have adequate time to recover between workdays.", "is_reverse": True},
    ]
}

async def generate_variations(domain, item):
    prompt = f"""
    You are an expert psychological assessment designer.
    Take the following source question from a clinical assessment ({domain}):
    "{item['text']}"

    Generate exactly 4 rephrased variations of this question. The variations MUST measure the exact same psychological construct, but use different vocabulary and sentence structure.
    Output ONLY a JSON list of 4 strings. No markdown formatting, no explanations.
    ["variation 1", "variation 2", "variation 3", "variation 4"]
    """
    try:
        response = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        variations = json.loads(content)
        # Combine original with variations
        return [item['text']] + variations
    except Exception as e:
        print(f"Error generating for {item['id']}: {e}")
        return [item['text']] * 5 # fallback

async def main():
    print("Generating vast bank...")
    vast_bank = {}
    
    for domain, questions in BASE_QUESTIONS.items():
        print(f"Processing domain: {domain}")
        vast_bank[domain] = []
        
        # Process sequentially to avoid rate limits
        for q in questions:
            variations = await generate_variations(domain, q)
            vast_bank[domain].append({
                "id": q["id"],
                "is_reverse": q["is_reverse"],
                "variations": variations
            })
            print(f"  Generated 5 variations for {q['id']}")
            
    with open(r"D:\PsyPredict\backend\app\data\vast_question_bank.json", "w") as f:
        json.dump(vast_bank, f, indent=2)
        
    print("Vast bank generated successfully at vast_question_bank.json")

if __name__ == "__main__":
    asyncio.run(main())
