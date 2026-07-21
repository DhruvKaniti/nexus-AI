# Nexus - Live Global Events System

## Overview
Nexus now displays **live global events** happening in the world right now, instead of static/hardcoded events. The system fetches real-time data from multiple sources including:
- **USGS** - Real-time earthquake data
- **NASA EONET** - Natural events (wildfires, storms, etc.)
- **Google News RSS** - Latest global news events

## What Changed

### Before
- Displayed hardcoded "permanent" events:
  - Maritime disruption (Strait of Hormuz)
  - Infrastructure anomaly (North Sea Grid)
  - Civil unrest monitoring (Buenos Aires)

### After
- Fetches **live events** from real-time APIs
- Events update automatically when you click "Refresh Events"
- No more static/placeholder data

## How to Run

### Option 1: Use the startup script (Recommended)
```bash
# Double-click this file:
start-nexus.bat
```

This will:
1. Install backend dependencies
2. Start the backend server (port 8000)
3. Start the frontend dev server (port 5173)

### Option 2: Manual startup

#### Terminal 1 - Backend
```bash
cd apps/backend
python -m app.main
```

#### Terminal 2 - Frontend
```bash
cd apps/frontend
npm run dev
```

## Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Testing the Live Events

1. **On Page Load**: The app automatically fetches 5 live events from the API
2. **Refresh Events**: Click the "Refresh Events" button to fetch new events
3. **View Console Logs**: Open browser DevTools (F12) to see detailed logs:
   - `🌐 Fetching live global events on mount...`
   - `✅ Loaded X live global events`
   - `📰 First event: {title, location, severity, ...}`

## Event Sources

### USGS Earthquakes
- **URL**: https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson
- **Update Frequency**: Real-time
- **Data**: Magnitude, location, depth, time

### NASA EONET
- **URL**: https://eonet.gsfc.nasa.gov/api/v3/events
- **Update Frequency**: Daily
- **Data**: Natural events (wildfires, severe storms, volcanoes, etc.)

### Google News RSS
- **URL**: https://news.google.com/rss
- **Update Frequency**: Real-time
- **Data**: Top global news stories with location extraction

## Event Severity Levels

- **Critical** (rose/red): Major events requiring immediate attention
- **Elevated** (amber/yellow): Significant events to monitor
- **Watch** (blue/cyan): Standard monitoring level

## Troubleshooting

### No events showing?
1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check backend logs for API fetch errors
4. Ensure you have internet connection (APIs are external)

### Backend won't start?
```bash
# Install dependencies
cd apps/backend
pip install -r requirements.txt
```

### Frontend won't start?
```bash
# Install dependencies
cd apps/frontend
npm install
```

## API Response Format

```json
{
  "events": [
    {
      "title": "Earthquake M5.2 - Location",
      "location": "Location name",
      "latitude": 35.123,
      "longitude": -118.456,
      "source": "USGS",
      "category": "Earthquake",
      "severity": "Elevated",
      "published_at": "2026-07-20T15:35:06+00:00",
      "url": "https://...",
      "description": "Magnitude 5.2 earthquake..."
    }
  ],
  "count": 5,
  "sources_used": ["USGS", "NASA EONET", "Google News"],
  "timestamp": "2026-07-20T15:49:04+00:00"
}
```

## Development

### Backend Structure
- `app/main.py` - Flask server entry point
- `app/api/global_scan.py` - API endpoint for fetching events
- `app/services/event_aggregator.py` - Event fetching and aggregation logic

### Frontend Structure
- `src/components/command-center.tsx` - Main command center component
- `src/components/leaflet-map.tsx` - Map visualization
- Event fetching happens in `useEffect` on component mount

## Notes
- Events are deduplicated based on title similarity
- Events are sorted by published date (newest first)
- Geocoding is performed to get coordinates for map display
- If an API source fails, the system continues with available sources