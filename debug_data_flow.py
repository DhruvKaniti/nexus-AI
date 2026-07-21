"""
Debug script to trace the entire data flow from backend to frontend
"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.event_aggregator import EventAggregator

def test_backend():
    """Test backend aggregator"""
    print("=" * 70)
    print("STEP 1: Testing Backend EventAggregator")
    print("=" * 70)
    
    aggregator = EventAggregator(newsapi_key=None)
    result = asyncio.run(aggregator.aggregate(limit=5))
    
    print(f"\n✅ Backend Result:")
    print(f"   Count: {result.get('count')}")
    print(f"   Sources: {result.get('sources_used')}")
    print(f"   Timestamp: {result.get('timestamp')}")
    
    if result.get('errors'):
        print(f"\n⚠️ Errors encountered:")
        for error in result['errors']:
            print(f"   - {error}")
    
    if result.get('events'):
        print(f"\n📰 Events returned:")
        for i, event in enumerate(result['events'], 1):
            print(f"\n   {i}. {event.get('title')}")
            print(f"      Source: {event.get('source')}")
            print(f"      Category: {event.get('category')}")
            print(f"      Location: {event.get('location')}")
            print(f"      Coordinates: ({event.get('latitude')}, {event.get('longitude')})")
            print(f"      Published: {event.get('published_at')}")
            print(f"      Severity: {event.get('severity')}")
    else:
        print(f"\n❌ No events returned!")
        if result.get('error'):
            print(f"   Error: {result.get('error')}")
    
    return result

def simulate_frontend_processing(api_response: dict):
    """Simulate what the frontend does with the API response"""
    print("\n" + "=" * 70)
    print("STEP 2: Simulating Frontend Processing")
    print("=" * 70)
    
    # This is what the frontend code does:
    # const data = await response.json()
    data = api_response
    
    print(f"\n📦 Raw API response received by frontend:")
    print(f"   Has error field: {'error' in data}")
    print(f"   Events count: {len(data.get('events', []))}")
    print(f"   Sources used: {data.get('sources_used', [])}")
    
    # Check for API error response
    if data.error:
        print(f"\n❌ Frontend would throw error: {data.error}")
        return None
    
    # Get events
    events = data.events || []
    print(f"\n📊 Events extracted: {len(events)}")
    
    if len(events) === 0:
        print(f"❌ Frontend would throw: No live events available")
        return None
    
    # Simulate crisis conversion
    print(f"\n🔄 Converting events to crisis objects...")
    new_crises = []
    
    for i, event in enumerate(events):
        print(f"\n   Event {i+1}: {event.get('title')}")
        
        # Frontend geocodes again (redundant but that's what it does)
        # For this test, we'll use the coordinates from backend
        lat = event.get('latitude')
        lng = event.get('longitude')
        
        crisis = {
            'title': event.get('title'),
            'place': event.get('location'),
            'severity': event.get('severity', 'Watch'),
            'tone': 'blue',  # Default in frontend
            'time': 'Just now',
            'lat': lat or 0,
            'lng': lng or 0,
        }
        
        new_crises.append(crisis)
        print(f"   ✅ Converted to crisis: {crisis['title']} at ({crisis['lat']}, {crisis['lng']})")
    
    print(f"\n📋 Final crises array that would be set:")
    for i, c in enumerate(new_crises, 1):
        print(f"   {i}. {c['title']} - {c['place']}")
    
    return new_crises

def analyze_issue():
    """Analyze why default crises might still be showing"""
    print("\n" + "=" * 70)
    print("STEP 3: Analysis - Why Default Crises Might Still Show")
    print("=" * 70)
    
    print("\n🔍 Possible Issues:")
    print("\n1. BACKEND NOT RETURNING EVENTS:")
    print("   - Check if EventAggregator is actually fetching data")
    print("   - Check if sources are accessible")
    print("   - Check for errors in source fetching")
    
    print("\n2. FRONTEND NOT CALLING API:")
    print("   - Check if startGlobalScan() is being triggered")
    print("   - Check if fetch() is executing")
    print("   - Check browser console for errors")
    
    print("\n3. FRONTEND APPENDING INSTEAD OF REPLACING:")
    print("   - OLD CODE: setCrises((prev) => [...prev, crisis])")
    print("   - NEW CODE: setCrises(newCrises) ← Should replace")
    print("   - Check if new code is actually deployed")
    
    print("\n4. REACT STATE NOT UPDATING:")
    print("   - Check if setCrises() is actually being called")
    print("   - Check for React rendering issues")
    print("   - Check if component is re-rendering")
    
    print("\n5. DEFAULT CRISES HARDCODED IN UI:")
    print("   - Check CrisisPanel component")
    print("   - initialCrises is used directly in render")
    print("   - Need to verify it's using 'crises' prop not 'initialCrises'")

if __name__ == "__main__":
    # Test backend
    backend_result = test_backend()
    
    # Simulate frontend processing
    if backend_result:
        crises = simulate_frontend_processing(backend_result)
        
        if crises and len(crises) > 0:
            print("\n" + "=" * 70)
            print("✅ SUCCESS: Backend is returning live events")
            print("=" * 70)
            print(f"\nThe backend returned {len(crises)} live events.")
            print(f"The frontend should replace default crises with these.")
            print(f"\nIf you still see default crises, check:")
            print(f"  1. Browser console for JavaScript errors")
            print(f"  2. Network tab to see if API is being called")
            print(f"  3. React DevTools to see if state is updating")
        else:
            print("\n" + "=" * 70)
            print("❌ ISSUE: Backend not returning events")
            print("=" * 70)
            print(f"\nThe backend returned no events.")
            print(f"This is why default crises are still showing.")
    
    # Analysis
    analyze_issue()
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Check backend logs when you click 'Start Global Scan'")
    print("   - Look for '🔍 Global scan requested'")
    print("   - Look for source fetch results")
    print("   - Look for '✅ Global scan complete'")
    print("\n2. Check browser console (F12) when you click 'Start Global Scan'")
    print("   - Look for '🔍 Starting global scan...'")
    print("   - Look for '📡 API Response status'")
    print("   - Look for '📦 Raw API response'")
    print("   - Look for '🔄 Replacing all crises'")
    print("\n3. Check Network tab in browser DevTools")
    print("   - Look for /api/global-scan?limit=5 request")
    print("   - Check response status and body")
    print("   - Verify it's returning events")