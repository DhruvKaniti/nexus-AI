"""Debug script to see what's being filtered"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'backend'))

from app.services.event_aggregator import EventAggregator
from app.services.intelligence_engine import IntelligenceEngine

async def debug_filtering():
    print("=" * 80)
    print("DEBUG: EVENT FILTERING")
    print("=" * 80)
    
    aggregator = EventAggregator()
    
    # Fetch all events
    all_events = []
    for source in aggregator.sources:
        try:
            events = await source.fetch(50)
            print(f"\n{source.get_source_name()}: {len(events)} events")
            for e in events[:3]:  # Show first 3
                print(f"  - {e.title[:60]}... [{e.location}]")
            all_events.extend(events)
        except Exception as ex:
            print(f"\n{source.get_source_name()}: FAILED - {ex}")
    
    print(f"\n\nTotal events collected: {len(all_events)}")
    
    # Remove duplicates
    unique_events = aggregator._remove_duplicates(all_events)
    print(f"After deduplication: {len(unique_events)} events")
    
    # Apply intelligence engine
    engine = IntelligenceEngine()
    high_impact_events, filter_stats = engine.process_events(
        unique_events,
        min_impact=75,
        min_confidence=80,
        max_results=5
    )
    
    print(f"\n\nFiltering Results:")
    print(f"  Low Impact: {filter_stats['low_impact']}")
    print(f"  Below Threshold: {filter_stats['below_threshold']}")
    print(f"  Low Confidence: {filter_stats['low_confidence']}")
    print(f"  Total Filtered: {sum(filter_stats.values())}")
    print(f"  Final Events: {len(high_impact_events)}")
    
    print(f"\n\nFinal Events:")
    for i, e in enumerate(high_impact_events, 1):
        print(f"\n{i}. {e['title'][:70]}...")
        print(f"   Location: {e['location']}")
        print(f"   Category: {e['balanced_category']} | Impact: {e['impact_score']}")
        print(f"   Source: {e['source']}")

if __name__ == "__main__":
    asyncio.run(debug_filtering())