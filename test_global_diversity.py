"""Quick test to check global event diversity"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'backend'))

from app.services.event_aggregator import EventAggregator

async def test_global_diversity():
    print("=" * 80)
    print("GLOBAL EVENT DIVERSITY TEST")
    print("=" * 80)
    
    aggregator = EventAggregator()
    result = await aggregator.aggregate(limit=5)
    
    print(f"\nTotal Events: {result['count']}")
    print(f"Sources: {', '.join(result['sources_used'])}")
    print(f"\nRegions: {result['intelligence_summary']['regions']}")
    print(f"Region Counts: {result['intelligence_summary']['region_counts']}")
    print(f"\nBalanced Categories: {result['intelligence_summary']['balanced_categories']}")
    
    print(f"\nTop Events:")
    for i, event in enumerate(result['events'], 1):
        print(f"\n{i}. {event['title'][:70]}...")
        print(f"   Location: {event['location']}")
        print(f"   Category: {event['balanced_category']} | Impact: {event['impact_score']}")
        print(f"   Source: {event['source']}")

if __name__ == "__main__":
    asyncio.run(test_global_diversity())