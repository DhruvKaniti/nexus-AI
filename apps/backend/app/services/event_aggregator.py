"""
Event Aggregator Service
Fetches events from multiple live sources and normalizes them into a unified schema.
"""
import httpx
import feedparser
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Event:
    """Unified event schema"""
    def __init__(
        self,
        title: str,
        location: str,
        latitude: Optional[float],
        longitude: Optional[float],
        source: str,
        category: str,
        severity: str,
        published_at: str,
        url: str,
        description: str = ""
    ):
        self.title = title
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
        self.source = source
        self.category = category
        self.severity = severity
        self.published_at = published_at
        self.url = url
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "source": self.source,
            "category": self.category,
            "severity": self.severity,
            "published_at": self.published_at,
            "url": self.url,
            "description": self.description
        }
    
    def get_dedupe_key(self) -> str:
        """Generate a key for deduplication based on title similarity"""
        if not self.title:
            return "untitled_event"
        return self.title.lower().strip()[:50]


class EventSource(ABC):
    """Base class for event sources"""
    
    @abstractmethod
    async def fetch(self, limit: int) -> List[Event]:
        """Fetch events from this source"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this source"""
        pass


class GoogleNewsRSSSource(EventSource):
    """Fetch events from Google News RSS feed"""
    
    def __init__(self):
        self.base_url = "https://feeds.reuters.com/reuters/worldNews"

    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                # Fetch top stories
                response = client.get(self.base_url, follow_redirects=True)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # Extract location from title/description
                    location = self._extract_location(entry.get("title", "") + " " + entry.get("description", ""))
                    
                    # Geocode location
                    lat, lng = await self._geocode(location)
                    
                    event = Event(
                        title=entry.get("title", "News Event"),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="Google News",
                        category="News",
                        severity="Watch",
                        published_at=self._parse_date(entry.get("published_parsed")),
                        url=entry.get("link", ""),
                        description=entry.get("description", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"Google News RSS fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from ", "off the coast of"]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def _parse_date(self, published_parsed) -> str:
        """Parse published date to ISO format"""
        try:
            if published_parsed:
                dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()
        except Exception:
            pass
        return datetime.now(timezone.utc).isoformat()
    
    def get_source_name(self) -> str:
        return "Google News"


class USGSEarthquakeSource(EventSource):
    """Fetch earthquake data from USGS"""
    
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url)
                response.raise_for_status()
                
                data = response.json()
                features = data.get("features", [])[:limit]
                
                for feature in features:
                    props = feature.get("properties", {})
                    coords = feature.get("geometry", {}).get("coordinates", [])
                    
                    if len(coords) >= 2:
                        magnitude = props.get("mag", 0)
                        severity = self._calculate_severity(magnitude)
                        
                        event = Event(
                            title=f"Earthquake M{magnitude:.1f} - {props.get('place', 'Unknown')}",
                            location=props.get("place", "Unknown"),
                            latitude=coords[1],
                            longitude=coords[0],
                            source="USGS",
                            category="Earthquake",
                            severity=severity,
                            published_at=datetime.fromtimestamp(props.get("time", 0) / 1000, tz=timezone.utc).isoformat(),
                            url=props.get("url", ""),
                            description=f"Magnitude {magnitude:.1f} earthquake detected. Depth: {coords[2]:.1f}km"
                        )
                        events.append(event)
                        
        except Exception as e:
            logger.error(f"USGS Earthquake fetch failed: {e}", exc_info=True)
        
        return events
    
    def _calculate_severity(self, magnitude: float) -> str:
        """Calculate severity based on magnitude"""
        if magnitude >= 7.0:
            return "Critical"
        elif magnitude >= 5.0:
            return "Elevated"
        else:
            return "Watch"
    
    def get_source_name(self) -> str:
        return "USGS"


