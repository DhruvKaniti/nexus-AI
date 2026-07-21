# Complete End-to-End Debugging Guide

## Objective
Trace exactly where live events are being replaced by default/demo data.

## Debug Logging Added

### 1. Backend (apps/backend/app/api/global_scan.py)
- Logs when global scan is requested
- Logs NewsAPI key configuration
- Logs aggregator initialization
- Logs each source fetch attempt
- Logs complete result with event count and sources

### 2. Frontend - CommandCenter (apps/frontend/src/components/command-center.tsx)
- `🔍 Starting global scan...` - Function entry
- `📡 API Response status` - HTTP status code
- `📦 Raw API response` - Complete JSON from backend
- `📊 Received X events` - Event count and sources
- `📰 First event` - Details of first event
- `🔎 Processing event X/Y` - Each event being processed
- `📍 Geocoded` - Location geocoding results
- `✅ Added crisis` - Crisis object created
- `🔄 Replacing all crises` - Before setCrises()
- `💾 Calling setCrises()` - State update call
- `Before setCrises - current crises count` - Current state
- `✅ setCrises() called` - After state update

### 3. Frontend - LeafletMap (apps/frontend/src/components/leaflet-map.tsx)
- `🗺️ LeafletMap render` - Every render with full crises array
- `Total crises` - Number of crises received
- `Crisis titles` - List of all crisis titles

## How to Debug

### Step 1: Start Backend
```bash
cd apps/backend
python -m app.main
```

### Step 2: Open Frontend in Browser
```bash
cd apps/frontend
npm run dev
# Open http://localhost:5173
```

### Step 3: Open Browser DevTools
1. Press F12
2. Go to Console tab
3. Clear console (Ctrl+L or right-click → Clear)

### Step 4: Click "Start Global Scan"
Watch console logs in order.

## Expected Debug Output

### If Backend Returns Live Events:
```
🔍 Starting global scan...
📡 API Response status: 200 OK
📦 Raw API response: {
  "events": [...],
  "count": 5,
  "sources_used": ["Google News", "USGS", "NASA EONET"],
  ...
}
📊 Received 5 events from sources: ["Google News", "USGS", "NASA EONET"]
📰 First event: {title: "...", source: "...", ...}
🔎 Processing event 1/5: ...
📍 Geocoded "..." to {lat: ..., lng: ...}
✅ Added crisis: ... at ...
...
🔄 Replacing all crises with 5 live events
📋 Final crises array: [...]
💾 Calling setCrises() with: 5 crises
   Before setCrises - current crises count: 3
✅ setCrises() called - React will re-render with new crises

🗺️ LeafletMap render - crises prop: [...]
   Total crises: 5
   Crisis titles: Event 1, Event 2, Event 3, Event 4, Event 5
```

### If Default Crises Persist (BUG):
```
🔍 Starting global scan...
📡 API Response status: 200 OK
📦 Raw API response: {
  "events": [...],  ← LIVE EVENTS HERE
  ...
}
📊 Received 5 events from sources: [...]
...
🔄 Replacing all crises with 5 live events
💾 Calling setCrises() with: 5 crises
   Before setCrises - current crises count: 3
✅ setCrises() called - React will re-render with new crises

🗺️ LeafletMap render - crises prop: [
  {title: "Maritime disruption", ...},  ← DEFAULT CRISES STILL HERE
  {title: "Infrastructure anomaly", ...},
  {title: "Civil unrest monitoring", ...}
]
   Total crises: 3  ← SHOULD BE 5
   Crisis titles: Maritime disruption, Infrastructure anomaly, Civil unrest monitoring
```

## Root Cause Analysis

### Check These in Order:

1. **Backend returning live events?**
   - Look for `📦 Raw API response`
   - Check if `events` array has real data or is empty
   - If empty → Backend issue

2. **Frontend receiving live events?**
   - Look for `📊 Received X events`
   - Check if count > 0
   - If count = 0 → Frontend not getting data

