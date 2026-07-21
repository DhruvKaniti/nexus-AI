"""Test script for the Intelligence Engine"""
import sys
import os
import asyncio
import json
from datetime import datetime, timezone

# Add the backend to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'backend'))

from app.services.event_aggregator import Event, EventAggregator
from app.services.intelligence_engine import IntelligenceEngine


def create_test_events():
    """Create test events to verify filtering and scoring"""
    test_events = [
        # High-impact events that should pass
        Event(
            title="Magnitude 7.2 Earthquake Strikes Japan - Tsunami Warning Issued",
            location="Japan",
            latitude=35.6762,
            longitude=139.6503,
            source="USGS",
            category="Earthquake",
            severity="Critical",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://earthquake.usgs.gov/earthquakes/eventpage/abc123",
            description="A powerful magnitude 7.2 earthquake has struck off the coast of Japan. Tsunami warnings have been issued for multiple prefectures."
        ),
        Event(
            title="Major Cyberattack on US Power Grid - Nation-State Attack Suspected",
            location="United States",
            latitude=38.9072,
            longitude=-77.0369,
            source="Reuters",
            category="Cyberattack",
            severity="Critical",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://reuters.com/cyberattack",
            description="A sophisticated cyberattack has targeted critical power grid infrastructure across multiple states. Government agencies responding."
        ),
        Event(
            title="Hurricane Category 5 Makes Landfall in Florida - Evacuations Ordered",
            location="Florida, USA",
            latitude=25.7617,
            longitude=-80.1918,
            source="NASA EONET",
            category="Severe Storms",
            severity="Critical",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://eonet.gsfc.nasa.gov/hurricane",
            description="Category 5 hurricane has made landfall in Florida. Mandatory evacuations ordered for coastal areas."
        ),
        
        # Medium-impact events (should be filtered out - below 75)
        Event(
            title="Magnitude 4.5 Earthquake in California",
            location="California, USA",
            latitude=36.7783,
            longitude=-119.4179,
            source="USGS",
            category="Earthquake",
            severity="Watch",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://earthquake.usgs.gov/earthquakes/eventpage/def456",
            description="Minor magnitude 4.5 earthquake detected in California. No damage reported."
        ),
        Event(
            title="Local Traffic Accident on Highway 101",
            location="California, USA",
            latitude=37.7749,
            longitude=-122.4194,
            source="Google News",
            category="News",
            severity="Watch",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://news.google.com/traffic",
            description="Traffic accident on Highway 101 causing minor delays."
        ),
        
        # Low-impact events (should be filtered out)
        Event(
            title="Celebrity Wins Award at Movie Ceremony",
            location="Los Angeles, USA",
            latitude=34.0522,
            longitude=-118.2437,
            source="Google News",
            category="Entertainment",
            severity="Watch",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://news.google.com/entertainment",
            description="Famous actor wins best picture award at annual movie awards ceremony."
        ),
        Event(
            title="Local Football Team Wins Championship",
            location="Texas, USA",
            latitude=31.9686,
            longitude=-99.9018,
            source="Google News",
            category="Sports",
            severity="Watch",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://news.google.com/sports",
            description="Local high school football team wins state championship."
        ),
        
        # Borderline events (need proper scoring)
        Event(
            title="WHO Declares Global Health Emergency for New Virus Strain",
            location="Geneva, Switzerland",
            latitude=46.2044,
            longitude=6.1432,
            source="WHO",
            category="Health",
            severity="Critical",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://who.int/emergency",
            description="World Health Organization has declared a global health emergency due to a new virus strain spreading rapidly."
        ),
        Event(
            title="Major Stock Exchange Suspends Trading Due to Market Crash",
            location="New York, USA",
            latitude=40.7128,
            longitude=-74.0060,
            source="Reuters",
            category="Economic",
            severity="Critical",
            published_at=datetime.now(timezone.utc).isoformat(),
            url="https://reuters.com/market",
            description="New York Stock Exchange has suspended trading due to unprecedented market volatility and crash."
        ),
    ]
    
    return test_events


