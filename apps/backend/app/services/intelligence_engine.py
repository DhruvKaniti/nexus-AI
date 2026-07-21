"""
Global High-Impact Intelligence Engine
Priority-based intelligence pipeline that ensures diverse, global event coverage.
"""
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timezone
from app.services.event_aggregator import Event
from math import radians, cos, sin, asin, sqrt
from enum import Enum

logger = logging.getLogger(__name__)


class PriorityTier(Enum):
    """Event priority tiers for intelligence pipeline"""
    TIER_1_CRITICAL = 1  # Wars, military conflicts, terrorism, major cyber attacks, M5.5+ earthquakes, hurricanes, floods, wildfires, major infrastructure failures, health emergencies, large protests, economic shocks
    TIER_2_IMPORTANT = 2  # M4+ earthquakes, large fires, volcanoes, power outages, airport disruptions, shipping disruptions, severe weather, transportation accidents, government alerts, border incidents, large evacuations, significant crime affecting infrastructure
    TIER_3_GENERAL = 3  # Localized flooding, industrial accidents, smaller earthquakes, regional outages, infrastructure maintenance alerts, environmental hazards


class IntelligenceEngine:
    """
    Priority-based Intelligence Engine that ensures diverse global coverage.
    Always returns ~10 events using a tiered selection system.
    """
    
    # Source priority weights (higher = more authoritative)
    SOURCE_PRIORITY = {
        "USGS": 100,
        "NASA EONET": 95,
        "NASA FIRMS": 95,
        "NOAA": 95,
        "GDACS": 95,
        "ReliefWeb": 90,
        "WHO": 90,
        "Reuters": 85,
        "AP": 85,
        "BBC": 85,
        "Associated Press": 85,
        "CISA": 90,
        "MarineTraffic": 85,
        "Aviation": 85,
        "Google News": 60,
        "NewsAPI": 50,
        "GDELT": 40,
    }
    
    # Tier 1 - Critical Global Events (Highest Priority)
    TIER_1_KEYWORDS = {
        "geopolitical": [
            "war", "military conflict", "invasion", "missile strike", "airstrike",
            "terrorism", "terrorist attack", "bombing", "explosion", "nuclear",
            "weapons", "sanctions", "embargo", "coup", "revolution", "martial law",
            "state of emergency", "government emergency", "escalation", "border conflict"
        ],
        "cyber": [
            "major cyber attack", "cyber warfare", "ransomware attack", "data breach",
            "critical infrastructure attack", "massive data leak", "ddos attack",
            "cyberattack", "hacking", "security breach"
        ],
        "natural_disaster": [
            "tsunami", "hurricane", "cyclone", "typhoon",
            "major flood", "flash flood", "wildfire", "volcano", "eruption", "tornado",
            "storm surge", "landslide", "avalanche"
        ],
        "infrastructure": [
            "major infrastructure failure", "bridge collapse", "dam failure", 
            "hospital shutdown", "power grid failure", "major blackout",
            "airport shutdown", "port closure", "pipeline explosion"
        ],
        "health": [
            "pandemic", "epidemic", "disease outbreak", "who emergency", "virus outbreak",
            "public health emergency", "contamination", "quarantine", "lockdown"
        ],
        "protest": [
            "large protest", "mass demonstration", "riot", "civil unrest"
        ],
        "economic": [
            "stock market crash", "banking crisis", "financial crisis", "recession",
            "currency collapse", "major economic shock", "commodity crisis"
        ]
    }
    
    # Tier 2 - Important Regional Events
    TIER_2_KEYWORDS = {
        "earthquake": ["earthquake", "magnitude"],
        "fire": ["large fire", "wildfire", "forest fire", "industrial fire"],
        "volcano": ["volcano", "eruption", "volcanic"],
        "infrastructure": [
            "power outage", "blackout", "internet outage", "telecommunications outage",
            "airport disruption", "flight cancellation", "port disruption",
            "shipping disruption", "supply chain disruption"
        ],
        "weather": [
            "hurricane",
            "major hurricane",
            "typhoon",
            "cyclone",
            "storm surge",
            "catastrophic flooding",
            "extreme flooding",
        ],
        "transportation": [
            "transportation accident", "train derailment", "plane crash", 
            "shipwreck", "major accident", "collision"
        ],
        "government": [
            "government alert", "emergency alert", "evacuation order", 
            "border incident", "border closure"
        ],
        "crime": [
            "major crime", "terror plot", "significant crime", "infrastructure attack"
        ]
    }
    
    # Tier 3 - General Intelligence
    TIER_3_KEYWORDS = {
        "flooding": ["localized flooding", "flood", "overflow"],
        "industrial": ["industrial accident", "chemical spill", "hazardous material"],
        "earthquake": ["earthquake", "tremor"],
        "infrastructure": [
            "regional outage", "power outage", "outage", "maintenance alert",
            "infrastructure maintenance", "service disruption"
        ],
        "environmental": [
            "environmental hazard", "pollution", "air quality alert", 
            "water contamination", "chemical leak"
        ]
    }
    
    # Geographic regions for diversity
    GEOGRAPHIC_REGIONS = {
        "north_america": [
            "usa", "united states", "canada", "mexico", "america",
            "california", "texas", "florida", "new york", "colorado", "idaho", "oregon",
            "washington", "arizona", "nevada", "utah", "montana", "wyoming", "new mexico",
            "alaska", "hawaii", "kansas", "oklahoma", "missouri", "arkansas",
            "louisiana", "mississippi", "alabama", "georgia", "south carolina", "north carolina",
            "virginia", "west virginia", "maryland", "delaware", "new jersey", "pennsylvania",
            "connecticut", "rhode island", "massachusetts", "new hampshire", "vermont", "maine",
            "minnesota", "iowa", "nebraska", "south dakota", "north dakota",
            "ontario", "quebec", "british columbia", "alberta", "manitoba", "saskatchewan"
        ],
        "south_america": ["brazil", "argentina", "colombia", "chile", "peru", "venezuela", "ecuador", "bolivia"],
        "europe": ["uk", "united kingdom", "france", "germany", "italy", "spain", "ukraine", "russia", "poland", "netherlands", "belgium", "sweden", "norway", "finland", "denmark", "greece", "portugal", "austria", "switzerland", "czech republic", "romania", "hungary"],
        "middle_east": ["iran", "iraq", "saudi arabia", "israel", "syria", "yemen", "lebanon", "jordan", "uae", "qatar", "kuwait", "turkey", "egypt"],
        "asia": ["china", "japan", "india", "korea", "taiwan", "vietnam", "thailand", "indonesia", "philippines", "pakistan", "bangladesh", "myanmar", "malaysia", "singapore", "hong kong"],
        "africa": ["egypt", "nigeria", "south africa", "ethiopia", "kenya", "drc", "sudan", "somalia", "libya", "algeria", "morocco", "tanzania", "ghana", "ivory coast"],
        "oceania": ["australia", "new zealand", "papua new guinea", "fiji"]
    }
    
    # Category mapping for balancing
    CATEGORY_MAPPING = {
        "Earthquake": "natural_disaster",
        "Severe Storms": "natural_disaster",
        "Wildfires": "natural_disaster",
        "Flood": "natural_disaster",
        "Cyclone": "natural_disaster",
        "Volcano": "natural_disaster",
        "Natural Event": "natural_disaster",
        "Military": "geopolitical",
        "Conflict": "geopolitical",
        "Terror": "geopolitical",
        "News": "geopolitical",
        "airport shutdown": "infrastructure",
        "port closure": "infrastructure",
        "power grid": "infrastructure",
        "blackout": "infrastructure",
        "internet outage": "infrastructure",
        "bridge collapse": "infrastructure",
        "dam failure": "infrastructure",
        "supply chain": "infrastructure",
        "logistics": "infrastructure",
        "banking emergency": "economic",
        "stock exchange": "economic",
        "market crash": "economic",
        "recession": "economic",
        "financial": "economic",
        "cyberattack": "cyber",
        "ransomware": "cyber",
        "data breach": "cyber",
        "hacking": "cyber",
        "ddos": "cyber",
        "cloud outage": "cyber",
        "pandemic": "health",
        "epidemic": "health",
        "disease outbreak": "health",
        "virus": "health",
        "contamination": "health",
        "public health": "health",
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Demo mode for mission-control visualization
        self.demo_mode = True
    
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance in kilometers between two points"""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    def _get_geographic_region(self, location: str) -> Optional[str]:
        """Determine geographic region from location string"""
        location_lower = location.lower()
        for region, keywords in self.GEOGRAPHIC_REGIONS.items():
            if any(keyword in location_lower for keyword in keywords):
                return region
        return None
    
    def _get_balanced_category(self, event: Dict[str, Any]) -> str:
        """Map event to balanced category"""
        category = event.get("category", "")
        if category in self.CATEGORY_MAPPING:
            return self.CATEGORY_MAPPING[category]
        
        title_lower = event.get("title", "").lower()
        desc_lower = event.get("description", "").lower()
        combined = title_lower + " " + desc_lower
        
        for keyword, category in {
            "wildfire": "natural_disaster", "earthquake": "natural_disaster",
            "flood": "natural_disaster", "hurricane": "natural_disaster",
            "cyclone": "natural_disaster", "volcano": "natural_disaster",
            "tsunami": "natural_disaster", 
            "cyberattack": "cyber", "ransomware": "cyber", "data breach": "cyber",
            "hacking": "cyber", "pandemic": "health", "outbreak": "health",
            "military": "geopolitical",
            "conflict": "geopolitical", "attack": "geopolitical", "war": "geopolitical",
            "virus": "health", "supply chain": "infrastructure", "blackout": "infrastructure",
            "airport": "infrastructure", "port": "infrastructure",
            "banking": "economic", "stock exchange": "economic", "market": "economic",
            "ransomware": "cyber",
            "cyber actors": "cyber",
            "cyber actor": "cyber",
            "cyberattack": "cyber",
            "cyber attack": "cyber",
            "programmable logic controllers": "cyber",
            "industrial control systems": "cyber",
            "critical infrastructure attack": "cyber",
            "state-sponsored": "cyber",
            "malware": "cyber",
            "exploit": "cyber",
        
        }.items():
            if keyword in combined:
                return category
        
        return "other"
    
    def _determine_priority_tier(self, event: Event) -> Optional[PriorityTier]:
        """
        Determine the priority tier of an event.

        Priority order:
        1. Earthquakes (magnitude based)
        2. Category-specific rules
        3. Tier 1 keywords
        4. Tier 2 keywords
        5. Tier 3 keywords
        6. Geolocated fallback
        """

        title = (event.title or "").lower()
        description = (event.description or "").lower()
        combined = f"{title} {description}"

        category = (event.category or "").lower()

        # =====================================================
        # EARTHQUAKES (Magnitude Driven)
        # =====================================================
        if category == "earthquake":

            mag_match = (
                            re.search(r"\bm\s*(\d+(?:\.\d+)?)", combined, re.IGNORECASE)
                            or re.search(r"magnitude\s*(\d+(?:\.\d+)?)", combined, re.IGNORECASE)
                            or re.search(r"(\d+(?:\.\d+)?)\s*(?:magnitude|mag)", combined, re.IGNORECASE)
                        )

            if mag_match:
                magnitude = float(mag_match.group(1))

                if magnitude >= 6.5:
                    return PriorityTier.TIER_1_CRITICAL

                elif magnitude >= 5.0:
                    return PriorityTier.TIER_2_IMPORTANT

                elif magnitude >= 4.0:
                    return PriorityTier.TIER_3_GENERAL

                return None

            # Unknown magnitude
            return PriorityTier.TIER_3_GENERAL

        # =====================================================
        # CATEGORY RULES
        # =====================================================

        if category in [
            "military",
            "conflict",
            "terror",
        ]:
            return PriorityTier.TIER_1_CRITICAL

        if category in [
            "cyberattack",
            "cyber",
        ]:
            return PriorityTier.TIER_1_CRITICAL

        if category in [
            "pandemic",
            "health",
        ] and any(
            x in combined
            for x in [
                "outbreak",
                "epidemic",
                "who emergency",
                "pandemic",
            ]
        ):
            return PriorityTier.TIER_1_CRITICAL

        if category in [
            "wildfires",
            "wildfire",
        ]:
            if "major" in combined or "extreme" in combined:
                return PriorityTier.TIER_1_CRITICAL
            return PriorityTier.TIER_2_IMPORTANT

        if category in [
            "severe storms",
            "cyclone",
            "flood",
            "volcano",
        ]:
            return PriorityTier.TIER_2_IMPORTANT

        # =====================================================
        # TIER 1 KEYWORDS
        # =====================================================

        for keywords in self.TIER_1_KEYWORDS.values():
            if any(keyword in combined for keyword in keywords):
                return PriorityTier.TIER_1_CRITICAL

        # =====================================================
        # TIER 2 KEYWORDS
        # =====================================================

        for keywords in self.TIER_2_KEYWORDS.values():
            if any(keyword in combined for keyword in keywords):
                return PriorityTier.TIER_2_IMPORTANT

        # =====================================================
        # TIER 3 KEYWORDS
        # =====================================================

        for keywords in self.TIER_3_KEYWORDS.values():
            if any(keyword in combined for keyword in keywords):
                return PriorityTier.TIER_3_GENERAL

        # =====================================================
        # FALLBACK
        # =====================================================

        if (
            event.latitude is not None
            and event.longitude is not None
            and event.location
            and event.location != "Global"
        ):
            return PriorityTier.TIER_3_GENERAL

        return None
    
    def _is_wildfire(self, event: Dict[str, Any]) -> bool:
        """Return True if the event is a wildfire."""

        category = (event.get("category") or "").lower()
        title = (event.get("title") or "").lower()
        description = (event.get("description") or "").lower()

        combined = f"{category} {title} {description}"

        return any(
            keyword in combined
            for keyword in [
                "wildfire",
                "forest fire",
                "brush fire",
                "vegetation fire",
            ]
        )

    def _extract_state_province(self, location: str) -> Optional[str]:
        """Extract state/province from location string"""
        patterns = [
            r',\s*([A-Z]{2})\s*,',  # US state: ", CA,"
            r',\s*([A-Z][a-z]+)\s+',  # Province: ", Ontario "
            r'-\s*([A-Z]{2})\s',  # State after dash: "- CA "
        ]
        
        for pattern in patterns:
            match = re.search(pattern, location)
            if match:
                return match.group(1)
        
        return None
    
    def calculate_impact_score(self, event: Event, tier: PriorityTier) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate impact score (0-100) based on tier and multiple factors.
        """
        score = 0
        details = {
            "tier": tier.name if tier else "UNKNOWN",
            "tier_score": 0,
            "source_bonus": 0,
            "keyword_matches": [],
            "category_bonus": 0,
            "severity_bonus": 0,
            "geographic_bonus": 0,
            "final_score": 0
        }
        
        # Tier-based scoring (0-40 points) - most important factor
        tier_score = 0
        if tier == PriorityTier.TIER_1_CRITICAL:
            tier_score = 40
        elif tier == PriorityTier.TIER_2_IMPORTANT:
            tier_score = 25
        elif tier == PriorityTier.TIER_3_GENERAL:
            tier_score = 10
        score += tier_score
        details["tier_score"] = tier_score
        
        # Source authority (0-20 points)
        source_score = self.SOURCE_PRIORITY.get(event.source, 20)
        source_bonus = min(source_score / 100 * 20, 20)
        score += source_bonus
        details["source_bonus"] = round(source_bonus, 2)
        
        # Keyword matching (0-20 points)
        title_lower = (event.title or "").lower() 
        desc_lower = (event.description or "").lower()
        combined_text = title_lower + " " + desc_lower
        
        keyword_matches = []
        all_keywords = []
        if tier == PriorityTier.TIER_1_CRITICAL:
            for keywords in self.TIER_1_KEYWORDS.values():
                all_keywords.extend(keywords)
        elif tier == PriorityTier.TIER_2_IMPORTANT:
            for keywords in self.TIER_2_KEYWORDS.values():
                all_keywords.extend(keywords)
        else:
            for keywords in self.TIER_3_KEYWORDS.values():
                all_keywords.extend(keywords)
        
        for keyword in all_keywords:
            if keyword in combined_text:
                keyword_matches.append(keyword)
        
        keyword_score = min(len(keyword_matches) * 2, 20)
        score += keyword_score
        details["keyword_matches"] = keyword_matches[:10]
        details["keyword_score"] = round(keyword_score, 2)
        
        # Category bonus (0-10 points)
        category_bonus = 0
        high_impact_categories = [
            "Earthquake", "Severe Storms", "Wildfires", "Flood", "Cyclone",
            "Military", "Conflict", "Terror", "Cyberattack", "Pandemic"
        ]
        if event.category in high_impact_categories:
            category_bonus = 10
        elif event.category in ["Natural Event", "News", "Technology", "Health"]:
            category_bonus = 5
        score += category_bonus
        details["category_bonus"] = category_bonus
        
        # Severity bonus (0-10 points)
        severity_bonus = 0
        if event.severity == "Critical":
            severity_bonus = 10
        elif event.severity == "Elevated":
            severity_bonus = 7
        elif event.severity == "Watch":
            severity_bonus = 3
        score += severity_bonus
        details["severity_bonus"] = severity_bonus
        
        # Recency bonus (0-15 points)
        from datetime import datetime, timezone

        recency_bonus = 0

        try:
            if event.published_at:
                published = datetime.fromisoformat(
                    event.published_at.replace("Z", "+00:00")
                )

                hours_old = (
                    datetime.now(timezone.utc) - published
                ).total_seconds() / 3600

                if hours_old <= 3:
                    recency_bonus = 15
                elif hours_old <= 12:
                    recency_bonus = 10
                elif hours_old <= 24:
                    recency_bonus = 6
                elif hours_old <= 48:
                    recency_bonus = 3

                if hours_old > 72:
                    recency_bonus = -10 

        except Exception:   
            pass

        score += recency_bonus
        details["recency_bonus"] = recency_bonus

        # Cap at 100
        final_score = min(int(score), 100)
        details["final_score"] = final_score
        
        return final_score, details
    
    def calculate_confidence(self, event: Event) -> int:
        """Calculate confidence score (0-100) based on source reliability and data quality."""
        confidence = 50  # Base confidence
        
        # Source reliability (0-30 points)
        source_weight = self.SOURCE_PRIORITY.get(event.source, 20)
        confidence += min(source_weight / 100 * 30, 30)
        
        # Data completeness (0-20 points)
        if event.latitude and event.longitude:
            confidence += 10
        if event.location and event.location != "Global":
            confidence += 5
        if event.description and len(event.description) > 50:
            confidence += 5
        
        return min(int(confidence), 100)
    
    def is_low_impact(self, event: Event) -> Tuple[bool, str]:
        """Filter out low-value, repetitive, or non-global intelligence events."""

        title = (event.title or "").lower()
        desc = (event.description or "").lower()
        category = (event.category or "").lower()
        source = (event.source or "").lower()

        combined = f"{title} {desc} {category}"

        # ==========================================================
# REMOVE OLD EARTHQUAKE REPORTS
# ==========================================================

        if "earthquake" in combined or category == "earthquake":

            old_date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{4}-\d{2}-\d{2})'
            ]

            for pattern in old_date_patterns:
                match = re.search(pattern, combined)

                if match:
                    try:
                        date_str = match.group(1)

                        if "/" in date_str:
                            event_date = datetime.strptime(
                                date_str,
                                "%d/%m/%Y"
                            ).replace(tzinfo=timezone.utc)

                        else:
                            event_date = datetime.strptime(
                                date_str,
                                "%Y-%m-%d"
                            ).replace(tzinfo=timezone.utc)

                        age_days = (
                            datetime.now(timezone.utc) - event_date
                        ).days

                        if age_days > 3:
                            return True, "Old earthquake event"

                    except Exception:
                        pass

        # ==========================================================
        # REMOVE NWS WEATHER WARNINGS
        # ==========================================================

        nws_phrases = [
            "flood warning",
            "flood advisory",
            "flood watch",
            "flash flood warning",
            "special marine warning",
            "marine warning",
            "severe thunderstorm warning",
            "severe thunderstorm watch",
            "tornado warning",
            "heat advisory",
            "wind advisory",
            "dense fog advisory",
            "winter weather advisory",
            "small craft advisory",
            "special weather statement",
            "weather statement",
            "extreme heat warning",
            "heat warning",
            "excessive heat warning",
        ]

        if any(x in combined for x in nws_phrases):
            return True, "Routine weather alert"
        
        # ==========================================================