3. **setCrises() being called with live events?**
   - Look for `🔄 Replacing all crises with X live events`
   - Check if X matches events received
   - Look for `💾 Calling setCrises() with: X crises`
   - If X = 0 or X doesn't match → Conversion issue

4. **React state updating?**
   - Look for `Before setCrises - current crises count: X`
   - Then look for next `🗺️ LeafletMap render`
   - Check if `Total crises` matches X
   - If not matching → React state issue

5. **LeafletMap receiving correct crises?**
   - Look for `🗺️ LeafletMap render - crises prop:`
   - Check if array contains live events or defaults
   - If defaults → State not updating or component not re-rendering

6. **Markers rendering correctly?**
   - LeafletMap renders markers from `crises` prop
   - Check `crises.map()` loop in LeafletMap
   - Verify markers match crises array

## Common Issues

### Issue 1: Backend Returns Empty Events
**Symptom:** `📊 Received 0 events`
**Cause:** EventAggregator sources failing
**Check:** Backend logs for source errors

### Issue 2: Frontend Throws Error
**Symptom:** `❌ Global scan failed`
**Cause:** API error or no events
**Check:** Error message in console

### Issue 3: setCrises() Not Updating State
**Symptom:** `Before setCrises - current crises count: 3` then `Total crises: 3`
**Cause:** React state not updating
**Check:** React DevTools → Components → CommandCenter → crises state

### Issue 4: LeafletMap Not Re-rendering
**Symptom:** Console shows new crises but map shows old markers
**Cause:** React memo or shouldComponentUpdate preventing re-render
**Check:** React DevTools → Components → LeafletMap → props

### Issue 5: Browser Cache
**Symptom:** Old code running despite changes
**Cause:** Browser caching old JavaScript
**Fix:** Hard refresh (Ctrl+Shift+R) or disable cache in DevTools

## Verification Checklist

After clicking "Start Global Scan":

- [ ] Backend logs show "Global scan requested"
- [ ] Backend logs show sources being fetched
- [ ] Backend logs show "Global scan complete" with event count
- [ ] Frontend console shows "🔍 Starting global scan..."
- [ ] Frontend console shows "📡 API Response status: 200"
- [ ] Frontend console shows "📦 Raw API response" with events array
- [ ] Frontend console shows "📊 Received X events" (X > 0)
- [ ] Frontend console shows "🔄 Replacing all crises with X live events"
- [ ] Frontend console shows "💾 Calling setCrises() with: X crises"
- [ ] Frontend console shows "🗺️ LeafletMap render" with X crises
- [ ] Crisis titles in LeafletMap match live events (not defaults)
- [ ] Map markers correspond to live event locations
- [ ] CrisisPanel shows live events (not defaults)

## If Default Crises Still Show

### Check 1: Verify Backend Response
```bash
# In browser console, run:
fetch('http://localhost:8000/api/global-scan?limit=5')
  .then(r => r.json())
  .then(d => console.log('Backend response:', d))
```

### Check 2: Verify React State
1. Open React DevTools (F12 → Components tab)
2. Find "CommandCenter" component
3. Check "crises" state
4. Should show live events, not initialCrises

### Check 3: Verify Props
1. In React DevTools, find "LeafletMap" component
2. Check "crises" prop
3. Should show live events array

### Check 4: Check for Multiple Instances
```javascript
// In browser console:
console.log('React roots:', document.querySelector('[data-reactroot]'))
console.log('CommandCenter instances:', document.querySelectorAll('button'))
```

## Reporting Issues

When reporting that default crises still show, provide:

1. **Backend logs** - Complete output from terminal
2. **Frontend console logs** - All logs from F12 console after clicking scan
3. **React DevTools screenshot** - Show crises state in CommandCenter
4. **React DevTools screenshot** - Show crises prop in LeafletMap
5. **Network tab screenshot** - Show /api/global-scan request and response

## Success Criteria

✅ Backend returns live events in JSON
✅ Frontend receives and parses live events
✅ setCrises() called with live events
✅ React state updates to live events
✅ LeafletMap receives live events prop
✅ CrisisPanel displays live events
✅ Map markers correspond to live events
✅ No default crises visible after scan