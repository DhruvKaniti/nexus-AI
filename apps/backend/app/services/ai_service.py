import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

# Initialize Gemini client (using new google.genai package)
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_model = None
if gemini_api_key:
    try:
        from google import genai
        gemini_client = genai.Client(api_key=gemini_api_key)
        gemini_model = 'gemini-3.5-flash'  # Use latest model
    except ImportError:
        print("Warning: google.genai package not found. Gemini features disabled.")
        gemini_model = None

async def get_gemini_recommendation(crisis):
    """Get recommendation from Gemini API"""
    if not gemini_model:
        print("Gemini API: Model not initialized (no API key)")
        return None
    
    try:
        # Safely escape any special characters in crisis data
        title = crisis.get('title', 'Unknown').replace('"', '\\"').replace('\n', ' ')
        location = crisis.get('location', 'Unknown').replace('"', '\\"').replace('\n', ' ')
        category = crisis.get('category', 'Unknown').replace('"', '\\"').replace('\n', ' ')
        severity = crisis.get('severity', 'Unknown').replace('"', '\\"').replace('\n', ' ')
        description = crisis.get('description', 'No description provided').replace('"', '\\"').replace('\n', ' ')
        
        prompt = f"""Analyze this crisis event and provide a threat assessment.

Event: {title} in {location}
Category: {category}
Severity: {severity}
Impact Score: {crisis.get('impact_score', 'N/A')}
Confidence: {crisis.get('confidence', 'N/A')}
Description: {description}"""

        print(f"Gemini API: Calling API with model {gemini_model}...")
        
        # Use new google.genai API with JSON-only response
        from google.genai import types
        response = gemini_client.models.generate_content(
            model=gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000,
                response_mime_type="application/json",
            )
        )
        content = response.text.strip()
        print(f"Gemini API: Received response: {content[:100]}...")
        
        # Parse JSON response
        try:
            result = json.loads(content)
            print(f"Gemini API: Successfully parsed JSON response")
            return result
        except json.JSONDecodeError as e:
            # If direct parsing fails, try to extract JSON
            print(f"Gemini API: JSON parsing failed, attempting extraction: {e}")
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start != -1 and json_end != -1:
                content = content[json_start:json_end+1]
                try:
                    result = json.loads(content)
                    print(f"Gemini API: Successfully extracted and parsed JSON")
                    return result
                except json.JSONDecodeError:
                    pass
            print(f"Gemini API: Failed to parse response")
            return None
    except Exception as e:
        print(f"Gemini API error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def analyze_crisis(crisis):
    """Analyze crisis using OpenAI for general agents and Gemini for recommendations"""
    
    # Get Gemini recommendation first
    gemini_result = await get_gemini_recommendation(crisis)
    
    # Prepare the prompt for OpenAI (for other agents)
    prompt = f"""You are an AI crisis analysis system. Analyze the following crisis and provide findings from 4 specialized agents (excluding recommendations).

Crisis Details:
- Name: {crisis.get('title', crisis.get('name', 'Unknown'))}
- Location: {crisis.get('location', crisis.get('place', 'Unknown'))}
- Severity: {crisis.get('severity', 'Unknown')}
- Category: {crisis.get('category', crisis.get('tone', 'Unknown'))}
- Description: {crisis.get('description', 'No description')}

Provide findings in this exact JSON format:
{{
  "agents": [
    {{
      "name": "Satellite Intelligence Agent",
      "finding": "Detailed finding about satellite/imagery analysis specific to this crisis",
      "confidence": 85,
      "risk": "High"
    }},
    {{
      "name": "News Intelligence Agent",
      "finding": "Detailed finding about news/social media analysis specific to this crisis",
      "confidence": 78,
      "risk": "Medium"
    }},
    {{
      "name": "Supply Chain Agent",
      "finding": "Detailed finding about supply chain impact specific to this crisis",
      "confidence": 82,
      "risk": "High"
    }},
    {{
      "name": "Economic Impact Agent",
      "finding": "Detailed finding about economic impact specific to this crisis",
      "confidence": 75,
      "risk": "Medium"
    }}
  ]
}}

Make findings specific to the crisis details provided. Be professional and analytical."""

    try:
        # Get OpenAI results for the 4 agents
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a crisis analysis AI. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        import json
        content = response.choices[0].message.content
        
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content.strip())
        
        # Add Recommendation Agent with Gemini result or fallback
        if gemini_result:
            recommendation_agent = {
                "name": "Recommendation Agent",
                "finding": gemini_result.get('threat_assessment', 'Analysis complete'),
                "confidence": gemini_result.get('confidence_score', 75),
                "risk": crisis.get('severity', 'Medium'),
                "reasoning": gemini_result.get('analyst_summary', ''),
                "recommendation": gemini_result.get('recommended_actions', 'Continue monitoring the situation.')
            }
        else:
            # Fallback to template if Gemini fails
            recommendation_agent = {
                "name": "Recommendation Agent",
                "finding": "Analysis complete. Multiple factors require monitoring.",
                "confidence": 70,
                "risk": crisis.get('severity', 'Medium'),
                "reasoning": "Using fallback analysis due to API limitations.",
                "recommendation": f"Continue monitoring {crisis.get('location', 'the area')} and prepare contingency protocols for {crisis.get('title', 'the situation').lower()}."
            }
        
        result["agents"].append(recommendation_agent)
        return result
        
    except Exception as e:
        # Fallback to mock data if AI fails completely
        return {
            "agents": [
                {
                    "name": "Satellite Intelligence Agent",
                    "finding": f"Satellite analysis of {crisis.get('location', 'the area')} shows activity patterns consistent with {crisis.get('title', 'the event').lower()}.",
                    "confidence": 75,
                    "risk": crisis.get('severity', 'Medium')
                },
                {
                    "name": "News Intelligence Agent",
                    "finding": f"News sources report developments related to {crisis.get('title', 'the event')} in {crisis.get('location', 'the area')}.",
                    "confidence": 70,
                    "risk": "Medium"
                },
                {
                    "name": "Supply Chain Agent",
                    "finding": f"Supply chain routes near {crisis.get('location', 'the area')} may be affected by {crisis.get('title', 'the event').lower()}.",
                    "confidence": 72,
                    "risk": crisis.get('severity', 'Medium')
                },
                {
                    "name": "Economic Impact Agent",
                    "finding": f"Economic analysis suggests {crisis.get('title', 'the event')} could impact regional operations.",
                    "confidence": 68,
                    "risk": "Medium"
                },
                {
                    "name": "Recommendation Agent",
                    "finding": "Analysis complete. Multiple factors require monitoring.",
                    "confidence": 70,
                    "risk": crisis.get('severity', 'Medium'),
                    "reasoning": "Using fallback analysis due to API limitations.",
                    "recommendation": f"Continue monitoring {crisis.get('location', 'the area')} and prepare contingency protocols for {crisis.get('title', 'the situation').lower()}."
                }
            ]
        }