# REMOVE LOW-VALUE CISA POSTS FIRST
# ==========================================================

        if source == "cisa":

            cisa_blocked = [
                "router hygiene",
                "best practices",
                "guidance",
                "recommended practices",
                "security bulletin",
                "after action report",
                "lessons learned",
                "incident response",
                "known exploited vulnerabilities",
                "kev",
                "advisory",
                "alert",
                "technical advisory",
            ]

            if any(x in combined for x in cisa_blocked):
                return True, "Informational CISA cybersecurity advisory"
 
# ==========================================================
        # KEEP IMPORTANT EVENTS
        # ==========================================================

        keep_keywords = [
            "war",
            "military",
            "missile",
            "airstrike",
            "terror",
            "cyber attack",
            "cyberattack",
            "ransomware",
            "critical infrastructure",
            "tsunami",
            "volcano",
            "wildfire",
            "major wildfire",
            "hurricane",
            "typhoon",
            "cyclone",
            "major flood",
            "flash flood",
            "pandemic",
            "epidemic",
            "outbreak",
            "port closure",
            "airport shutdown",
            "bridge collapse",
            "power grid",
            "blackout",
        ]

        if any(k in combined for k in keep_keywords):
            return False, ""


        # ==========================================================
        # REMOVE CISA INFORMATIONAL POSTS
        # ==========================================================

        cisa_phrases = [
            "router hygiene",
            "china-nexus",
            "russian state-sponsored",
            "best practices",
            "guidance",
            "known exploited vulnerabilities",
            "advisory",
            "security bulletin",
            "recommended practices",
        ]

        if source == "cisa":
            informational = [
                "router hygiene",
                "best practices",
                "guidance",
                "recommended practices",
                "security bulletin",
                "lessons learned",
    "incident response engagement",
    "incident response",
    "after action report",
    "technical advisory",
            ]

            if any(x in combined for x in informational):
                return True, "Informational cybersecurity bulletin"
        # ==========================================================
        # REMOVE ENVIRONMENTAL TRACKING
        # ==========================================================

        environmental = [
            "iceberg",
            "ice shelf",
            "glacier",
            "sea ice",
        ]

        if any(x in combined for x in environmental):
            return True, "Environmental tracking"

        # ==========================================================
        # REMOVE SPORTS / ENTERTAINMENT / ETC.
        # ==========================================================
        exclusions = {
            "sports": [
                "football",
                "basketball",
                "baseball",
                "soccer",
                "tennis",
                "golf",
                "nfl",
                "nba",
                "mlb",
                "match",
                "game",
                "score",
            ],
            "entertainment": [
                "movie",
                "film",
                "actor",
                "actress",
                "celebrity",
                "concert",
                "album",
                "song",
            ],
            "opinion": [
                "opinion",
                "editorial",
                "column",
                "commentary",
                "op-ed",
            ],
            "local_crime": [
                "arrest",
                "burglary",
                "theft",
                "robbery",
            ],
            "traffic": [
                "traffic accident",
                "car crash",
                "vehicle accident",
            ],
            "small_fire": [
                "house fire",
                "building fire",
                "apartment fire",
            ],
            "minor_political": [
                "city council",
                "mayor",
                "local election",
            ],
            "small_protest": [
                "small protest",
                "demonstration",
            ],
            "routine_weather": [
                "weather forecast",
                "sunny",
                "cloudy",
                "chance of rain",
            ],
        }

        for reason, words in exclusions.items():
            if any(word in combined for word in words):
                return True, f"Excluded: {reason}"

        # MUST BE LAST LINE OF FUNCTION
        return False, ""
    
    def get_demo_events(self):
        """
        Demo intelligence events for mission-control visualization.
        """

        return [

            {
                "title": "Major Earthquake Detected Near Japan",
                "location": "Tokyo, Japan",
                "latitude": 35.6762,
                "longitude": 139.6503,
                "category": "Earthquake",
                "balanced_category": "natural_disaster",
                "severity": "Critical",
                "tone": "red",
                "demo": True,
                "impact_score": 92,
                "confidence": 96,
                "priority_tier": "TIER_1_CRITICAL",
                "intelligence_rank": 1,
                "source": "USGS",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "response_priority": "CRITICAL",
                "response_actions": [
                    "Monitor affected regions for situational awareness",
                    "Assess damage and coordinate emergency response assets",
                    "Prepare evacuation and relief operations if required"
                ],
                "response_confidence": 98
            },

            {
                "title": "Critical Infrastructure Cyber Attack Detected",
                "location": "Washington DC, United States",
                "latitude": 38.9072,
                "longitude": -77.0369,
                "category": "Cyberattack",
                "balanced_category": "cyber",
                "severity": "Critical",
                "tone": "purple",
                "demo": True,
                "impact_score": 90,
                "confidence": 94,
                "priority_tier": "TIER_1_CRITICAL",
                "intelligence_rank": 2,
                "source": "CISA",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "response_priority": "CRITICAL",
                "response_actions": [
                    "Isolate affected infrastructure and implement network segmentation",
                    "Patch exploited systems and apply security updates",
                    "Coordinate incident response with cybersecurity teams"
                ],
                "response_confidence": 96
            },

            {
                "title": "Wildfire Emergency Expanding",
                "location": "California, United States",
                "latitude": 36.7783,
                "longitude": -119.4179,
                "category": "Wildfire",
                "balanced_category": "natural_disaster",
                "severity": "Critical",
                "tone": "orange",
                "demo": True,
                "impact_score": 88,
                "confidence": 91,
                "priority_tier": "TIER_1_CRITICAL",
                "intelligence_rank": 3,
                "source": "NASA FIRMS",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "response_priority": "HIGH",
                "response_actions": [
                    "Monitor affected regions for situational awareness",
                    "Assess damage and coordinate emergency response assets",
                    "Prepare evacuation and relief operations if required"
                ],
                "response_confidence": 93
            },

            {
                "title": "Military Escalation Alert",
                "location": "Middle East",
                "latitude": 31.7683,
                "longitude": 35.2137,
                "category": "Military",
                "balanced_category": "geopolitical",
                "severity": "Critical",
                "tone": "crimson",
                "demo": True,
                "impact_score": 95,
                "confidence": 93,
                "priority_tier": "TIER_1_CRITICAL",
                "intelligence_rank": 4,
                "source": "Reuters",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "response_priority": "CRITICAL",
                "response_actions": [
                    "Monitor escalation indicators and diplomatic channels",
                    "Assess impact on regional stability and operations",
                    "Coordinate with security teams and adjust operational posture"
                ],
                "response_confidence": 94
            },

            {
                "title": "Major Port Disruption",
                "location": "Singapore",
                "latitude": 1.3521,
                "longitude": 103.8198,
                "category": "Infrastructure",
                "balanced_category": "infrastructure",
                "severity": "Elevated",
                "tone": "blue",
                "demo": True,
                "impact_score": 82,
                "confidence": 90,
                "priority_tier": "TIER_2_IMPORTANT",
                "intelligence_rank": 5,
                "source": "MarineTraffic",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "response_priority": "HIGH",
                "response_actions": [
                    "Activate alternate routes and contingency operations",
                    "Monitor disruption duration and impact scope",
                    "Coordinate with operators and stakeholders for resolution"
                ],
                "response_confidence": 91
            },

            {
                "title": "Volcanic Activity Increasing",
                "location": "Indonesia",
                "latitude": -6.2088,
                "longitude": 106.8456,
                "category": "Volcano",
                "balanced_category": "natural_disaster",
                "severity": "Elevated",
                "tone": "yellow",
                "demo": True,
                "impact_score": 80,
                "confidence": 89,
                "priority_tier": "TIER_2_IMPORTANT",
                "intelligence_rank": 6,
                "source": "NASA EONET",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "response_priority": "MODERATE",
                "response_actions": [
                    "Monitor affected regions for situational awareness",
                    "Assess damage and coordinate emergency response assets",
                    "Prepare evacuation and relief operations if required"
                ],
                "response_confidence": 90
            },

        ]

    def _is_low_value_alert(self, event: Dict[str, Any]) -> bool:
        """
        Final safety filter for events that should never reach frontend.
        """

        title = (event.get("title") or "").lower()
        desc = (event.get("description") or "").lower()
        source = (event.get("source") or "").lower()

        combined = f"{title} {desc}"

        blocked = [

            # NWS routine warnings
            "flood warning",
            "flood advisory",
            "flood watch",
            "special marine warning",
            "marine warning",
            "severe thunderstorm warning",
            "severe thunderstorm watch",
            "tornado warning",
            "wind advisory",
            "heat advisory",
            "small craft advisory",

            # routine weather
            "weather forecast",
            "forecast issued",
            "rain expected",
            "snow expected",

            # cyber advisories
            "router hygiene",
            "china-nexus",
            "russian state-sponsored",
            "security advisory",
            "cybersecurity advisory",
            "best practices",
            "guidance",
            # NWS routine coastal/weather alerts
            "rip current statement",
            "high surf warning",
            "coastal flood advisory",
            "beach hazard statement",
            "excessive heat warning",
            "freeze warning",
            "frost advisory",
            "lake wind advisory",
            "small craft advisory",
            "nearshore marine forecast",
            "hazardous weather outlook",

        ]

        return any(word in combined for word in blocked)

    def _apply_diversity_optimization(self, events: List[Dict[str, Any]], target_count: int = 10) -> List[Dict[str, Any]]:
        """
        Apply diversity optimization with strict rules:
        - Max 2 events per country (unless all are Critical/Tier 1)
        - Max 2 events per category
        - No duplicate wildfires in same state
        - No duplicate earthquakes within 200 km
        - Target ~10 diverse events
        """
        if not events:
            return events


        # FINAL FILTER BEFORE SELECTION
        events = [
            e for e in events
            if not self._is_low_value_alert(e)
        ]


        if not events:
            return []
        
        # Separate Tier 1 events (they get priority)
        tier1_events = [e for e in events if e.get("priority_tier") == "TIER_1_CRITICAL"]
        other_events = [e for e in events if e.get("priority_tier") != "TIER_1_CRITICAL"]
        
        # Track selections for diversity
        selected_countries = {}
        selected_categories = {}
        selected_wildfire_states = {}
        selected_earthquake_locations = []
        
        optimized_events = []
        
        # Process Tier 1 events first (they have priority)
        for event in tier1_events:
            region = self._get_geographic_region(event.get("location", ""))
            balanced_category = self._get_balanced_category(event)
            is_wildfire = self._is_wildfire(event)
            is_earthquake = event.get("category", "").lower() == "earthquake"
            state = self._extract_state_province(event.get("location", ""))
            lat = event.get("latitude")
            lng = event.get("longitude")
            
            # For Tier 1, allow up to 3 per country (more flexible)
            if region:
                country_count = selected_countries.get(region, 0)
                if country_count >= 3:
                    continue
            
            # Max 2 per category even for Tier 1
            category_count = selected_categories.get(balanced_category, 0)
            if category_count >= 2:
                continue
            
            # No duplicate wildfires in same state
            if is_wildfire and state and state in selected_wildfire_states:
                continue
            
            # No duplicate earthquakes within 200 km
            if is_earthquake and lat and lng:
                too_close = False
                for sel_lat, sel_lng in selected_earthquake_locations:
                    distance = self._haversine_distance(lat, lng, sel_lat, sel_lng)
                    if distance < 200:
                        too_close = True
                        break
                if too_close:
                    continue
            
            optimized_events.append(event)
            if region:
                selected_countries[region] = country_count + 1
            selected_categories[balanced_category] = category_count + 1
            if is_wildfire and state:
                selected_wildfire_states[state] = event
            if is_earthquake and lat and lng:
                selected_earthquake_locations.append((lat, lng))
        
        # Process other events (Tier 2 and 3)
        for event in other_events:
            if len(optimized_events) >= target_count:
                break
            
            region = self._get_geographic_region(event.get("location", ""))
            balanced_category = self._get_balanced_category(event)
            is_wildfire = self._is_wildfire(event)
            is_earthquake = event.get("category", "").lower() == "earthquake"
            state = self._extract_state_province(event.get("location", ""))
            lat = event.get("latitude")
            lng = event.get("longitude")
            
            # Max 2 per country for non-Tier 1
            if region:
                country_count = selected_countries.get(region, 0)
                if country_count >= 2:
                    continue
            
            # Max 2 per category
            category_count = selected_categories.get(balanced_category, 0)
            if category_count >= 2:
                continue
            
            # No duplicate wildfires in same state
            if is_wildfire and state and state in selected_wildfire_states:
                continue
            
            # No duplicate earthquakes within 200 km
            if is_earthquake and lat and lng:
                too_close = False
                for sel_lat, sel_lng in selected_earthquake_locations:
                    distance = self._haversine_distance(lat, lng, sel_lat, sel_lng)
                    if distance < 200:
                        too_close = True
                        break
                if too_close:
                    continue
            
            optimized_events.append(event)
            if region:
                selected_countries[region] = country_count + 1
            selected_categories[balanced_category] = category_count + 1
            if is_wildfire and state:
                selected_wildfire_states[state] = event
            if is_earthquake and lat and lng:
                selected_earthquake_locations.append((lat, lng))
        
        # Sort by: Priority Tier, Impact Score, Severity, Confidence, Recency
        tier_order = {"TIER_1_CRITICAL": 1, "TIER_2_IMPORTANT": 2, "TIER_3_GENERAL": 3}
        severity_order = {"Critical": 3, "Elevated": 2, "Watch": 1}
        
        optimized_events.sort(key=lambda x: (
            tier_order.get(x.get("priority_tier", "TIER_3_GENERAL"), 3),
            x.get("impact_score", 0),
            severity_order.get(x.get("severity", ""), 0),
            x.get("confidence", 0),
            x.get("published_at", "")
        ), reverse=True)
        
        return optimized_events[:target_count]
    
    def process_events(self, events: List[Event], target_count: int = 20) -> List[Dict[str, Any]]:
        """
        Process events through the priority-based intelligence pipeline.
        Always returns ~10 diverse events when possible.
        
        Args:
            events: List of events to process
            target_count: Target number of events to return (default 10)
        
        Returns:
            List of processed, scored, and ranked events with diversity optimization
        """
        processed_events = []
        filter_stats = {
            "low_impact": 0,
            "no_tier": 0,
            "duplicates": 0,
            "diversity_filtered": 0
        }
        
        # Step 1: Filter out low-impact events and assign tiers
        for event in events:
            # Filter out low-impact events
            is_low, reason = self.is_low_impact(event)
            if is_low:
                filter_stats["low_impact"] += 1
                self.logger.debug(f"Filtered out: {event.title} - {reason}")
                continue
            
            # Determine priority tier
            tier = self._determine_priority_tier(event)
            if not tier:
                filter_stats["no_tier"] += 1
                continue
            
            # Calculate impact score based on tier
            impact_score, score_details = self.calculate_impact_score(event, tier)
            
            # Calculate confidence
            confidence = self.calculate_confidence(event)
            
            # Create enriched event
            enriched_event = event.to_dict()
            enriched_event.update({
                "impact_score": impact_score,
                "confidence": confidence,
                "score_details": score_details,
                "priority_tier": tier.name,
                "intelligence_rank": 0,
                "balanced_category": self._get_balanced_category(enriched_event)
            })
            
            # Generate response actions for this event
            response_data = self._generate_response_actions(enriched_event)
            enriched_event.update(response_data)
            
            processed_events.append(enriched_event)
        
        self.logger.info(f"Processed {len(processed_events)} events after initial filtering")
        
        # Step 2: Apply diversity optimization

        
        processed_events.sort(
                key=lambda e: (
                    {"TIER_1_CRITICAL": 3,
                    "TIER_2_IMPORTANT": 2,
                    "TIER_3_GENERAL": 1}[e["priority_tier"]],
                    e["impact_score"],
                    e["confidence"],
                ),
                reverse=True,
        )

        optimized_events = self._apply_diversity_optimization(processed_events, target_count)
                
        if self.demo_mode:
             optimized_events.extend(self.get_demo_events())
        # Step 3: Assign ranks
        for idx, event in enumerate(optimized_events, 1):
            event["intelligence_rank"] = idx
        
        self.logger.info(
            f"Intelligence Engine: Processed {len(events)} events, "
            f"filtered {sum(filter_stats.values())}, "
            f"returning {len(optimized_events)} diverse events"
        )
        
        return optimized_events, filter_stats
    
    def _generate_response_actions(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate event-specific operational response actions based on category.
        Returns response priority, recommended actions, and confidence.
        """
        category = event.get("balanced_category", "other")
        impact_score = event.get("impact_score", 0)
        severity = event.get("severity", "Watch")
        confidence = event.get("confidence", 50)
        
        # Determine response priority based on impact and severity
        if impact_score >= 90 or severity == "Critical":
            priority = "CRITICAL"
        elif impact_score >= 80 or severity == "Elevated":
            priority = "HIGH"
        elif impact_score >= 70:
            priority = "MODERATE"
        else:
            priority = "LOW"
        
        # Generate category-specific response actions
        response_actions = []
        
        if category == "cyber":
            response_actions = [
                "Isolate affected infrastructure and implement network segmentation",
                "Patch exploited systems and apply security updates",
                "Coordinate incident response with cybersecurity teams"
            ]
        elif category == "natural_disaster":
            response_actions = [
                "Monitor affected regions for situational awareness",
                "Assess damage and coordinate emergency response assets",
                "Prepare evacuation and relief operations if required"
            ]
        elif category == "infrastructure":
            response_actions = [
                "Activate alternate routes and contingency operations",
                "Monitor disruption duration and impact scope",
                "Coordinate with operators and stakeholders for resolution"
            ]
        elif category == "geopolitical":
            response_actions = [
                "Monitor escalation indicators and diplomatic channels",
                "Assess impact on regional stability and operations",
                "Coordinate with security teams and adjust operational posture"
            ]
        elif category == "health":
            response_actions = [
                "Monitor outbreak progression and containment measures",
                "Assess public health impact and resource requirements",
                "Coordinate with health authorities and implement protective protocols"
            ]
        elif category == "economic":
            response_actions = [
                "Monitor market conditions and financial exposure",
                "Assess impact on operations and supply chains",
                "Implement risk mitigation and contingency financial measures"
            ]
        else:
            # Generic responses for other categories
            response_actions = [
                "Monitor situation development and gather additional intelligence",
                "Assess potential impact on operations and stakeholders",
                "Prepare contingency plans and coordinate with relevant teams"
            ]
        
        # Adjust confidence based on data quality
        response_confidence = min(confidence + 5, 95)  # Slight boost but cap at 95
        
        return {
            "response_priority": priority,
            "response_actions": response_actions,
            "response_confidence": response_confidence,
            "response_generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_intelligence_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate intelligence summary from processed events."""
        if not events:
            return {
                "threat_level": "Low",
                "total_events": 0,
                "categories": [],
                "top_sources": [],
                "average_impact": 0
            }
        
        # Calculate statistics
        categories = {}
        sources = {}
        total_impact = 0
        balanced_categories = {}
        regions = {}
        tier_counts = {}
        
        for event in events:
            cat = event.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            bal_cat = event.get("balanced_category", "other")
            balanced_categories[bal_cat] = balanced_categories.get(bal_cat, 0) + 1
            
            region = self._get_geographic_region(event.get("location", ""))
            if region:
                regions[region] = regions.get(region, 0) + 1
            
            src = event.get("source", "Unknown")
            sources[src] = sources.get(src, 0) + 1
            
            tier = event.get("priority_tier", "UNKNOWN")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            total_impact += event.get("impact_score", 0)
        
        # Determine threat level
        avg_impact = total_impact / len(events)
        if avg_impact >= 90:
            threat_level = "Critical"
        elif avg_impact >= 80:
            threat_level = "High"
        elif avg_impact >= 70:
            threat_level = "Elevated"
        else:
            threat_level = "Moderate"
        
        # Top sources
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "threat_level": threat_level,
            "total_events": len(events),
            "categories": list(categories.keys()),
            "balanced_categories": balanced_categories,
            "category_counts": categories,
            "regions": list(regions.keys()),
            "region_counts": regions,
            "tier_distribution": tier_counts,
            "top_sources": [{"source": s, "count": c} for s, c in top_sources],
            "average_impact": round(avg_impact, 2),
            "max_impact": max(e.get("impact_score", 0) for e in events),
            "min_impact": min(e.get("impact_score", 0) for e in events)
        }