# gold-invest-instructor

# 🥇 Gold Assistant - Smart Gold Investment Companion

A comprehensive AI-powered platform for gold investment guidance, real-time price tracking, and market analysis. Built with FastAPI backend and Streamlit frontend.

![Gold Assistant](https://img.shields.io/badge/Gold-Assistant-FFD700?style=for-the-badge&logo=gold)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

## ✨ Features...

### 🤖 AI-Powered Chat Assistant
- **Intelligent Responses**: Powered by Google Gemini AI with fallback to rule-based responses
- **Real-time Gold Prices**: Live market data integration with multiple API sources
- **Market Analysis**: Comprehensive insights into gold market trends and factors
- **Investment Guidance**: Personalized recommendations for different investment strategies...

### 📊 Real-Time Market Data
- **Live Gold Prices**: Current spot prices with 24-hour changes
- **Price Charts**: Interactive historical price trends
- **Market Indicators**: High/low ranges and percentage changes..
- **Multi-Source Data**: Reliable price feeds from multiple APIs with fallback mechanisms...

### 🛒 Purchase Integration
- **Buy Gold Online**: Direct integration with trusted gold dealers
- **Multiple Options**: Physical gold (coins, bars), jewelry, and digital gold
- **Cost Estimation**: Real-time pricing with dealer premiums
- **Secure Redirects**: Safe connections to verified gold platforms

### 💎 Investment Education
- **Purity Guide**: Complete karat and fineness explanations
- **Investment Options**: ETFs, physical gold, mining stocks, digital gold
- **Market Factors**: Understanding what drives gold prices
- **Buying Tips**: Best practices for gold purchases

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip or conda
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/gold-assistant.git
cd gold-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file in the root directory:
```env
# Required for AI responses (optional - has fallback)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional APIs for enhanced features
GOLDAPI_KEY=your_goldapi_key_here
NEWS_API_KEY=your_news_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

4. **Start the FastAPI backend**
```bash
# Terminal 1
python main.py
# or
uvicorn main:app --reload
```

5. **Launch the Streamlit frontend**
```bash
# Terminal 2
streamlit run streamlit_app.py
```

6. **Access the application**
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## 📋 Requirements

Create a `requirements.txt` file:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.1
requests==2.31.0
pydantic==2.5.0
python-dotenv==1.0.0
google-generativeai==0.3.2
plotly==5.17.0
pandas==2.1.3
python-multipart==0.0.6
```

## 🔧 Configuration

### API Keys Setup

#### 1. Google Gemini API (Recommended)
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Create a new API key
- Add to `.env`: `GEMINI_API_KEY=your_key_here`

#### 2. Gold Price APIs (Optional)
- **GoldAPI.io**: Professional gold price data
  - Sign up at [GoldAPI.io](https://goldapi.io/)
  - Add to `.env`: `GOLDAPI_KEY=your_key_here`

#### 3. News API (Optional)
- **NewsAPI**: Latest gold market news
  - Get free API key at [NewsAPI.org](https://newsapi.org/)
  - Add to `.env`: `NEWS_API_KEY=your_key_here`

#### 4. Search API (Optional)
- **SerpAPI**: Enhanced web search results
  - Register at [SerpAPI.com](https://serpapi.com/)
  - Add to `.env`: `SERPAPI_KEY=your_key_here`

### Fallback Mechanisms
The application works without any API keys using:
- Enhanced rule-based AI responses
- Mock gold price data with realistic fluctuations
- Built-in gold knowledge database

## 🏗️ Architecture

```
Gold Assistant
├── main.py              # FastAPI backend server
├── streamlit_app.py     # Streamlit frontend
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

### Backend (FastAPI)
- **Gold Price Service**: Multi-source price fetching with fallbacks
- **AI Chat Service**: Gemini AI integration with rule-based fallback
- **Search Service**: News and market information retrieval
- **Purchase Service**: Gold buying platform integration
- **Health Monitoring**: Service status and performance tracking

### Frontend (Streamlit)
- **Interactive Chat**: Real-time conversation with AI assistant
- **Price Dashboard**: Live gold price tracking and charts
- **Purchase Flow**: Guided gold buying experience
- **Market Analysis**: Educational content and market insights

## 🔌 API Endpoints

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "What's the current gold price?",
  "user_id": "optional_user_id"
}
```

### Gold Price Endpoint
```http
GET /gold-price
```

### Purchase Endpoint
```http
POST /purchase
Content-Type: application/json

{
  "user_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "gold_type": "coins",
  "quantity": 1.0,
  "budget": 2000.0,
  "delivery_address": "123 Main St, City, State"
}
```

### Health Check
```http
GET /health
```

## 🧪 Testing

### Test the Backend
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test gold price endpoint
curl http://localhost:8000/gold-price

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is gold?"}'
```

### Test the Frontend
1. Open http://localhost:8501
2. Try the quick question buttons
3. Send a custom message
4. Check the gold price display
5. Test the purchase flow

## 🔒 Security Features

- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: API timeout protection prevents infinite loops
- **Error Handling**: Graceful fallbacks for all external API failures
- **CORS Protection**: Configured CORS policies for web security
- **Data Privacy**: No sensitive user data stored or logged

## 🚨 Troubleshooting

### Common Issues

#### 1. "Connection refused" error
```bash
# Make sure FastAPI is running
python main.py
# Check if port 8000 is available
netstat -an | grep 8000
```

#### 2. Streamlit won't start
```bash
# Check if port 8501 is available
streamlit run streamlit_app.py --server.port 8502
```

#### 3. API key errors
```bash
# Verify .env file exists and has correct format
cat .env
# Check if environment variables are loaded
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

#### 4. Gold price not updating
- Check internet connection
- Verify API keys in `.env`
- Check logs for API rate limits
- The app works with mock data if APIs fail

#### 5. AI responses seem repetitive
- Ensure `GEMINI_API_KEY` is set correctly
- Check API quotas and limits
- Rule-based responses activate as fallback

## 🔄 Updates & Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Monitoring Logs
```bash
# Backend logs
python main.py 2>&1 | tee backend.log

# Check service status
curl http://localhost:8000/health
```

### Database Integration (Future)
For production deployment, consider adding:
- User authentication
- Chat history storage
- Purchase order tracking
- Analytics and reporting

## 🚀 Deployment

### Local Development
Already covered in Quick Start section.

### Production Deployment

#### Using Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8501

CMD ["bash", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
```

#### Using Cloud Platforms
- **Heroku**: Add `Procfile` and deploy
- **AWS**: Use EC2 or ECS with load balancers  
- **Google Cloud**: Deploy to Cloud Run or Compute Engine
- **Digital Ocean**: Use App Platform or Droplets

## 📊 Performance Optimization

### Backend Optimizations
- **Caching**: Implement Redis for gold price caching
- **Database**: Add PostgreSQL for chat history
- **Load Balancing**: Use multiple FastAPI instances
- **CDN**: Cache static content

### Frontend Optimizations  
- **Session State**: Optimize Streamlit session management
- **Lazy Loading**: Load charts and data on demand
- **Caching**: Use `@st.cache_data` for expensive operations

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update README for new functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI**: For intelligent chat responses
- **GoldAPI.io**: For reliable gold price data
- **Streamlit**: For the beautiful frontend framework
- **FastAPI**: For the high-performance backend
- **Plotly**: For interactive charts and visualizations

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/gold-assistant/issues)
- **Documentation**: Check the `/docs` endpoint when running
- **Community**: Join discussions in GitHub Discussions

## 🔮 Roadmap

### Version 2.0 (Planned)
- [ ] User authentication and profiles
- [ ] Portfolio tracking
- [ ] Email/SMS price alerts
- [ ] Mobile app (React Native)
- [ ] Multi-currency support
- [ ] Advanced charting tools

### Version 2.5 (Future)
- [ ] Machine learning price predictions
- [ ] Social trading features
- [ ] Integration with crypto exchanges
- [ ] Advanced risk analytics
- [ ] API marketplace integration

---

**⚠️ Disclaimer**: This application provides educational information about gold investment. Always consult with qualified financial advisors before making investment decisions. Gold prices are volatile and past performance does not guarantee future results.

---

Made with ❤️ and ☕ by Gaurav Singh 

**🌟 Star this repo if you found it helpful!**
