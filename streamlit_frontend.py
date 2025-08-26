# streamlit_app.py - Improved Streamlit Frontend
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

# Enhanced Custom CSS for better UI
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF6B35 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .price-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        50% { box-shadow: 0 12px 40px rgba(102,126,234,0.3); }
        100% { box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
    }
    
    /* Chat styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 2px solid #f0f2f6;
        border-radius: 15px;
        background: #fafafa;
        margin-bottom: 1rem;
    }
    
    .chat-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #FFD700;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        animation: slideIn 0.3s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196F3;
        margin-left: 10%;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 4px solid #9c27b0;
        margin-right: 10%;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Response formatting */
    .formatted-response {
        line-height: 1.6;
        font-size: 14px;
    }
    
    .formatted-response h1, .formatted-response h2, .formatted-response h3 {
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .formatted-response ul, .formatted-response ol {
        margin: 1rem 0;
        padding-left: 2rem;
    }
    
    .formatted-response li {
        margin: 0.5rem 0;
    }
    
    .formatted-response strong {
        color: #e74c3c;
        font-weight: 600;
    }
    
    .formatted-response code {
        background: #f8f9fa;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: monospace;
    }
    
    /* Purchase card */
    .purchase-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-healthy {
        background-color: #4CAF50;
        animation: blink 2s infinite;
    }
    
    .status-warning {
        background-color: #FF9800;
    }
    
    .status-error {
        background-color: #f44336;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #FFD700;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Sidebar styling */
    .sidebar-content {
        padding: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FFD700;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_prices' not in st.session_state:
    st.session_state.current_prices = {}
if 'price_history' not in st.session_state:
    st.session_state.price_history = []
if 'last_price_update' not in st.session_state:
    st.session_state.last_price_update = None

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust this to your FastAPI backend URL
METALS_API_KEY = "your_metals_api_key"  # Replace with your actual API key

# Helper Functions
def get_gold_prices():
    """Fetch current gold prices from API"""
    try:
        # Mock data for demonstration - replace with actual API call
        mock_prices = {
            'XAU': 2050.50,
            'XAG': 25.75,
            'XPT': 950.25,
            'XPD': 1425.80
        }
        
        # In real implementation, use something like:
        # response = requests.get(f"https://api.metals.live/v1/spot", 
        #                        headers={"X-API-KEY": METALS_API_KEY})
        # if response.status_code == 200:
        #     return response.json()
        
        return mock_prices
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
        return {}

def send_message_to_backend(message: str, context: Dict[str, Any] = None):
    """Send message to FastAPI backend"""
    try:
        payload = {
            "message": message,
            "context": context or {}
        }
        
        # Replace with actual backend call
        # response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        # if response.status_code == 200:
        #     return response.json()
        
        # Mock response for demonstration
        mock_response = {
            "response": f"Thank you for your question: '{message}'. Based on current market conditions, gold is showing strong performance with prices at $2,050.50/oz. I'd recommend considering dollar-cost averaging for long-term investment strategies.",
            "context": {
                "intent": "investment_advice",
                "entities": ["gold", "investment"],
                "sentiment": "neutral"
            }
        }
        return mock_response
        
    except Exception as e:
        return {"response": f"Sorry, I'm having trouble connecting to the backend. Error: {e}", "context": {}}

def format_message(text: str) -> str:
    """Format markdown text for display"""
    # Simple markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text

def calculate_investment_metrics(amount: float, price: float, duration_months: int):
    """Calculate investment metrics"""
    shares = amount / price
    monthly_investment = amount / duration_months if duration_months > 0 else amount
    
    # Mock calculations for demonstration
    projected_return = amount * 1.08  # 8% annual return assumption
    risk_score = "Moderate"
    
    return {
        'shares': shares,
        'monthly_investment': monthly_investment,
        'projected_return': projected_return,
        'risk_score': risk_score
    }

# Main App Layout
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🥇 Gold Assistant</h1>
        <p>Your Smart Gold Investment Companion</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        st.title("⚙️ Settings")
        
        # API Configuration
        st.subheader("API Configuration")
        api_key = st.text_input("Metals API Key", type="password", value=METALS_API_KEY)
        backend_url = st.text_input("Backend URL", value=API_BASE_URL)
        
        # Investment Preferences
        st.subheader("Investment Preferences")
        risk_tolerance = st.selectbox("Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
        investment_horizon = st.selectbox("Investment Horizon", ["Short-term (< 1 year)", "Medium-term (1-5 years)", "Long-term (> 5 years)"])
        
        # Quick Actions
        st.subheader("Quick Actions")
        if st.button("🔄 Refresh Prices"):
            st.session_state.current_prices = get_gold_prices()
            st.session_state.last_price_update = datetime.now()
            st.success("Prices updated!")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
        
        # System Status
        st.subheader("System Status")
        status_html = f"""
        <div>
            <span class="status-indicator status-healthy"></span>Price Feed: Active<br>
            <span class="status-indicator status-healthy"></span>AI Assistant: Online<br>
            <span class="status-indicator status-warning"></span>Backend: Demo Mode
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Main Content Area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Current Prices Section
        st.subheader("📈 Live Gold Prices")
        
        # Update prices
        if not st.session_state.current_prices or (
            st.session_state.last_price_update and 
            (datetime.now() - st.session_state.last_price_update).seconds > 300
        ):
            st.session_state.current_prices = get_gold_prices()
            st.session_state.last_price_update = datetime.now()
        
        if st.session_state.current_prices:
            price_cols = st.columns(4)
            metals = [
                ("Gold (XAU)", "XAU", "🥇"),
                ("Silver (XAG)", "XAG", "🥈"),
                ("Platinum (XPT)", "XPT", "⚪"),
                ("Palladium (XPD)", "XPD", "⚫")
            ]
            
            for i, (name, symbol, emoji) in enumerate(metals):
                with price_cols[i]:
                    if symbol in st.session_state.current_prices:
                        price = st.session_state.current_prices[symbol]
                        change = "+1.2%"  # Mock change
                        color = "green" if "+" in change else "red"
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{emoji} {name}</h4>
                            <h2>${price:.2f}</h2>
                            <p style="color: {color};">{change}</p>
                        </div>
                        """, unsafe_allow_html=True)

        # Price Chart
        st.subheader("📊 Price Trends")
        
        # Generate mock price history for demonstration
        dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
        gold_prices = [2000 + (i * 2) + ((-1) ** i * 10) for i in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=gold_prices,
            mode='lines+markers',
            name='Gold Price',
            line=dict(color='#FFD700', width=3),
            marker=dict(color='#FFA500', size=6)
        ))
        
        fig.update_layout(
            title="Gold Price Trend (30 Days)",
            xaxis_title="Date",
            yaxis_title="Price (USD/oz)",
            template="plotly_white",
            hovermode='x',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Chat Interface
        st.subheader("💬 Chat with Gold Assistant")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if st.session_state.chat_history:
                for i, (role, message, timestamp) in enumerate(st.session_state.chat_history):
                    message_class = "user-message" if role == "user" else "assistant-message"
                    formatted_message = format_message(message)
                    
                    st.markdown(f"""
                    <div class="chat-message {message_class}">
                        <small><strong>{'You' if role == 'user' else 'Assistant'}</strong> - {timestamp}</small>
                        <div class="formatted-response">{formatted_message}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="chat-message assistant-message">
                    <strong>Gold Assistant:</strong> Hello! I'm here to help you with gold investment advice, market analysis, and pricing information. Ask me anything about gold investing!
                </div>
                """, unsafe_allow_html=True)

        # Chat Input
        user_input = st.text_input("Ask me about gold investing...", key="user_input", placeholder="e.g., Should I buy gold now? What's the best investment strategy?")
        
        col_send, col_examples = st.columns([1, 3])
        with col_send:
            send_button = st.button("Send 📨", type="primary")
        
        with col_examples:
            example_questions = st.selectbox(
                "Quick Examples:",
                ["Select a question...", 
                 "What's the current market outlook for gold?",
                 "How much gold should I buy with $10,000?",
                 "Is now a good time to invest in gold?",
                 "What are the risks of gold investment?",
                 "How does inflation affect gold prices?"]
            )

        # Handle message sending
        if send_button and user_input:
            # Add user message to chat
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append(("user", user_input, timestamp))
            
            # Get response from backend
            with st.spinner("Thinking..."):
                context = {
                    "current_prices": st.session_state.current_prices,
                    "risk_tolerance": risk_tolerance,
                    "investment_horizon": investment_horizon
                }
                response_data = send_message_to_backend(user_input, context)
                
                # Add assistant response to chat
                assistant_response = response_data.get("response", "I'm sorry, I couldn't process your request.")
                st.session_state.chat_history.append(("assistant", assistant_response, timestamp))
            
            st.rerun()
        
        elif example_questions != "Select a question...":
            # Handle example question selection
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append(("user", example_questions, timestamp))
            
            with st.spinner("Thinking..."):
                context = {
                    "current_prices": st.session_state.current_prices,
                    "risk_tolerance": risk_tolerance,
                    "investment_horizon": investment_horizon
                }
                response_data = send_message_to_backend(example_questions, context)
                assistant_response = response_data.get("response", "I'm sorry, I couldn't process your request.")
                st.session_state.chat_history.append(("assistant", assistant_response, timestamp))
            
            st.rerun()

    with col2:
        # Investment Calculator
        st.subheader("🧮 Investment Calculator")
        
        with st.container():
            investment_amount = st.number_input("Investment Amount ($)", min_value=100, max_value=1000000, value=5000, step=100)
            metal_choice = st.selectbox("Metal", ["Gold (XAU)", "Silver (XAG)", "Platinum (XPT)", "Palladium (XPD)"])
            investment_duration = st.slider("Investment Duration (months)", 1, 60, 12)
            
            if st.button("Calculate", type="primary"):
                metal_symbol = metal_choice.split("(")[1].split(")")[0]
                current_price = st.session_state.current_prices.get(metal_symbol, 2000)
                
                metrics = calculate_investment_metrics(investment_amount, current_price, investment_duration)
                
                st.markdown(f"""
                <div class="purchase-card">
                    <h4>Investment Summary</h4>
                    <p><strong>Shares/Ounces:</strong> {metrics['shares']:.4f}</p>
                    <p><strong>Monthly Investment:</strong> ${metrics['monthly_investment']:.2f}</p>
                    <p><strong>Projected Value:</strong> ${metrics['projected_return']:.2f}</p>
                    <p><strong>Risk Level:</strong> {metrics['risk_score']}</p>
                </div>
                """, unsafe_allow_html=True)

        # Market News (Mock)
        st.subheader("📰 Market News")
        
        news_items = [
            {
                "title": "Gold Reaches New Monthly High",
                "summary": "Gold prices surge amid economic uncertainty...",
                "time": "2 hours ago",
                "sentiment": "positive"
            },
            {
                "title": "Federal Reserve Policy Update",
                "summary": "Latest Fed announcement impacts precious metals...",
                "time": "4 hours ago",
                "sentiment": "neutral"
            },
            {
                "title": "Mining Production Report",
                "summary": "Global gold production shows mixed results...",
                "time": "1 day ago",
                "sentiment": "negative"
            }
        ]
        
        for news in news_items:
            sentiment_color = {"positive": "#4CAF50", "neutral": "#FF9800", "negative": "#f44336"}[news["sentiment"]]
            
            st.markdown(f"""
            <div style="
                background: white; 
                padding: 1rem; 
                border-radius: 8px; 
                margin: 0.5rem 0; 
                border-left: 4px solid {sentiment_color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            ">
                <h5 style="margin: 0; color: #2c3e50;">{news['title']}</h5>
                <p style="margin: 0.5rem 0; color: #7f8c8d; font-size: 0.9rem;">{news['summary']}</p>
                <small style="color: #95a5a6;">{news['time']}</small>
            </div>
            """, unsafe_allow_html=True)

        # Performance Metrics
        st.subheader("📊 Performance Metrics")
        
        metrics_data = {
            "Today's High": "$2,055.30",
            "Today's Low": "$2,045.80",
            "52-Week High": "$2,150.75",
            "52-Week Low": "$1,810.20",
            "Market Cap": "$2.1T",
            "Volume": "125.5K oz"
        }
        
        for metric, value in metrics_data.items():
            st.markdown(f"""
            <div class="metric-card" style="margin: 0.25rem 0;">
                <strong>{metric}:</strong> {value}
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()