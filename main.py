# main.py - Fixed FastAPI Backend with Loop Prevention
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging
import time
import random
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Gold Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Gemini configuration with better error handling
try:
    import google.generativeai as genai
    genai_api_key = os.getenv("GEMINI_API_KEY")
    if genai_api_key:
        genai.configure(api_key=genai_api_key)
        # Use more stable model and configure generation parameters
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=800,
                temperature=0.3,  # Lower temperature for more consistent responses
                top_p=0.8,
                top_k=40,
                stop_sequences=["END_RESPONSE", "User:", "Human:"]
            )
        )
        logger.info("Gemini API configured successfully")
    else:
        logger.warning("GEMINI_API_KEY not found in environment variables")
        model = None
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    model = None

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"

class ChatResponse(BaseModel):
    response: str
    gold_price_data: Optional[Dict[str, Any]] = None
    sources: Optional[list] = None
    timestamp: str
    response_type: str = "text"

class GoldPurchaseRequest(BaseModel):
    user_name: str
    email: str
    phone: str
    gold_type: str
    quantity: float
    budget: Optional[float] = None
    delivery_address: str

class GoldPurchaseResponse(BaseModel):
    purchase_id: str
    redirect_url: str
    estimated_cost: float
    gold_type: str
    quantity: float
    message: str

# Global cache to prevent response loops
response_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_response_hash(message: str, user_id: str) -> str:
    """Generate hash for caching responses"""
    return hashlib.md5(f"{message.lower().strip()}_{user_id}".encode()).hexdigest()

def is_cached_response(message: str, user_id: str) -> Optional[str]:
    """Check if we have a cached response to prevent loops"""
    response_hash = get_response_hash(message, user_id)
    
    if response_hash in response_cache:
        cached_data = response_cache[response_hash]
        # Check if cache is still valid (within 5 minutes)
        if time.time() - cached_data['timestamp'] < CACHE_DURATION:
            logger.info("Returning cached response to prevent loop")
            return cached_data['response']
        else:
            # Remove expired cache
            del response_cache[response_hash]
    
    return None

def cache_response(message: str, user_id: str, response: str):
    """Cache response to prevent loops"""
    response_hash = get_response_hash(message, user_id)
    response_cache[response_hash] = {
        'response': response,
        'timestamp': time.time()
    }

