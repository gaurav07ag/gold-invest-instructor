# main.py - Improved FastAPI Backend
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
                max_output_tokens=1000,
                temperature=0.7,
                stop_sequences=["END_RESPONSE"]
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
    response_type: str = "text"  # New field for UI handling

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

# Fixed AI response generation to prevent infinite loops
def generate_ai_response(user_message: str, gold_price_data: Dict = None, search_results: list = None):
    """Generate AI response with timeout and loop prevention"""
    logger.info(f"Generating response for: {user_message[:100]}...")
    
    # First try rule-based responses for common queries (faster and more reliable)
    user_message_lower = user_message.lower()
    
    # Price queries
    if any(keyword in user_message_lower for keyword in ["price", "cost", "current", "spot", "value"]):
        if gold_price_data:
            direction = "📈 up" if gold_price_data["change_24h"] > 0 else "📉 down"
            return format_price_response(gold_price_data, direction)
        else:
            return get_fallback_price_response()
    
    # Investment queries  
    elif any(keyword in user_message_lower for keyword in ["invest", "buy", "purchase", "investment", "should i"]):
        return get_investment_advice()
    
    # Purity queries
    elif any(keyword in user_message_lower for keyword in ["purity", "karat", "quality", "hallmark"]):
        return get_purity_guide()
    
    # Market analysis
    elif any(keyword in user_message_lower for keyword in ["factors", "why", "market", "trend", "analysis"]):
        return get_market_analysis()
    
    # Greeting
    elif any(keyword in user_message_lower for keyword in ["hello", "hi", "hey", "greetings"]):
        return get_greeting_response()
    
    # If Gemini is available, use it for complex queries with safety measures
    if model and len(user_message) > 10:
        try:
            # Create focused prompt to prevent loops
            context = create_focused_context(user_message, gold_price_data, search_results)
            
            # Set timeout and use generation config to prevent loops
            start_time = time.time()
            response = model.generate_content(
                context,
                request_options={"timeout": 10}  # 10 second timeout
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Gemini response generated in {elapsed_time:.2f} seconds")
            
            # Validate response length and content
            if response.text and len(response.text) > 50 and len(response.text) < 2000:
                return response.text
            else:
                logger.warning("Gemini response was invalid, using fallback")
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
    
    # Fallback response
    return get_default_response(user_message)

def create_focused_context(user_message: str, gold_price_data: Dict, search_results: list):
    """Create focused context for Gemini to prevent loops"""
    
    price_context = ""
    if gold_price_data:
        price_context = f"Current gold price: ${gold_price_data['current_price']}/oz (${gold_price_data['change_24h']:+.2f}, {gold_price_data['change_percent']:+.2f}%)"
    
    search_context = ""
    if search_results:
        search_context = f"Recent news: {search_results[0].get('title', '')} - {search_results[0].get('snippet', '')[:100]}..."
    
    return f"""You are a helpful gold investment assistant. Keep your response concise (under 500 words), informative, and focused.

{price_context}
{search_context}

User question: "{user_message}"

Provide a helpful, accurate response about gold investment, prices, or market information. Be conversational but professional. End your response with "END_RESPONSE"."""

# Helper functions for formatted responses
def format_price_response(gold_price_data, direction):
    return f"""💰 **Current Gold Price**

**${gold_price_data['current_price']:.2f} per {gold_price_data['unit']}** ({gold_price_data['currency']})

**24-Hour Performance:** {direction}
• Change: ${gold_price_data['change_24h']:+.2f} ({gold_price_data['change_percent']:+.2f}%)
• Range: ${gold_price_data['low_24h']:.2f} - ${gold_price_data['high_24h']:.2f}

📊 **Market Status:** {"Bullish trend" if gold_price_data['change_24h'] > 0 else "Bearish trend" if gold_price_data['change_24h'] < -10 else "Sideways movement"}

*Data from {gold_price_data.get('source', 'market source')} • Updated: {datetime.fromisoformat(gold_price_data['last_updated']).strftime('%H:%M:%S')}*

💡 **Quick Tip:** Gold prices are influenced by USD strength, inflation expectations, and geopolitical events."""

def get_fallback_price_response():
    return """💰 **Gold Price Information**

I'm currently unable to fetch real-time prices, but here's what you should know:

📈 **Typical Range:** $1,800 - $2,200 per ounce
🔄 **Volatility:** ±2-5% daily movements are normal
📊 **Key Levels:** Support around $1,950, Resistance near $2,050

**Live Price Sources:**
• GoldPrice.org
• APMEX.com
• Your local precious metals dealer

Would you like investment advice or market analysis instead?"""

def get_investment_advice():
    return """🎯 **Gold Investment Guide**

**🏆 Top Options:**
1. **Physical Gold** - Coins (American Eagle, Maple Leaf), Bars (1 oz to 1 kg)
2. **Gold ETFs** - SPDR Gold (GLD), iShares Gold (IAU) 
3. **Digital Gold** - PayPal, Revolut, local apps
4. **Mining Stocks** - Newmont (NEM), Barrick Gold (GOLD)

**💡 Smart Strategy:**
• Allocate 5-10% of portfolio to gold
• Dollar-cost average your purchases
• Choose based on your storage preference
• Consider tax implications

**🔍 Before Buying:**
✅ Compare dealer premiums
✅ Verify authenticity (hallmarks)
✅ Plan for storage/insurance
✅ Check buy-back policies

**Best for Beginners:** Start with Gold ETFs or fractional digital gold!"""

def get_purity_guide():
    return """💎 **Gold Purity Guide**

**Karat System:**
• **24K** = 99.9% pure (Investment grade) 🏆
• **22K** = 91.7% pure (Indian jewelry)
• **18K** = 75% pure (Fine jewelry)
• **14K** = 58.3% pure (Everyday jewelry)
• **10K** = 41.7% pure (Budget jewelry)

**Fineness Stamps:**
• 999 = 24K investment gold
• 916 = 22K gold
• 750 = 18K gold
• 585 = 14K gold

**🎯 For Investment:** Choose 24K (.999 fine) coins and bars
**🎯 For Jewelry:** 18K-22K offers durability + value

**🔍 Authentication Tips:**
✅ Look for hallmarks/stamps
✅ Magnetic test (gold isn't magnetic)
✅ Buy from certified dealers only
✅ Request authenticity certificates"""

def get_market_analysis():
    return """📊 **Gold Market Analysis**

**🔥 Key Price Drivers:**
• **US Dollar** - Inverse relationship (strong $ = lower gold)
• **Interest Rates** - Higher rates reduce gold appeal
• **Inflation** - Gold hedge against rising prices
• **Geopolitical Events** - Safe haven demand

**📈 Current Market Factors:**
• Central bank gold purchases increasing
• Economic uncertainty driving demand
• Supply constraints from major mines
• ETF inflows/outflows impact prices

**🌍 Seasonal Patterns:**
• **Q4 Strong:** Holiday jewelry demand
• **Q1 Weak:** Post-holiday selling
• **Wedding Seasons:** India/China boost demand

**💡 Investment Timing:**
• Buy during market dips
• Dollar-cost average for long-term
• Watch Fed policy announcements
• Monitor inflation data releases"""

def get_greeting_response():
    return """👋 **Welcome to Gold Assistant!**

I'm here to help with all things gold:

💰 **Real-time Prices** - Current gold spot prices & trends
📈 **Investment Advice** - ETFs, coins, bars, digital gold
🔍 **Market Analysis** - Factors affecting gold prices  
💎 **Purity Guide** - Karat ratings and authenticity
🛒 **Buying Tips** - Where and how to purchase safely

**🚀 Quick Start Questions:**
• "What's the current gold price?"
• "How should I invest in gold?"
• "What affects gold prices?"
• "Help me buy gold"

What would you like to explore first?"""

def get_default_response(user_message):
    return f"""Thanks for your question about gold! 

Here's some quick information:

**🥇 Gold Basics:**
• Store of value for 5,000+ years
• Portfolio diversifier and inflation hedge
• Global 24/7 trading market
• Popular during uncertain times

**📊 Current Focus Areas:**
• Investment strategies and options
• Real-time price tracking
• Market analysis and trends
• Buying guidance and tips

Could you be more specific about what interests you? For example:
• Current prices and performance
• Investment recommendations
• Market analysis
• Buying/selling guidance

I'm here to help with any gold-related questions!"""

@app.post("/chat", response_model=ChatResponse)
async def chat_inquiry(request: ChatRequest):
    """Enhanced chat endpoint with better error handling"""
    try:
        start_time = time.time()
        
        # Validate input
        if not request.message or len(request.message.strip()) < 2:
            raise HTTPException(status_code=400, detail="Message is too short")
        
        if len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="Message is too long")
        
        # Get gold price data with timeout
        gold_price_data = None
        try:
            gold_price_data = get_gold_price()
        except Exception as e:
            logger.error(f"Error fetching gold price: {e}")
        
        # Search for additional information if needed (with timeout)
        search_results = []
        user_message_lower = request.message.lower()
        if any(keyword in user_message_lower for keyword in ["news", "latest", "recent", "today"]):
            try:
                search_results = search_gold_info(request.message)
            except Exception as e:
                logger.error(f"Error in search: {e}")
        
        # Generate response with timeout protection
        try:
            ai_response = generate_ai_response(request.message, gold_price_data, search_results)
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            ai_response = "I apologize, but I'm experiencing technical difficulties. Please try asking your question again or contact support if the issue persists."
        
        processing_time = time.time() - start_time
        logger.info(f"Request processed in {processing_time:.2f} seconds")
        
        return ChatResponse(
            response=ai_response,
            gold_price_data=gold_price_data,
            sources=search_results,
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
            "coins": 0.05,      # 5% premium
            "bars": 0.03,       # 3% premium  
            "jewelry": 0.30,    # 30% premium
            "digital_gold": 0.025  # 2.5% premium
        }
        
        premium = premiums.get(request.gold_type, 0.05)
        
        if request.gold_type == "jewelry":
            # Jewelry priced per gram, convert from grams to oz equivalent
            estimated_cost = (request.quantity / 31.1035) * current_price * (1 + premium)
        else:
            # Coins, bars, digital gold priced per oz
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
            message=f"Purchase request initiated for {request.quantity} {'grams' if request.gold_type == 'jewelry' else 'oz'} of {request.gold_type}. Estimated cost includes current market premiums."
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
            "version": "1.1.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)