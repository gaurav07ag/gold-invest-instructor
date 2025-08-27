# streamlit_app.py - Fixed Integration Code
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
import time
import re

# Configure Streamlit page
st.set_page_config(
    page_title="Gold Assistant - Your Smart Gold Investment Companion",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000"  # Make sure this matches your FastAPI server

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_prices' not in st.session_state:
    st.session_state.current_prices = {}
if 'last_price_update' not in st.session_state:
    st.session_state.last_price_update = None

def check_backend_health():
    """Check if backend is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        return False

def get_gold_prices():
    """Fetch current gold prices from backend API"""
    try:
        response = requests.get(f"{API_BASE_URL}/gold-price", timeout=10)
        if response.status_code == 200:
            price_data = response.json()
            return {
                'XAU': price_data.get('current_price', 2000.0),
                'timestamp': price_data.get('last_updated'),
                'change_24h': price_data.get('change_24h', 0),
                'change_percent': price_data.get('change_percent', 0),
                'high_24h': price_data.get('high_24h', 0),
                'low_24h': price_data.get('low_24h', 0)
            }
        else:
            st.warning(f"Price API returned status {response.status_code}")
            return get_mock_prices()
    except Exception as e:
        return get_mock_prices()

def get_mock_prices():
    """Fallback mock prices when backend is unavailable"""
    return {
        'XAU': 2050.50,
        'XAG': 25.75,
        'XPT': 950.25,
        'XPD': 1425.80,
        'timestamp': datetime.now().isoformat(),
        'change_24h': 12.35,
        'change_percent': 0.61,
        'high_24h': 2065.25,
        'low_24h': 2035.80
    }

def send_message_to_backend(message: str, user_id: str = "streamlit_user"):
    """Send message to FastAPI backend with correct payload structure"""
    try:
        # Correct payload structure matching ChatRequest model
        payload = {
            "message": message,
            "user_id": user_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat", 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Backend returned status {response.status_code}. Please try again.",
                "gold_price_data": None,
                "sources": None,
                "timestamp": datetime.now().isoformat()
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "response": "❌ Cannot connect to backend server. Please ensure the FastAPI server is running on http://localhost:8000",
            "gold_price_data": None
        }
    except requests.exceptions.Timeout:
        return {
            "response": "⏰ Request timed out. Please try again with a shorter question.",
            "gold_price_data": None
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "gold_price_data": None
        }

def format_message(text: str) -> str:
    """Format markdown text for display"""
    # Simple markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Convert bullet points
    text = re.sub(r'^• ', r'&bull; ', text, flags=re.MULTILINE)
    # Convert newlines to <br>
    text = text.replace('\n', '<br>')
    return text

def display_price_data(price_data):
    """Display gold price data if available"""
    if price_data:
        change_color = "green" if price_data.get('change_24h', 0) >= 0 else "red"
        change_symbol = "+" if price_data.get('change_24h', 0) >= 0 else ""
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 1rem 0;
        ">
            <h4>📊 Current Gold Price Update</h4>
            <h2>${price_data.get('current_price', 'N/A')}/oz</h2>
            <p style="color: {change_color};">
                {change_symbol}{price_data.get('change_24h', 0):.2f} 
                ({change_symbol}{price_data.get('change_percent', 0):.2f}%)
            </p>
            <small>Updated: {price_data.get('last_updated', 'N/A')}</small>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.title("🥇 Gold Assistant")
    st.subheader("Your Smart Gold Investment Companion")
    
    # Check backend health
    backend_healthy = check_backend_health()
    
    if backend_healthy:
        st.success("✅ Connected to backend server")
    else:
        st.error("❌ Backend server not available. Please start the FastAPI server.")
        st.info("Run: `uvicorn main:app --reload` in your backend directory")
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings & Controls")
        
        # Backend URL configuration
        backend_url = st.text_input("Backend URL", value=API_BASE_URL)
        if backend_url != API_BASE_URL:
            st.warning("Backend URL changed. Click 'Test Connection' to verify.")
        
        if st.button("🔄 Test Connection"):
            try:
                response = requests.get(f"{backend_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("Connection successful!")
                else:
                    st.error(f"Connection failed: Status {response.status_code}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
        
        if st.button("🔄 Refresh Prices"):
            st.session_state.current_prices = get_gold_prices()
            st.session_state.last_price_update = datetime.now()
            st.success("Prices updated!")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
        
        st.divider()
        
        # Quick Actions in Sidebar
        st.subheader("🚀 Quick Actions")
        
        example_questions = [
            "What's the current gold price?",
            "Should I invest in gold now?", 
            "How do gold prices move?",
            "What affects gold prices?",
            "Investment advice for beginners"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"sidebar_{hash(question)}"):
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.chat_history.append(("user", question, timestamp))
                
                with st.spinner("🤔 Processing..."):
                    response_data = send_message_to_backend(question)
                    assistant_response = response_data.get("response", "Sorry, I couldn't process your request.")
                    st.session_state.chat_history.append(("assistant", assistant_response, timestamp))
                
                st.rerun()
        
        st.divider()
        
        # System Status
        st.subheader("🔧 System Status")
        
        if backend_healthy:
            st.success("🟢 Backend: Online")
        else:
            st.error("🔴 Backend: Offline")
        
        st.info(f"🕒 Last Update: {st.session_state.last_price_update.strftime('%H:%M:%S') if st.session_state.last_price_update else 'Never'}")

    # Main content area (now single column layout)
    # Current Prices Section
    st.subheader("📈 Live Gold Prices")
    
    # Update prices if needed
    if not st.session_state.current_prices or (
        st.session_state.last_price_update and 
        (datetime.now() - st.session_state.last_price_update).seconds > 300
    ):
        st.session_state.current_prices = get_gold_prices()
        st.session_state.last_price_update = datetime.now()
    
    # Display current prices
    if st.session_state.current_prices:
        xau_price = st.session_state.current_prices.get('XAU', 'N/A')
        change_24h = st.session_state.current_prices.get('change_24h', 0)
        change_percent = st.session_state.current_prices.get('change_percent', 0)
        
        col_price1, col_price2, col_price3, col_price4 = st.columns(4)
        
        with col_price1:
            st.metric(
                label="🥇 Gold (XAU)",
                value=f"${xau_price}",
                delta=f"{change_24h:+.2f} ({change_percent:+.2f}%)"
            )
        
        with col_price2:
            st.metric(
                label="🥈 Silver (XAG)", 
                value=f"${st.session_state.current_prices.get('XAG', 'N/A')}",
                delta="+0.50 (+2.0%)"
            )
        
        with col_price3:
            st.metric(
                label="💍 Platinum (XPT)",
                value=f"${st.session_state.current_prices.get('XPT', 'N/A')}",
                delta="-5.25 (-0.5%)"
            )
        
        with col_price4:
            st.metric(
                label="🔹 Palladium (XPD)",
                value=f"${st.session_state.current_prices.get('XPD', 'N/A')}",
                delta="+15.30 (+1.1%)"
            )

    st.divider()

    # Chat Interface
    st.subheader("💬 Chat with Gold Assistant")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for i, (role, message, timestamp) in enumerate(st.session_state.chat_history):
                if role == "user":
                    with st.chat_message("user"):
                        st.write(f"**You:** {message}")
                        st.caption(f"🕒 {timestamp}")
                else:
                    with st.chat_message("assistant"):
                        st.markdown(format_message(message), unsafe_allow_html=True)
                        st.caption(f"🤖 {timestamp}")
        else:
            st.info("👋 Hello! I'm your Gold Assistant. Ask me anything about gold investing, current prices, or market analysis!")
            
            # Show example conversations
            st.markdown("""
            **Try asking me:**
            - "What's the current gold price?"
            - "Should I invest in gold now?"
            - "How do economic factors affect gold prices?"
            - "What are the best ways to buy gold?"
            - "Is gold a good hedge against inflation?"
            """)

    # Chat input - MUST be at the top level, outside of any columns or containers
    user_input = st.chat_input("Ask me about gold investing...")
    
    # Process user input
    if user_input:
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append(("user", user_input, timestamp))
        
        # Get response from backend
        with st.spinner("🤔 Thinking..."):
            response_data = send_message_to_backend(user_input)
            
            # Add assistant response to chat
            assistant_response = response_data.get("response", "Sorry, I couldn't process your request.")
            st.session_state.chat_history.append(("assistant", assistant_response, timestamp))
            
            # Display price data if included in response
            if response_data.get("gold_price_data"):
                display_price_data(response_data["gold_price_data"])
        
        st.rerun()

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>
            💡 <strong>Gold Assistant</strong> - Powered by FastAPI & Streamlit | 
            Real-time prices and AI-powered insights
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()