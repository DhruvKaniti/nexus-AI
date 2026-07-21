from flask import Blueprint, jsonify, request
import asyncio
import os
import json
from datetime import datetime, timezone
from app.services.event_aggregator import EventAggregator
import logging

bp = Blueprint('global_scan', __name__)
logger = logging.getLogger(__name__)


@bp.route('/global-scan', methods=['GET'])
def get_global_events():
    """
    Global High-Impact Intelligence Scan
    
    Returns 10-12 events with Impact Score ≥75 and Confidence ≥80%
    Optimized for geographic and category diversity
    Sorted by impact, severity, and recency
    """
    try:
        limit = int(request.args.get('limit', 10))
        logger.info(f"🔍 Global scan requested with limit={limit}")
        
        # Get NewsAPI key if configured
        newsapi_key = os.getenv('NEWSAPI_KEY')
        logger.info(f"🔑 NewsAPI key configured: {'Yes' if newsapi_key else 'No'}")
        
        # Create aggregator with all sources
        logger.info("🏗️ Creating EventAggregator...")
        aggregator = EventAggregator(newsapi_key=newsapi_key)
        logger.info(f"📊 Aggregator initialized with {len(aggregator.sources)} sources")
        
        # Run async aggregation
        try:
            loop = asyncio.get_event_loop()
            logger.info("♻️ Using existing event loop")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info("🆕 Created new event loop")
        
        logger.info("🚀 Starting intelligence aggregation...")
        result = loop.run_until_complete(aggregator.aggregate(limit=limit))
        
        # Log intelligence summary
        if 'intelligence_summary' in result:
            summary = result['intelligence_summary']
            logger.info(
                f"✅ Intelligence scan complete: {result.get('count', 0)} high-impact events | "
                f"Threat Level: {summary.get('threat_level', 'Unknown')} | "
                f"Avg Impact: {summary.get('average_impact', 0)}"
            )
        else:
            logger.info(
                f"✅ Global scan complete: {result.get('count', 0)} events from "
                f"{', '.join(result.get('sources_used', []))}"
            )
        
        # Add metadata
        result['api_version'] = '2.1'
        result['filter_criteria'] = {
            'min_impact_score': 75,
            'min_confidence': 80,
            'max_results': min(limit, 12),  # Cap at 12 for diversity
            'raw_events_fetched': result.get('raw_events_collected', 0),
            'diversity_rules': {
                'max_per_country': 2,
                'max_per_category': 2,
                'max_wildfire_per_state': 1,
                'max_earthquake_300km': 1
            }
        }
        logger.info(json.dumps(result.get("events", [])[0], indent=2))
        return jsonify(result)
        
          
    except Exception as e:
        logger.error(f"❌ Unexpected error in global scan: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "api_version": "2.1",
            "filter_criteria": {
                "min_impact_score": 75,
                "min_confidence": 80,
                "max_results": 10
            }
        }), 500


@bp.route('/intelligence-summary', methods=['GET'])
def get_intelligence_summary():
    """
    Get intelligence summary without full event details
    """
    try:
        limit = int(request.args.get('limit', 10))
        logger.info(f"🔍 Intelligence summary requested with limit={limit}")
        
        # Get NewsAPI key if configured
        newsapi_key = os.getenv('NEWSAPI_KEY')
        
        # Create aggregator and run
        aggregator = EventAggregator(newsapi_key=newsapi_key)
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(aggregator.aggregate(limit=limit))
        
        # Return only summary
        if 'intelligence_summary' in result:
            return jsonify({
                'summary': result['intelligence_summary'],
                'timestamp': result.get('timestamp'),
                'sources_used': result.get('sources_used', [])
            })
        else:
            return jsonify({
                'error': 'No intelligence summary available',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Error in intelligence summary: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "Nexus Intelligence Engine",
        "version": "2.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
