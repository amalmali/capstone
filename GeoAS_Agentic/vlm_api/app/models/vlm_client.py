# app/models/vlm_client.py

from openai import OpenAI
import os


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
You are an AI system specialized in detecting environmental violations from images.

Your task is to objectively analyze the image and report only what is visible.
Do not give advice, warnings, or explanations.
Return JSON only.
"""

USER_PROMPT = """
Analyze the provided image and determine whether it shows an environmental violation.

Possible violation types:
- Illegal Hunting
- Illegal Camping
- Illegal Logging
- Off-road Driving
- Pollution
- No Violation

Violation severity rules:
- Low: minimal activity, 1 person, no harmful tools
- Medium: multiple people OR vehicles OR camping equipment
- High: weapons, hunting activity, heavy machinery, visible environmental damage
- If violation_type is "No Violation", severity must be "Low"

Instructions:
- Choose the most appropriate violation type based only on visible evidence.
- Assign a violation severity (Low, Medium, High).
- Count the number of visible people.
- List clearly visible objects related to the activity.
- Provide a confidence score between 0.0 and 1.0.

If no violation is detected:
- violation_type = "No Violation"
- violation_severity = "Low"
- people_count = 0
- detected_objects = []
- confidence between 0.0 and 0.3

Return ONLY valid JSON in the following format:

{
  "violation_type": "",
  "violation_severity": "",
  "people_count": 0,
  "detected_objects": [],
  "confidence": 0.0
}
"""

def analyze_image(image_base64: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