class NASAEONETSource(EventSource):
    """Fetch natural events from NASA EONET"""
    
    def __init__(self):
        self.base_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params={"limit": limit, "days": 7})
                response.raise_for_status()
                
                data = response.json()
                event_list = data.get("events", [])[:limit]
                
                for eonet_event in event_list:
                    # Get geometry (coordinates)
                    geometry = eonet_event.get("geometry", [])
                    coords = geometry[0].get("coordinates", []) if geometry else []
                    
                    lat, lng = None, None
                    if len(coords) >= 2:
                        lng, lat = coords[0], coords[1]
                    
                    # Get location from first geometry or categories
                    location = eonet_event.get("title", "Unknown")
                    if not lat and geometry:
                        location = geometry[0].get("date", location)
                    
                    # Try to extract actual location from title if it contains coordinates
                    if lat and lng:
                        # Use geocoding to get proper location name from coordinates
                        pass  # Will use coordinates for region detection
                    
                    # Determine category
                    categories = eonet_event.get("categories", [])
                    category = categories[0].get("title", "Natural Event") if categories else "Natural Event"
                    
                    # Clean up location - remove category name if present
                    clean_location = location
                    for cat in ["Wildfire", "Severe Storms", "Flood", "Cyclone", "Volcano", "Earthquake"]:
                        clean_location = clean_location.replace(cat, "").strip()
                        clean_location = clean_location.strip("-").strip()
                        clean_location = clean_location.strip(",").strip()
                    
                    # If location still looks like a title, try to extract just the place names
                    if len(clean_location.split()) > 5:
                        # Take only the last few words which are likely the location
                        words = clean_location.split()
                        clean_location = " ".join(words[-3:])
                    
                    event = Event(
                        title=eonet_event.get("title", "Natural Event"),
                        location=clean_location if clean_location else location,
                        latitude=lat,
                        longitude=lng,
                        source="NASA EONET",
                        category=category,
                        severity="Elevated" if category in ["Severe Storms", "Wildfires"] else "Watch",
                        published_at=eonet_event.get("geometry", [{}])[0].get("date", datetime.now(timezone.utc).isoformat()),
                        url=eonet_event.get("link", ""),
                        description=f"Natural event: {category}"
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"NASA EONET fetch failed: {e}", exc_info=True)
        
        return events
    
    def get_source_name(self) -> str:
        return "NASA EONET"


