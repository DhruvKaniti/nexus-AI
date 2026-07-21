"""Test Gemini API integration for Recommendation Agent"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_service import analyze_crisis

async def test_gemini_integration():
    """Test the Gemini API integration"""
    print("🧪 Testing Gemini API Integration...")
    print("=" * 60)
    
    # Sample crisis event
    test_crisis = {
        "title": "Major Flooding in Southeast Asia",
        "location": "Bangladesh",
        "category": "Natural Disaster",
        "severity": "High",
        "impact_score": 8.5,
        "confidence": 0.92,
        "description": "Severe monsoon flooding has affected millions of people in Bangladesh, with widespread damage to infrastructure and agriculture."
    }
    
    print(f"\n📋 Test Event:")
    print(f"   Title: {test_crisis['title']}")
    print(f"   Location: {test_crisis['location']}")
    print(f"   Category: {test_crisis['category']}")
    print(f"   Severity: {test_crisis['severity']}")
    
    print(f"\n🚀 Running analysis...")
    result = await analyze_crisis(test_crisis)
    
    print(f"\n✅ Analysis Complete!")
    print(f"   Total agents: {len(result.get('agents', []))}")
    
    # Check for Recommendation Agent
    recommendation_agent = None
    for agent in result.get('agents', []):
        if agent['name'] == 'Recommendation Agent':
            recommendation_agent = agent
            break
    
    if recommendation_agent:
        print(f"\n🎯 Recommendation Agent Results:")
        print(f"   Finding: {recommendation_agent.get('finding', 'N/A')[:100]}...")
        print(f"   Confidence: {recommendation_agent.get('confidence', 'N/A')}%")
        print(f"   Risk: {recommendation_agent.get('risk', 'N/A')}")
        print(f"   Reasoning: {recommendation_agent.get('reasoning', 'N/A')[:100]}...")
        print(f"   Recommendation: {recommendation_agent.get('recommendation', 'N/A')[:100]}...")
        
        # Check if Gemini was used
        if 'Using fallback' in recommendation_agent.get('reasoning', ''):
            print(f"\n⚠️  Gemini API: Using fallback (API not configured or failed)")
        else:
            print(f"\n✅ Gemini API: Successfully integrated!")
    else:
        print(f"\n❌ Recommendation Agent not found in results!")
    
    print(f"\n📊 All Agents:")
    for agent in result.get('agents', []):
        print(f"   - {agent['name']}: {agent.get('confidence', 'N/A')}% confidence")
    
    print("\n" + "=" * 60)
    
    # Save full result to file for inspection
    import json
    with open('test_gemini_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Full results saved to: test_gemini_result.json")

if __name__ == "__main__":
    asyncio.run(test_gemini_integration())