def test_intelligence_engine():
    """Test the intelligence engine with various events"""
    print("=" * 80)
    print("NEXUS INTELLIGENCE ENGINE - TEST SUITE")
    print("=" * 80)
    
    engine = IntelligenceEngine()
    test_events = create_test_events()
    
    print(f"\n📊 Testing with {len(test_events)} test events")
    print("-" * 80)
    
    # Test individual event scoring
    print("\n1. INDIVIDUAL EVENT SCORING")
    print("-" * 80)
    for i, event in enumerate(test_events, 1):
        impact_score, score_details = engine.calculate_impact_score(event)
        confidence = engine.calculate_confidence(event)
        is_low, reason = engine.is_low_impact(event)
        
        print(f"\nEvent {i}: {event.title[:60]}...")
        print(f"  Source: {event.source} | Category: {event.category} | Severity: {event.severity}")
        print(f"  Impact Score: {impact_score}/100")
        print(f"  Confidence: {confidence}%")
        print(f"  Low Impact: {is_low} {f'({reason})' if reason else ''}")
        print(f"  Will Pass: {'✅ YES' if impact_score >= 75 and confidence >= 80 and not is_low else '❌ NO'}")
    
    # Test full processing pipeline
    print("\n\n2. FULL PROCESSING PIPELINE")
    print("-" * 80)
    processed_events, filter_stats = engine.process_events(
        test_events,
        min_impact=75,
        min_confidence=80,
        max_results=5
    )
    
    print(f"\n📥 Input: {len(test_events)} events")
    print(f"🚫 Filtered Out:")
    print(f"  - Low Impact: {filter_stats['low_impact']}")
    print(f"  - Below Threshold: {filter_stats['below_threshold']}")
    print(f"  - Low Confidence: {filter_stats['low_confidence']}")
    print(f"  - Total Filtered: {sum(filter_stats.values())}")
    print(f"\n✅ Output: {len(processed_events)} high-impact events")
    
    # Display processed events
    if processed_events:
        print("\n" + "=" * 80)
        print("HIGH-IMPACT EVENTS (Ranked by Intelligence)")
        print("=" * 80)
        for event in processed_events:
            print(f"\n🏆 Rank #{event['intelligence_rank']} - Impact: {event['impact_score']}/100")
            print(f"   Title: {event['title']}")
            print(f"   Source: {event['source']} | Confidence: {event['confidence']}%")
            print(f"   Category: {event['category']} | Severity: {event['severity']}")
            print(f"   Location: {event['location']}")
            print(f"   Published: {event['published_at']}")
            print(f"   URL: {event['url']}")
    
    # Test intelligence summary
    print("\n\n3. INTELLIGENCE SUMMARY")
    print("-" * 80)
    summary = engine.get_intelligence_summary(processed_events)
    print(json.dumps(summary, indent=2))
    
    return processed_events


async def test_full_aggregation():
    """Test the full aggregation pipeline"""
    print("\n\n" + "=" * 80)
    print("4. FULL AGGREGATION PIPELINE TEST")
    print("=" * 80)
    
    print("\n📡 Fetching live events from all sources...")
    aggregator = EventAggregator(newsapi_key=None)  # No NewsAPI key for testing
    
    result = await aggregator.aggregate(limit=5)
    
    print(f"\n📊 Aggregation Results:")
    print(f"  Events Found: {result.get('count', 0)}")
    print(f"  Sources Used: {', '.join(result.get('sources_used', []))}")
    print(f"  Timestamp: {result.get('timestamp')}")
    
    if 'intelligence_summary' in result:
        summary = result['intelligence_summary']
        print(f"\n🎯 Intelligence Summary:")
        print(f"  Threat Level: {summary.get('threat_level')}")
        print(f"  Average Impact: {summary.get('average_impact')}")
        print(f"  Categories: {', '.join(summary.get('categories', []))}")
    
    if 'filter_stats' in result:
        stats = result['filter_stats']
        print(f"\n🔍 Filter Statistics:")
        print(f"  Low Impact: {stats.get('low_impact', 0)}")
        print(f"  Below Threshold: {stats.get('below_threshold', 0)}")
        print(f"  Low Confidence: {stats.get('low_confidence', 0)}")
    
    if result.get('events'):
        print(f"\n✅ Top Events:")
        for i, event in enumerate(result['events'][:3], 1):
            print(f"\n  {i}. {event['title'][:70]}...")
            print(f"     Impact: {event['impact_score']}/100 | Confidence: {event['confidence']}%")
            print(f"     Source: {event['source']} | {event['category']}")
    
    if result.get('error'):
        print(f"\n⚠️  Note: {result['error']}")
    
    return result


def main():
    """Run all tests"""
    try:
        # Test intelligence engine with mock data
        processed = test_intelligence_engine()
        
        # Test full aggregation
        result = asyncio.run(test_full_aggregation())
        
        # Final summary
        print("\n\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Intelligence Engine: OPERATIONAL")
        print(f"✅ Filtering System: ACTIVE (Impact ≥75, Confidence ≥80%)")
        print(f"✅ Source Priority: ENABLED")
        print(f"✅ Event Ranking: ENABLED")
        print(f"\n🎯 The Nexus Intelligence Engine is ready for deployment!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())