class NewsAPISource(EventSource):
    """Fetch events from NewsAPI (requires API key)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        
        if not self.api_key:
            logger.warning("NewsAPI key not configured, skipping")
            return events
        
        try:
            with httpx.Client(timeout=30.0) as client:
                # Fetch from multiple categories
                categories = ['general', 'technology', 'science', 'health', 'business']
                
                for category in categories:
                    if len(events) >= limit:
                        break
                    
                    response = client.get(
                        self.base_url,
                        params={
                            "country": "us",
                            "category": category,
                            "pageSize": min(10, limit - len(events)),
                            "apiKey": self.api_key
                        }
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if data.get("status") == "ok" and data.get("articles"):
                        for article in data["articles"]:
                            if len(events) >= limit:
                                break
                            
                            # Skip removed articles
                            if article.get("title") == "[Removed]":
                                continue
                            
                            # Extract location
                            location = self._extract_location(
                                article.get("title", "") + " " + article.get("description", "")
                            )
                            
                            # Geocode
                            lat, lng = await self._geocode(location)
                            
                            event = Event(
                                title=article.get("title", "News Event"),
                                location=location,
                                latitude=lat,
                                longitude=lng,
                                source=article.get("source", {}).get("name", "NewsAPI"),
                                category=category.capitalize(),
                                severity="Watch",
                                published_at=article.get("publishedAt", datetime.now(timezone.utc).isoformat()),
                                url=article.get("url", ""),
                                description=(article.get("description") or article.get("title") or "")[:200]
                            )
                            events.append(event)
                            
        except Exception as e:
            logger.error(f"NewsAPI fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from ", "off the coast of"]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def get_source_name(self) -> str:
        return "NewsAPI"


class GlobalNewsSource(EventSource):
    """Fetch global news from multiple international sources"""
    
    def __init__(self):
        self.base_url = "https://news.google.com/rss"
        self.global_feeds = [
            "https://news.google.com/rss",
            "https://news.google.com/rss/world",
            "https://news.google.com/rss/business",
            "https://news.google.com/rss/science",
            "https://news.google.com/rss/technology",
        ]
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                # Fetch from world news section for more global coverage
                response = client.get("https://news.google.com/rss/world", follow_redirects=True)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # Extract location from title/description
                    location = self._extract_location(entry.get("title", "") + " " + entry.get("description", ""))
                    
                    # Geocode location
                    lat, lng = await self._geocode(location)
                    
                    event = Event(
                        title=entry.get("title", "News Event"),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="Google News World",
                        category="News",
                        severity="Watch",
                        published_at=self._parse_date(entry.get("published_parsed")),
                        url=entry.get("link", ""),
                        description=entry.get("description", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"Global News fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from ", "off the coast of"]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def _parse_date(self, published_parsed) -> str:
        """Parse published date to ISO format"""
        try:
            if published_parsed:
                dt = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()
        except Exception:
            pass
        return datetime.now(timezone.utc).isoformat()
    
    def get_source_name(self) -> str:
        return "Google News World"


class GDELTSource(EventSource):
    """Fetch events from GDELT (currently non-functional)"""
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        
        try:
            with httpx.Client(timeout=30.0) as client:
                # GDELT endpoints returned 404 during testing
                # Kept for reference if endpoints are updated
                gdelt_url = "https://api.gdeltproject.org/api/v2/doc/query"
                
                params = {
                    "query": "sort:Date desc",
                    "mode": "artlist",
                    "maxrecords": str(limit),
                    "format": "json",
                    "trans": "googtrans"
                }
                
                response = client.get(gdelt_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "articles" in data:
                    for article in data["articles"][:limit]:
                        location = self._extract_location(article)
                        lat, lng = await self._geocode(location)
                        
                        event = Event(
                            title=article.get("title", "Global Event"),
                            location=location,
                            latitude=lat,
                            longitude=lng,
                            source="GDELT",
                            category="News",
                            severity="Watch",
                            published_at=datetime.now(timezone.utc).isoformat(),
                            url=article.get("url", ""),
                            description=(article.get("description") or article.get("title") or "")[:200]
                        )
                        events.append(event)
                        
        except Exception as e:
            logger.error(f"GDELT fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, article: dict) -> str:
        """Extract location from article"""
        if "location" in article:
            return article["location"]
        
        text = article.get("title", "") + " " + article.get("description", "")
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from "]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def get_source_name(self) -> str:
        return "GDELT"


class NOAASource(EventSource):
    """Fetch severe weather data from NOAA"""
    
    def __init__(self):
        self.base_url = "https://api.weather.gov/alerts/active"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, headers={"User-Agent": "NexusEventAggregator/1.0"})
                response.raise_for_status()
                
                data = response.json()
                alerts = data.get("features", [])[:limit]
                
                for alert in alerts:
                    props = alert.get("properties", {})
                    
                    # Extract location from geometry or area
                    geometry = alert.get("geometry")
                    coords = []
                    if geometry and geometry.get("coordinates"):
                        coords = geometry.get("coordinates", [[]])[0]
                    lat, lng = None, None
                    if len(coords) >= 2:
                        lng, lat = coords[0], coords[1]
                    
                    # Get area description as location
                    area_desc = props.get("areaDesc", "Unknown")
                    location = area_desc.split(";")[0].strip() if area_desc else "Unknown"
                    
                    # Determine severity
                    severity = props.get("severity", "Watch")
                    if severity in ["Extreme", "Severe"]:
                        severity = "Critical"
                    elif severity in ["Moderate", "Minor"]:
                        severity = "Elevated"
                    
                    event = Event(
                        title=props.get("headline", props.get("event", "Weather Alert")),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="NOAA",
                        category="Severe Weather",
                        severity=severity,
                        published_at=props.get("sent", datetime.now(timezone.utc).isoformat()),
                        url=props.get("@id", ""),
                        description=props.get("description", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"NOAA fetch failed: {e}", exc_info=True)
        
        return events
    
    def get_source_name(self) -> str:
        return "NOAA"


class GDACSSource(EventSource):
    """Fetch disaster data from GDACS"""
    
    def __init__(self):
        self.base_url = "https://www.gdacs.org/xml/rss.xml"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # Extract location
                    location = entry.get("title", "Global")
                    # GDACS titles usually start with event type, extract location
                    if " - " in location:
                        parts = location.split(" - ")
                        if len(parts) > 1:
                            location = parts[-1]
                    
                    # Geocode
                    lat, lng = await self._geocode(location)
                    
                    # Determine category and severity from title
                    title_lower = entry.get("title", "").lower()
                    category = "Natural Disaster"
                    severity = "Elevated"
                    
                    if "earthquake" in title_lower:
                        category = "Earthquake"
                        severity = "Critical" if "magnitude" in title_lower else "Elevated"
                    elif "flood" in title_lower:
                        category = "Flood"
                    elif "cyclone" in title_lower or "typhoon" in title_lower:
                        category = "Cyclone"
                    elif "volcano" in title_lower:
                        category = "Volcano"
                    
                    event = Event(
                        title=entry.get("title", "GDACS Alert"),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="GDACS",
                        category=category,
                        severity=severity,
                        published_at=entry.get("published", datetime.now(timezone.utc).isoformat()),
                        url=entry.get("link", ""),
                        description=entry.get("summary", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"GDACS fetch failed: {e}", exc_info=True)
        
        return events
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global" or not place:
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def get_source_name(self) -> str:
        return "GDACS"


class WHOSource(EventSource):
    """Fetch health emergency data from WHO"""
    
    def __init__(self):
        self.base_url = "https://www.who.int/rss-feeds/news-english.xml"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # Extract location from title/description
                    text = entry.get("title", "") + " " + entry.get("summary", "")
                    location = self._extract_location(text)
                    
                    # Geocode
                    lat, lng = await self._geocode(location)
                    
                    # Check if it's a health emergency
                    title_lower = entry.get("title", "").lower()
                    severity = "Watch"
                    if any(term in title_lower for term in ["emergency", "outbreak", "pandemic", "epidemic"]):
                        severity = "Elevated"
                    
                    event = Event(
                        title=entry.get("title", "WHO Health Alert"),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="WHO",
                        category="Health",
                        severity=severity,
                        published_at=entry.get("published", datetime.now(timezone.utc).isoformat()),
                        url=entry.get("link", ""),
                        description=entry.get("summary", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"WHO fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from ", "off the coast of"]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def get_source_name(self) -> str:
        return "WHO"


class CISASource(EventSource):
    """Fetch cybersecurity alerts from CISA"""
    
    def __init__(self):
        self.base_url = "https://www.cisa.gov/cybersecurity-advisories/cybersecurity-advisories.xml"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # CISA alerts are typically US-focused but global impact
                    location = "United States"
                    
                    event = Event(
                        title=entry.get("title", "CISA Alert"),
                        location=location,
                        latitude=38.9072,  # Washington DC
                        longitude=-77.0369,
                        source="CISA",
                        category="Cyberattack",
                        severity="Elevated",
                        published_at=entry.get("published", datetime.now(timezone.utc).isoformat()),
                        url=entry.get("link", ""),
                        description=entry.get("summary", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"CISA fetch failed: {e}", exc_info=True)
        
        return events
    
    def get_source_name(self) -> str:
        return "CISA"


class BBCSource(EventSource):
    """Fetch top news from BBC"""
    
    def __init__(self):
        self.base_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, follow_redirects=True)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # Extract location from title/description
                    text = entry.get("title", "") + " " + entry.get("summary", "")
                    location = self._extract_location(text)
                    
                    # Geocode
                    lat, lng = await self._geocode(location)
                    
                    event = Event(
                        title=entry.get("title", "BBC News"),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="BBC",
                        category="News",
                        severity="Watch",
                        published_at=entry.get("published", datetime.now(timezone.utc).isoformat()),
                        url=entry.get("link", ""),
                        description=entry.get("summary", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"BBC fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from ", "off the coast of"]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def get_source_name(self) -> str:
        return "BBC"


class ReutersSource(EventSource):
    """Fetch top news from Reuters (backup)"""
    
    def __init__(self):
        self.base_url = "https://www.reuters.com/arc/outboundfeeds/rss/category/world/"
    
    async def fetch(self, limit: int) -> List[Event]:
        events = []
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, follow_redirects=True)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:limit]:
                    # Extract location from title/description
                    text = entry.get("title", "") + " " + entry.get("summary", "")
                    location = self._extract_location(text)
                    
                    # Geocode
                    lat, lng = await self._geocode(location)
                    
                    event = Event(
                        title=entry.get("title", "Reuters News"),
                        location=location,
                        latitude=lat,
                        longitude=lng,
                        source="Reuters",
                        category="News",
                        severity="Watch",
                        published_at=entry.get("published", datetime.now(timezone.utc).isoformat()),
                        url=entry.get("link", ""),
                        description=entry.get("summary", "")[:200]
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"Reuters fetch failed: {e}", exc_info=True)
        
        return events
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        text = text.lower()
        location_keywords = ["in ", "at ", "near ", "from ", "off the coast of"]
        
        for keyword in location_keywords:
            if keyword in text:
                idx = text.index(keyword) + len(keyword)
                words = text[idx:idx+50].split()
                if words:
                    return " ".join(words[:3]).strip(",.")
        
        return "Global"
    
    async def _geocode(self, place: str) -> tuple[Optional[float], Optional[float]]:
        """Geocode location"""
        if place == "Global":
            return None, None
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": place, "limit": 1},
                    headers={"User-Agent": "NexusEventAggregator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding failed for '{place}': {e}")
        
        return None, None
    
    def get_source_name(self) -> str:
        return "Reuters"


class EventAggregator:
    """Aggregates events from multiple specialized sources"""
    
    def __init__(self, newsapi_key: Optional[str] = None):
        self.sources: List[EventSource] = [
            # Specialized feeds
            USGSEarthquakeSource(),      # USGS (earthquakes)
            NASAEONETSource(),            # NASA EONET (fires, volcanoes)
            NOAASource(),                 # NOAA (storms)
            GDACSSource(),                # GDACS (major disasters)
            CISASource(),                 # CISA (cybersecurity)
                                  
            # General news
           GlobalNewsSource()
        ]
        
        # Add NewsAPI if key is provided
        if newsapi_key:
            self.sources.append(NewsAPISource(newsapi_key))
        
        # Add GDELT (currently non-functional)
        # self.sources.append(GDELTSource())
    
    async def aggregate(self, limit: int = 10) -> Dict[str, Any]:
        """
        Aggregate events from multiple sources with timeout protection
        and parallel fetching.
        """

        import asyncio
        from app.services.intelligence_engine import IntelligenceEngine

        all_events: List[Event] = []
        sources_used = []
        errors = []

        # Reduced workload for faster live scanning
        raw_fetch_limit = max(20, limit * 3)

        logger.info(
            f"🎯 Fetching {raw_fetch_limit} raw events from {len(self.sources)} sources"
        )

        async def fetch_source(source):
            """
            Fetch one source safely with timeout protection.
            """

            try:
                logger.info(
                    f"Fetching from {source.get_source_name()}"
                )

                events = await asyncio.wait_for(
                    source.fetch(raw_fetch_limit),
                    timeout=5
                )

                return (
                    source.get_source_name(),
                    events,
                    None
                )

            except asyncio.TimeoutError:
                return (
                    source.get_source_name(),
                    [],
                    "Timed out after 20 seconds"
                )

            except Exception as e:
                return (
                    source.get_source_name(),
                    [],
                    str(e)
                )


        # Run all sources simultaneously
        results = await asyncio.gather(
            *(fetch_source(source) for source in self.sources)
        )


        # Process results
        for source_name, events, error in results:

            if events:
                all_events.extend(events)
                sources_used.append(source_name)

                logger.info(
                    f"✅ {source_name}: {len(events)} events"
                )

            else:
                logger.warning(
                    f"⚠️ {source_name}: no events"
                )

            if error:
                errors.append(
                    f"{source_name}: {error}"
                )


        logger.info(
            f"Total raw events collected: {len(all_events)}"
        )


        # Remove duplicates
        unique_events = self._remove_duplicates(all_events)

        logger.info(
            f"After deduplication: {len(unique_events)} events"
        )


        # AI filtering
        intelligence_engine = IntelligenceEngine()

        high_impact_events, filter_stats = intelligence_engine.process_events(
            unique_events,
            target_count=limit
        )


        summary = intelligence_engine.get_intelligence_summary(
            high_impact_events
        )


        result = {
            "events": high_impact_events,
            "count": len(high_impact_events),
            "sources_used": sources_used,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intelligence_summary": summary,
            "filter_stats": filter_stats,
            "raw_events_collected": len(all_events),
            "unique_events_after_dedup": len(unique_events)
        }


        if errors:
            result["errors"] = errors


        if not high_impact_events:
            result["error"] = "No events meet the criteria"


        return result        

    def _remove_duplicates(self, events: List[Event]) -> List[Event]:
        """Remove duplicate events based on title similarity"""
        seen_keys = set()
        unique_events = []

        for event in events:
            dedupe_key = event.get_dedupe_key()

            if dedupe_key not in seen_keys:
                seen_keys.add(dedupe_key)
                unique_events.append(event)

        logger.info(
            f"Removed {len(events) - len(unique_events)} duplicate events"
        )

        return unique_events


    def _sort_by_date(self, events: List[Event]) -> List[Event]:
        """Sort events by published_at (newest first)"""
        try:
            return sorted(
                events,
                key=lambda x: x.published_at,
                reverse=True
            )

        except Exception as e:
            logger.error(
                f"Sorting failed: {e}"
            )
            return events