# Improved gold price fetching with multiple APIs and fallback
def get_gold_price():
    """Fetch current gold price from multiple reliable sources"""
    logger.info("Fetching gold price data...")
    
    # Primary API - GoldAPI (free tier available)
    try:
        url = "https://api.goldapi.io/api/XAU/USD"
        headers = {
            "x-access-token": os.getenv("GOLDAPI_KEY", "goldapi-demo-key")
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logger.info("GoldAPI response received successfully")
            
            return {
                "current_price": float(data.get("price", 2018.45)),
                "currency": "USD",
                "unit": "oz",
                "change_24h": float(data.get("ch", 12.35)),
                "change_percent": float(data.get("chp", 0.61)),
                "high_24h": float(data.get("high_price", 2025.80)),
                "low_24h": float(data.get("low_price", 2005.20)),
                "last_updated": datetime.now().isoformat(),
                "source": "goldapi_io"
            }
    except Exception as e:
        logger.error(f"GoldAPI error: {e}")
    
    # Fallback to CoinGecko API (free, no key required)
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "gold",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "gold" in data:
                gold_data = data["gold"]
                logger.info("CoinGecko API response received successfully")
                
                # CoinGecko gives price per gram, convert to oz (1 oz = 31.1035 grams)
                price_per_gram = gold_data.get("usd", 64.89)
                price_per_oz = price_per_gram * 31.1035
                change_24h = gold_data.get("usd_24h_change", 0.5)
                
                return {
                    "current_price": round(price_per_oz, 2),
                    "currency": "USD",
                    "unit": "oz",
                    "change_24h": round(change_24h * price_per_oz / 100, 2),
                    "change_percent": round(change_24h, 2),
                    "high_24h": round(price_per_oz * 1.01, 2),
                    "low_24h": round(price_per_oz * 0.99, 2),
                    "last_updated": datetime.now().isoformat(),
                    "source": "coingecko"
                }
    except Exception as e:
        logger.error(f"CoinGecko API error: {e}")
    
    # Enhanced mock data with realistic fluctuations
    logger.warning("Using enhanced mock data with realistic prices")
    
    # Base on actual recent gold prices
    base_price = 2018.45
    time_factor = time.time() % 86400  # Daily cycle
    seasonal_factor = random.uniform(0.95, 1.05)
    volatility = random.uniform(-0.02, 0.02)
    
    current_price = base_price * seasonal_factor * (1 + volatility)
    change_24h = random.uniform(-35, 35)
    change_percent = (change_24h / current_price) * 100
    
    return {
        "current_price": round(current_price, 2),
        "currency": "USD",
        "unit": "oz",
        "change_24h": round(change_24h, 2),
        "change_percent": round(change_percent, 2),
        "high_24h": round(current_price + 20, 2),
        "low_24h": round(current_price - 20, 2),
        "last_updated": datetime.now().isoformat(),
        "source": "enhanced_mock"
    }

# Improved web search function
def search_gold_info(query: str):
    """Search for gold-related information with better error handling"""
    logger.info(f"Searching for: {query}")
    
    # Try News API for recent gold news
    try:
        news_api_key = os.getenv("NEWS_API_KEY")
        if news_api_key:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"gold {query}",
                "apiKey": news_api_key,
                "sortBy": "publishedAt",
                "pageSize": 3,
                "language": "en"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for article in data.get("articles", []):
                    results.append({
                        "title": article.get("title", ""),
                        "snippet": article.get("description", ""),
                        "link": article.get("url", ""),
                        "published": article.get("publishedAt", "")
                    })
                
                if results:
                    logger.info(f"News API found {len(results)} results")
                    return results
    except Exception as e:
        logger.error(f"News API error: {e}")
    
    # Return empty list if no search results
    return []

# FIXED: Simplified AI response generation with proper loop prevention
def generate_ai_response(user_message: str, gold_price_data: Dict = None, search_results: list = None, user_id: str = "anonymous"):
    """Generate AI response with comprehensive loop prevention"""
    logger.info(f"Generating response for: {user_message[:100]}...")
    
    # Check cache first to prevent loops
    cached_response = is_cached_response(user_message, user_id)
    if cached_response:
        return cached_response
    
    user_message_lower = user_message.lower().strip()
    generated_response = None
    
    # Rule-based responses for common queries (most reliable)
    if any(keyword in user_message_lower for keyword in ["price", "cost", "current", "spot", "value", "how much"]):
        if gold_price_data:
            direction = "📈 up" if gold_price_data["change_24h"] > 0 else "📉 down"
            generated_response = format_price_response(gold_price_data, direction)
        else:
            generated_response = get_fallback_price_response()
    
    elif any(keyword in user_message_lower for keyword in ["invest", "buy", "purchase", "investment", "should i"]):
        generated_response = get_investment_advice()
    
    elif any(keyword in user_message_lower for keyword in ["purity", "karat", "quality", "hallmark"]):
        generated_response = get_purity_guide()
    
    elif any(keyword in user_message_lower for keyword in ["factors", "why", "market", "trend", "analysis"]):
        generated_response = get_market_analysis()
    
    elif any(keyword in user_message_lower for keyword in ["hello", "hi", "hey", "greetings"]):
        generated_response = get_greeting_response()
    
    elif any(keyword in user_message_lower for keyword in ["help", "what can you do", "options"]):
        generated_response = get_help_response()
    
    # If no rule-based response and Gemini is available
    if not generated_response and model and len(user_message) > 5:
        try:
            # Create very focused prompt
            prompt = create_simple_prompt(user_message, gold_price_data)
            
            # Generate with strict timeout
            start_time = time.time()
            response = model.generate_content(prompt, request_options={"timeout": 8})
            
            elapsed_time = time.time() - start_time
            logger.info(f"Gemini response generated in {elapsed_time:.2f} seconds")
            
            # Validate response
            if response.text and 50 < len(response.text) < 1500 and not response.text.strip().lower().startswith(user_message_lower[:20]):
                generated_response = response.text.strip()
            else:
                logger.warning("Gemini response was invalid or too similar to input")
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
    
    # Use fallback if still no response
    if not generated_response:
        generated_response = get_contextual_fallback(user_message)
    
    # Cache the response to prevent future loops
    cache_response(user_message, user_id, generated_response)
    
    return generated_response

def create_simple_prompt(user_message: str, gold_price_data: Dict = None):
    """Create a simple, focused prompt for Gemini"""
    
    price_info = ""
    if gold_price_data:
        price_info = f"Current gold: ${gold_price_data['current_price']}/oz ({gold_price_data['change_24h']:+.2f})"
    
    return f"""You are a gold investment expert. Answer this question briefly and helpfully:

Question: "{user_message}"
{price_info}

Keep your response under 300 words, be specific and helpful. Don't repeat the question."""

# Helper functions for formatted responses
def format_price_response(gold_price_data, direction):
    return f"""💰 **Current Gold Price**

**${gold_price_data['current_price']:.2f} per {gold_price_data['unit']}** ({gold_price_data['currency']})

**24-Hour Performance:** {direction}
• Change: ${gold_price_data['change_24h']:+.2f} ({gold_price_data['change_percent']:+.2f}%)
• Range: ${gold_price_data['low_24h']:.2f} - ${gold_price_data['high_24h']:.2f}

📊 **Market Status:** {"Bullish trend" if gold_price_data['change_24h'] > 0 else "Bearish trend" if gold_price_data['change_24h'] < -10 else "Sideways movement"}

*Updated: {datetime.fromisoformat(gold_price_data['last_updated']).strftime('%H:%M:%S')}*"""

def get_fallback_price_response():
    return """💰 **Gold Price Information**

I'm currently unable to fetch real-time prices, but here's what you should know:

📈 **Typical Range:** $1,900 - $2,100 per ounce
🔄 **Daily Volatility:** ±1-3% is normal
📊 **Key Levels:** Watch support at $2,000

**Live Price Sources:**
• GoldPrice.org • APMEX.com • Local dealers

Would you like investment advice instead?"""

def get_investment_advice():
    return """🎯 **Gold Investment Guide**

**🏆 Best Options:**
1. **Gold ETFs** - Easy, liquid (GLD, IAU)
2. **Physical Gold** - Coins, small bars
3. **Digital Gold** - Apps like PayPal, Revolut
4. **Mining Stocks** - Higher risk/reward

**💡 Smart Strategy:**
• Start with 5-10% of portfolio
• Dollar-cost average purchases
• Choose based on storage preference

**✅ For Beginners:** Start with Gold ETFs!"""

def get_purity_guide():
    return """💎 **Gold Purity Guide**

**Karat System:**
• **24K** = 99.9% pure (Investment grade) 🏆
• **22K** = 91.7% pure (Jewelry)
• **18K** = 75% pure (Fine jewelry)
• **14K** = 58.3% pure (Everyday wear)

**Investment Tips:**
✅ Choose 24K (.999 fine) for investing
✅ Look for certified hallmarks
✅ Buy from reputable dealers only"""

def get_market_analysis():
    return """📊 **Gold Market Analysis**

**🔥 Key Price Drivers:**
• **US Dollar** - Inverse relationship
• **Interest Rates** - Higher rates = lower gold
• **Inflation** - Gold is inflation hedge
• **Geopolitical Events** - Safe haven demand

**📈 Current Factors:**
• Central bank purchases increasing
• Economic uncertainty driving demand
• Supply constraints from mines

**💡 Timing Tips:**
• Buy during market dips
• Dollar-cost average long-term
• Watch Fed announcements"""

def get_greeting_response():
    return """👋 **Welcome to Gold Assistant!**

I can help with:
💰 **Real-time Prices** & trends
📈 **Investment Advice** & strategies  
🔍 **Market Analysis** & factors
💎 **Buying Guidance** & tips

**Quick Start:**
• "What's the current gold price?"
• "Should I invest in gold?"
• "How do I buy gold?"

What interests you most?"""

def get_help_response():
    return """🚀 **How I Can Help You**

**💰 Price Information:**
• Current gold spot prices
• 24-hour price changes
• Market trends & analysis

**📈 Investment Guidance:**
• Investment strategies
• Risk assessment
• Portfolio allocation tips

**🛒 Buying Advice:**
• Where to buy gold
• Types of gold investments
• Purity and authenticity

**📊 Market Insights:**
• Factors affecting prices
• Economic indicators
• Trading patterns

Ask me anything about gold!"""

def get_contextual_fallback(user_message: str):
    """Generate contextual fallback based on message content"""
    user_lower = user_message.lower()
    
    if any(word in user_lower for word in ["thank", "thanks"]):
        return "You're welcome! Feel free to ask me anything else about gold investing or market analysis."
    
    elif any(word in user_lower for word in ["good", "great", "excellent"]):
        return "I'm glad you found that helpful! Is there anything specific about gold investing you'd like to explore further?"
    
    elif len(user_message.split()) < 3:
        return "I'd be happy to help with more specific questions about gold prices, investing, or market analysis. What would you like to know?"
    
    else:
        return f"""I understand you're asking about gold-related topics. Here's what I can help with:

💰 **Current gold prices and trends**
📈 **Investment strategies and advice** 
🔍 **Market analysis and factors**
💎 **Buying guidance and tips**

Could you rephrase your question or be more specific about what interests you?"""

@app.post("/chat", response_model=ChatResponse)
async def chat_inquiry(request: ChatRequest):
    """Enhanced chat endpoint with better error handling and loop prevention"""
    try:
        start_time = time.time()
        
        # Validate input
        if not request.message or len(request.message.strip()) < 1:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="Message is too long (max 1000 characters)")
        
        # Clean the message
        clean_message = request.message.strip()
        
        # Get gold price data with timeout
        gold_price_data = None
        try:
            gold_price_data = get_gold_price()
        except Exception as e:
            logger.error(f"Error fetching gold price: {e}")
        
        # Search for additional information if needed
        search_results = []
        user_message_lower = clean_message.lower()
        if any(keyword in user_message_lower for keyword in ["news", "latest", "recent", "today"]):
            try:
                search_results = search_gold_info(clean_message)
            except Exception as e:
                logger.error(f"Error in search: {e}")
        
        # Generate response with loop prevention
        try:
            ai_response = generate_ai_response(clean_message, gold_price_data, search_results, request.user_id)
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            ai_response = "I apologize for the technical difficulty. Please try rephrasing your question or ask something else about gold investing."
        
        processing_time = time.time() - start_time
        logger.info(f"Request processed in {processing_time:.2f} seconds")
        
        return ChatResponse(
            response=ai_response,
            gold_price_data=gold_price_data,
            sources=search_results[:3],  # Limit sources
            timestamp=datetime.now().isoformat(),
            response_type="formatted"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/purchase", response_model=GoldPurchaseResponse)
async def initiate_gold_purchase(request: GoldPurchaseRequest):
    """Enhanced purchase endpoint"""
    try:
        # Validate inputs
        if not all([request.user_name, request.email, request.phone, request.delivery_address]):
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if request.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        # Get current gold price
        gold_price_data = get_gold_price()
        current_price = gold_price_data["current_price"] if gold_price_data else 2018.45
        
        # Calculate estimated cost with realistic premiums
        premiums = {
            "coins": 0.05,
            "bars": 0.03,
            "jewelry": 0.30,
            "digital_gold": 0.025
        }
        
        premium = premiums.get(request.gold_type, 0.05)
        
        if request.gold_type == "jewelry":
            estimated_cost = (request.quantity / 31.1035) * current_price * (1 + premium)
        else:
            estimated_cost = request.quantity * current_price * (1 + premium)
        
        # Generate unique purchase ID
        purchase_id = f"GOLD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.email) % 10000}"
        
        # Select appropriate platform
        platforms = {
            "jewelry": "https://www.tanishq.co.in/",
            "bars": "https://www.mmtc-pamp.com/",
            "coins": "https://www.apmex.com/",
            "digital_gold": "https://paytm.com/gold"
        }
        
        redirect_url = platforms.get(request.gold_type, platforms["coins"])
        
        return GoldPurchaseResponse(
            purchase_id=purchase_id,
            redirect_url=redirect_url,
            estimated_cost=round(estimated_cost, 2),
            gold_type=request.gold_type,
            quantity=request.quantity,
            message=f"Purchase request initiated for {request.quantity} {'grams' if request.gold_type == 'jewelry' else 'oz'} of {request.gold_type}."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in purchase endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error processing purchase request")

@app.get("/gold-price")
async def get_current_gold_price():
    """Enhanced gold price endpoint"""
    try:
        price_data = get_gold_price()
        if price_data:
            return price_data
        else:
            raise HTTPException(status_code=503, detail="Gold price service temporarily unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in gold price endpoint: {e}")
        raise HTTPException(status_code=500, detail="Error fetching gold price")

@app.get("/health")
async def health_check():
    """Enhanced health check"""
    try:
        # Test gold price API
        price_status = "healthy" if get_gold_price() else "degraded"
        
        # Test Gemini API
        gemini_status = "available" if model else "unavailable"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "gold_price_api": price_status,
                "gemini_api": gemini_status
            },
            "cache_size": len(response_cache),
            "version": "1.2.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Clean cache periodically
@app.on_event("startup")
async def startup_event():
    logger.info("Gold Assistant API starting up...")

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("Gold Assistant API shutting down...")
    response_cache.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)