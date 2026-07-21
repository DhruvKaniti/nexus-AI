# Nexus Global High-Impact Intelligence Engine

## Overview

The Nexus Intelligence Engine transforms the Event Aggregator from a generic news collector into a **Global High-Impact Intelligence Platform** similar to Palantir, Dataminr, or Microsoft's crisis monitoring systems.

## Core Features

### 1. **Intelligent Filtering**
- Automatically removes low-impact events
- Filters out: sports, entertainment, local crimes, traffic accidents, minor political stories, etc.
- Only returns events with **Impact Score ≥ 75** and **Confidence ≥ 80%**

### 2. **Impact Scoring (0-100)**
Events are scored based on:
- **Source Authority** (0-30 points): USGS, NASA, NOAA, WHO, Reuters, AP, BBC weighted higher
- **Keyword Matching** (0-30 points): High-impact keywords in natural disasters, geopolitics, infrastructure, economy, cyber, health
- **Category Bonus** (0-20 points): Earthquakes, severe storms, cyberattacks, pandemics score higher
- **Severity Bonus** (0-20 points): Critical, Elevated, Watch levels
- **Geographic Precision** (0-10 points): Events with exact coordinates and specific locations

### 3. **Confidence Scoring (0-100)**
Based on:
- Source reliability and authority
- Data completeness (coordinates, location, description)
- Information quality

### 4. **Event Ranking**
Events sorted by:
1. Impact Score (descending)
2. Severity (Critical > Elevated > Watch)
3. Publication Time (newest first)

### 5. **Source Priority**
Authoritative sources preferred:
- **Tier 1 (95-100)**: USGS, NASA EONET, NASA FIRMS, NOAA, GDACS
- **Tier 2 (85-90)**: WHO, ReliefWeb, Reuters, AP, BBC
- **Tier 3 (50-60)**: Google News, NewsAPI
- **Tier 4 (40)**: GDELT

## API Endpoints

### `/api/global-scan`
**Global High-Impact Intelligence Scan**

Returns only events meeting strict criteria:
- Impact Score ≥ 75
- Confidence ≥ 80%
- Maximum 5 events by default

**Query Parameters:**
- `limit` (optional): Number of events to return (default: 5, max: 10)

**Response Format:**
```json
{
  "events": [
    {
      "title": "Event title",
      "location": "Location",
      "latitude": 35.6762,
      "longitude": 139.6503,
      "source": "USGS",
      "category": "Earthquake",
      "severity": "Critical",
      "published_at": "2026-07-20T16:51:28+00:00",
      "url": "https://...",
      "description": "Event description",
      "impact_score": 95,
      "confidence": 100,
      "intelligence_rank": 1,
      "score_details": {
        "source_bonus": 30.0,
        "keyword_matches": ["earthquake", "magnitude", "tsunami"],
        "category_bonus": 20,
        "severity_bonus": 20,
        "geographic_bonus": 10,
        "final_score": 95
      }
    }
  ],
  "count": 5,
  "sources_used": ["USGS", "NASA EONET", "Reuters"],
  "timestamp": "2026-07-20T16:51:28+00:00",
  "intelligence_summary": {
    "threat_level": "High",
    "total_events": 5,
    "categories": ["Earthquake", "Cyberattack", "Economic"],
    "average_impact": 85.25,
    "max_impact": 95,
    "min_impact": 81
  },
  "filter_stats": {
    "low_impact": 16,
    "below_threshold": 14,
    "low_confidence": 0
  },
  "api_version": "2.0",
  "filter_criteria": {
    "min_impact_score": 75,
    "min_confidence": 80,
    "max_results": 5
  }
}
```

### `/api/intelligence-summary`
**Intelligence Summary Only**

Returns summary statistics without full event details.

### `/api/health`
**Health Check**

Returns service status and version.

## Event Categories Prioritized

### Natural Disasters
- Earthquakes ≥ 5.0 magnitude
- Tsunami warnings
- Major hurricanes/cyclones (Category 3+)
- Floods affecting cities/regions
- Large wildfires
- Volcanic eruptions
- Tornado outbreaks

### Geopolitics
- Military strikes and missile launches
- Armed conflicts and invasions
- Border escalations
- Terror attacks
- Government emergencies
- Major protests affecting cities

### Infrastructure
- Airport shutdowns
- Port closures
- Shipping disruptions
- Power grid failures
- Internet/telecommunications outages
- Pipeline incidents
- Major transportation disruptions

