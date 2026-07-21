# Gemini API Integration for Recommendation Agent

## Overview
The Gemini API has been successfully integrated into the NEXUS backend to power the Recommendation Agent with AI-driven threat assessments and recommendations.

## Changes Made

### 1. Backend Environment Configuration
**File: `apps/backend/.env`**
- Added `GEMINI_API_KEY` environment variable
- API key is stored securely in backend only
- Never exposed to frontend

### 2. Dependencies
**File: `apps/backend/requirements.txt`**
- Added `google-genai>=0.3.0` package
- Uses the new Google GenAI SDK (replaces deprecated google-generativeai)

### 3. AI Service Implementation
**File: `apps/backend/app/services/ai_service.py`**
- Added `get_gemini_recommendation()` function to call Gemini API
- Modified `analyze_crisis()` to use Gemini for Recommendation Agent
- Implemented fallback behavior when Gemini API is unavailable
- Maintains backward compatibility with existing OpenAI integration

## Flow

1. **User selects an intelligence event** in the frontend
2. **Backend receives event data** with the following fields:
   - title
   - location
   - category
   - severity
   - impact_score
   - confidence
   - description

3. **Gemini API processes the event** and returns:
   - threat_assessment
   - recommended_actions
   - confidence_score
   - analyst_summary

4. **Backend formats the response** to match LiveFindings.tsx format:
   ```json
   {
     "name": "Recommendation Agent",
     "finding": "threat_assessment from Gemini",
     "confidence": "confidence_score from Gemini",
     "risk": "severity from event",
     "reasoning": "analyst_summary from Gemini",
     "recommendation": "recommended_actions from Gemini"
   }
   ```

5. **Frontend displays** the findings in LiveFindings component

## Fallback Behavior

If Gemini API fails or is not configured:
- Uses template-based fallback recommendations
- Maintains all existing functionality
- No breaking changes to frontend
- Graceful degradation with user-friendly message

## Security

- ✅ API key stored in backend .env file only
- ✅ .env file is gitignored (line 13 of .gitignore)
- ✅ API key never sent to frontend
- ✅ All AI processing happens server-side

## Testing

Run the test script to verify integration:
```bash
cd apps/backend
python test_gemini.py
```

The test will show:
- ✅ "Gemini API: Successfully integrated!" if API call succeeds
- ⚠️ "Gemini API: Using fallback" if API key is not configured OR if Gemini service is temporarily unavailable (503 errors are handled gracefully)

## Configuration

To enable Gemini API:
1. Get an API key from https://makersuite.google.com/app/apikey
2. Add to `apps/backend/.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Restart the backend server

## Response Format

The integration maintains the existing response format used by LiveFindings.tsx:
- `agent`: Agent name (string)
- `summary`: Finding text (string)
- `confidence`: Confidence percentage (number)
- `timestamp`: Time of analysis (Date)
- `reasoning`: Analyst reasoning (string, optional)

## No Breaking Changes

- ✅ All existing agents continue to work
- ✅ Frontend components unchanged
- ✅ Map functionality unchanged
- ✅ Event pipeline unchanged
- ✅ UI layout unchanged
- ✅ Only the Recommendation Agent is upgraded