"""Test script for Event Aggregator"""
import asyncio
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.event_aggregator import EventAggregator

async def test_aggregator():
    print("Testing Event Aggregator")
    print("=" * 60)
    
    # Create aggregator without NewsAPI key
    print("\n1. Testing with free sources only (Google News, USGS, NASA EONET):")
    print("-" * 60)
    aggregator = EventAggregator(newsapi_key=None)
    
    result = await aggregator.aggregate(limit=5)
    
    print(f"\nResult:")
    print(f"  Count: {result.get('count')}")
    print(f"  Sources Used: {result.get('sources_used')}")
    print(f"  Timestamp: {result.get('timestamp')}")
    
    if result.get('errors'):
        print(f"\n  Errors:")
        for error in result['errors']:
            print(f"    - {error}")
    
    if result.get('events'):
        print(f"\n  Events:")
        for i, event in enumerate(result['events'], 1):
            print(f"\n  {i}. {event.get('title')}")
            print(f"     Source: {event.get('source')}")
            print(f"     Category: {event.get('category')}")
            print(f"     Location: {event.get('location')}")
            print(f"     Coordinates: ({event.get('latitude')}, {event.get('longitude')})")
            print(f"     Published: {event.get('published_at')}")
            print(f"     Severity: {event.get('severity')}")
            print(f"     URL: {event.get('url')}")
    else:
        print("\n  No events returned")
    
    if result.get('error'):
        print(f"\n  Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_aggregator())