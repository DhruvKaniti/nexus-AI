"""Quick test of event aggregator"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.event_aggregator import EventAggregator

async def test_aggregator():
    print("🧪 Testing EventAggregator...")
    print("=" * 60)
    
    aggregator = EventAggregator(newsapi_key=None)
    print(f"📊 Initialized with {len(aggregator.sources)} sources:")
    for source in aggregator.sources:
        print(f"   - {source.get_source_name()}")
    
    print("\n🚀 Fetching events (limit=5)...")
    result = await aggregator.aggregate(limit=5)
    
    print("\n📦 Results:")
    print(f"   Count: {result.get('count', 0)}")
    print(f"   Sources used: {result.get('sources_used', [])}")
    print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
    
    if result.get('errors'):
        print(f"\n❌ Errors:")
        for error in result['errors']:
            print(f"   - {error}")
    
    if result.get('events'):
        print(f"\n✅ Events fetched:")
        for i, event in enumerate(result['events'], 1):
            print(f"\n   {i}. {event['title']}")
            print(f"      Location: {event['location']}")
            print(f"      Category: {event['category']}")
            print(f"      Severity: {event['severity']}")
            print(f"      Source: {event['source']}")
            print(f"      Published: {event['published_at']}")
            print(f"      Coordinates: ({event['latitude']}, {event['longitude']})")
    else:
        print("\n⚠️  No events fetched!")
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_aggregator())