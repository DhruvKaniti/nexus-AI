# Nexus Global Scan - Event Aggregator

## Overview
Nexus Global Scan has been transformed into a multi-source Event Aggregation Engine that fetches real, live events from multiple providers and normalizes them into a unified schema.

## Architecture

### Event Aggregator Service (`apps/backend/app/services/event_aggregator.py`)

**Unified Event Schema:**
```json
{
  "title": "Event title",
  "location": "Location name",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "source": "Source name",
  "category": "Event category",
  "severity": "Critical|Elevated|Watch",
  "published_at": "2026-07-19T15:30:00Z",
  "url": "https://...",
  "description": "Event description"
}
```

### Supported Sources

1. **Google News RSS** (`https://news.google.com/rss`)
   - Status: ✅ Active
   - Type: News headlines
   - Cost: Free
   - No API key required

2. **USGS Earthquake Feed** (`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`)
   - Status: ✅ Active
   - Type: Real-time earthquake data
   - Cost: Free
   - No API key required
   - Includes magnitude, depth, location

3. **NASA EONET** (`https://eonet.gsfc.nasa.gov/api/v3/events`)
   - Status: ✅ Active
   - Type: Natural events (storms, wildfires, floods, etc.)
   - Cost: Free
   - No API key required

4. **NewsAPI** (`https://newsapi.org/v2/top-headlines`)
   - Status: ⚪ Optional
   - Type: News headlines by category
   - Cost: Free tier available
   - Requires: `NEWSAPI_KEY` environment variable

5. **GDELT** (`https://api.gdeltproject.org/api/v2/doc/query`)
   - Status: ❌ Non-functional (returns 404)
   - Type: Global news events
   - Note: API endpoints have changed/deprecated
   - Kept in code for future updates

## Features

### ✅ Implemented
- **Multi-source aggregation**: Fetches from all active sources simultaneously
- **Unified schema**: All sources normalized to common format
- **Deduplication**: Removes duplicate events based on title similarity
- **Sorting**: Events sorted by published_at (newest first)
- **Geocoding**: Automatic lat/lng resolution via Nominatim
- **Error handling**: Each source fails independently without breaking others
- **Logging**: Comprehensive logging of source status and errors
- **No silent fallbacks**: Returns clear error messages when no data available

### Response Format
```json
{
  "events": [...],
  "count": 5,
  "sources_used": ["Google News", "USGS", "NASA EONET"],
  "timestamp": "2026-07-19T15:30:00Z",
  "errors": ["GDELT failed: 404 Not Found"]
}
```

## Installation

```bash
# Install dependencies
cd apps/backend
pip install -r requirements.txt
```

## Configuration

### Optional: NewsAPI Key
```bash
# Set environment variable
export NEWSAPI_KEY=your_api_key_here

# Or create .env file in apps/backend/
NEWSAPI_KEY=your_api_key_here
```

Get a free key at: https://newsapi.org/register

## Usage

### Start Backend Server
```bash
cd apps/backend
python -m app.main
```

### Test the Endpoint
```bash
# Via browser or curl
curl http://localhost:8000/api/global-scan?limit=5

# Or use the test script
python test_aggregator.py
```

### Frontend Integration
The frontend already calls `/api/global-scan?limit=5`. No changes needed.

Click "Start Global Scan" in the Command Center to fetch live events.

## Event Flow

1. **Request** → Frontend calls `/api/global-scan?limit=5`
2. **Aggregation** → EventAggregator fetches from all sources in parallel
3. **Normalization** → Each source converts data to unified Event schema
4. **Deduplication** → Duplicate events removed by title similarity
5. **Sorting** → Events sorted by published_at (newest first)
6. **Response** → Unified event list returned to frontend
7. **Display** → Events shown on map with markers

## Source Details

### Google News RSS
- Fetches top stories from Google News
- Extracts location from titles/descriptions
- Geocodes locations to coordinates
- Category: "News"

### USGS Earthquake Feed
- Real-time earthquake data (past 24 hours)
- Includes magnitude, depth, location
- Automatic severity calculation:
  - M7.0+ = Critical
  - M5.0+ = Elevated
  - <M5.0 = Watch
- Category: "Earthquake"

### NASA EONET
- Natural events from NASA Earth Observatory
- Events: severe storms, wildfires, floods, volcanoes, etc.
- Includes coordinates from satellite data
- Category: Event type (e.g., "Severe Storms")

### NewsAPI (Optional)
- Top headlines by category (general, tech, science, health, business)
- Requires API key
- Source attribution to original news outlet
- Category: Based on query category

## Error Handling

### If a Source Fails
- Error is logged
- Other sources continue
- Failed source listed in `errors` array
- Response still returned if other sources succeed

### If All Sources Fail
```json
{
  "error": "No live events available from any source",
  "events": [],
  "count": 0
}
```

### Common Issues
1. **No events returned**: Check internet connectivity, verify source APIs are accessible
2. **Geocoding failures**: Nominatim rate limiting, locations not found
3. **GDELT 404**: Expected - API endpoints have changed

## Testing

### Test Individual Sources
```python
# Test Google News
from app.services.event_aggregator import GoogleNewsRSSSource
import asyncio

source = GoogleNewsRSSSource()
events = asyncio.run(source.fetch(5))
print(f"Got {len(events)} events from Google News")
```

### Test Full Aggregation
```bash
python test_aggregator.py
```

### Test API Endpoint
```bash
python test_global_scan.py
```

## Performance

- **Parallel fetching**: All sources queried simultaneously
- **Timeout**: 30 seconds per source
- **Geocoding**: 10 second timeout per location
- **Rate limiting**: Respects Nominatim usage policy

## Future Enhancements

1. **Caching**: Cache results for 5-10 minutes to reduce API calls
2. **Fuzzy matching**: Improve duplicate detection with fuzzy string matching
3. **More sources**: Add Twitter/X API, Reddit, etc.
4. **GDELT revival**: Update to working GDELT endpoints when available
5. **Filtering**: Add category/severity filters
6. **Pagination**: Support for browsing more events

## Notes

- **No fake data**: System never returns sample/demo events
- **Transparent errors**: All failures logged and reported
- **Live data only**: Only real, current events from live sources
- **Frontend unchanged**: No modifications needed to frontend code