### Economy
- Supply chain disruptions
- Factory shutdowns
- Commodity shocks
- Banking emergencies
- Stock exchange suspensions
- Market crashes

### Cybersecurity
- Nation-state cyberattacks
- Critical infrastructure attacks
- Major ransomware incidents
- Cloud provider outages

### Health
- Disease outbreaks
- WHO emergency declarations
- Pandemic-related developments

## Filtered Events

The engine **automatically excludes**:
- ❌ Earthquakes below magnitude 5.0
- ❌ Small local crimes
- ❌ Local traffic accidents
- ❌ Small fires
- ❌ Minor political stories
- ❌ Celebrity news
- ❌ Opinion articles
- ❌ Sports
- ❌ Entertainment
- ❌ Small protests
- ❌ Routine weather
- ❌ Duplicate news

## Testing

Run the test suite:
```bash
python test_intelligence_engine.py
```

The test suite includes:
1. **Individual Event Scoring**: Tests 9 different event types
2. **Full Processing Pipeline**: Validates filtering and ranking
3. **Live Aggregation**: Tests real-time data from all sources
4. **Intelligence Summary**: Validates summary generation

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Intelligence Engine                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌──────────────────┐            │
│  │ Event Sources│─────▶│  Event Filter    │            │
│  │ - USGS       │      │  - Low impact    │            │
│  │ - NASA EONET │      │  - Magnitude     │            │
│  │ - Reuters    │      │  - Categories    │            │
│  │ - WHO        │      │  - Keywords      │            │
│  │ - Google News│      └──────────────────┘            │
│  └──────────────┘               │                       │
│                                 ▼                       │
│                        ┌──────────────────┐             │
│                        │ Impact Scoring   │             │
│                        │ - Source (0-30)  │             │
│                        │ - Keywords (0-30)│             │
│                        │ - Category (0-20)│             │
│                        │ - Severity (0-20)│             │
│                        │ - Geo (0-10)     │             │
│                        └──────────────────┘             │
│                                 │                       │
│                                 ▼                       │
│                        ┌──────────────────┐             │
│                        │ Confidence Score │             │
│                        │ - Source (0-30)  │             │
│                        │ - Data (0-20)    │             │
│                        └──────────────────┘             │
│                                 │                       │
│                                 ▼                       │
│                        ┌──────────────────┐             │
│                        │ Ranking & Filter │             │
│                        │ - Impact ≥ 75    │             │
│                        │ - Confidence ≥80 │             │
│                        │ - Sort by score  │             │
│                        └──────────────────┘             │
│                                 │                       │
│                                 ▼                       │
│                        ┌──────────────────┐             │
│                        │ Top 5 Events     │             │
│                        │ + Intelligence   │             │
│                        │   Summary        │             │
│                        └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables
- `NEWSAPI_KEY`: Optional API key for NewsAPI (provides additional news sources)

### Thresholds
Adjust in `intelligence_engine.py`:
- `min_impact`: Minimum impact score (default: 75)
- `min_confidence`: Minimum confidence score (default: 80)
- `max_results`: Maximum events to return (default: 5)

## Performance

- **Latency**: Typically 2-5 seconds for full aggregation
- **Sources**: 3-4 active sources (USGS, NASA EONET, Google News, optionally NewsAPI)
- **Filtering**: Removes ~80-90% of raw events as low-impact
- **Throughput**: Handles 15-20 input events, returns top 5 high-impact events

## Future Enhancements

1. **Multi-source Deduplication**: Detect same event from multiple sources to boost confidence
2. **Machine Learning**: Train model on historical high-impact events
3. **Real-time Streaming**: WebSocket updates for live crisis monitoring
4. **Geographic Clustering**: Group related events by region
5. **Trend Analysis**: Track event patterns over time
6. **Alert System**: Automated alerts for critical events
7. **Historical Data**: Archive and analyze past events
8. **Custom Feeds**: User-defined event categories and regions

## Version History

- **v2.0** (2026-07-20): Global High-Impact Intelligence Engine
  - Impact scoring system
  - Confidence scoring
  - Intelligent filtering
  - Source priority weighting
  - Event ranking
  - Intelligence summaries

- **v1.0**: Basic event aggregator
  - Multiple source aggregation
  - Simple deduplication
  - Date-based sorting

## License

Part of the Nexus platform.