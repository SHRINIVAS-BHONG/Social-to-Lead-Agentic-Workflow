# 🎬 AutoStream AI Agent

> **AI-Powered Conversational Agent for Video Editing SaaS**  
> Transform social media conversations into qualified business leads using intelligent AI agents.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-FF6B6B.svg)](https://langchain-ai.github.io/langgraph/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Deployment](#-deployment)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**AutoStream AI Agent** is a production-ready conversational AI system designed for SaaS businesses. It intelligently engages with potential customers, answers product questions, and automatically captures qualified leads with email notifications.

### Key Capabilities

- 🤖 **Intelligent Conversations**: Natural language understanding with context awareness
- 🎯 **Intent Classification**: Automatically detects user intent (greeting, inquiry, high-intent)
- 📚 **RAG-Powered Responses**: Retrieves accurate information from knowledge base
- 📧 **Automated Lead Capture**: Collects name, email, and platform with email notifications
- 🎨 **Modern UI/UX**: Dark premium theme with glassmorphism effects
- 🔐 **Authentication System**: Sign in/Sign up with session management

---

## ✨ Features

### Core Features

- **Multi-Turn Conversations**: Maintains context across 5-6+ conversation turns
- **Smart Lead Qualification**: Asks for information one field at a time
- **Email Notifications**: Sends professional welcome emails to captured leads
- **Real-Time Intent Detection**: Visual badges showing current conversation intent
- **Knowledge Base Search**: FAISS vector store with semantic search
- **Session Management**: Isolated conversations per user session

### UI/UX Features

- **Dark Premium Theme**: Modern gradient backgrounds with animations
- **Glassmorphism Effects**: Frosted glass design throughout
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Slide-in, fade, and hover effects
- **Real-Time Updates**: Live typing indicators and message delivery

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **AI/ML**: LangGraph, HuggingFace Transformers
- **Vector Store**: FAISS with sentence-transformers
- **Email**: SMTP (Gmail, SendGrid, AWS SES)
- **State Management**: LangGraph StateGraph

### Frontend
- **Framework**: React 18+
- **Styling**: CSS3 with custom animations
- **HTTP Client**: Fetch API
- **Build Tool**: Create React App

### Infrastructure
- **API**: RESTful with FastAPI
- **CORS**: Enabled for cross-origin requests
- **Logging**: Structured JSON logging
- **Environment**: Python dotenv

---

## 📁 Project Structure

```
autostream-ai-agent/
├── backend/
│   ├── agent/
│   │   ├── graph.py          # LangGraph state machine
│   │   ├── nodes.py          # Agent node functions
│   │   ├── state.py          # State TypedDict
│   │   ├── session.py        # Session management
│   │   └── tools.py          # Lead capture & email
│   ├── config/
│   │   ├── settings.py       # Configuration
│   │   └── logging_config.py # Logging setup
│   ├── data/
│   │   └── knowledge.json    # Knowledge base
│   ├── rag/
│   │   ├── loader.py         # Document loader
│   │   └── vectorstore.py    # FAISS vector store
│   └── main.py               # FastAPI application
├── frontend/
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js            # Main app component
│       ├── App.css           # Global styles
│       ├── LandingPage.js    # Landing page
│       ├── Auth.js           # Authentication
│       ├── Chat.js           # Chat interface
│       ├── Chat.css          # Chat styles
│       └── api.js            # API client
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/autostream-ai-agent.git
cd autostream-ai-agent
```

### Step 2: Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
cd frontend
npm install
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# LLM Configuration (Required)
HUGGINGFACE_API_KEY=hf_your_token_here
LLM_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
LLM_TEMPERATURE=0.5

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com

# RAG Configuration
RAG_TOP_K=3
MAX_CONVERSATION_TURNS=6
```

### 2. Get HuggingFace API Key (Free)

1. Go to [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. Create free account (no credit card required)
3. Click "New token" → Create with "Read" access
4. Copy token to `.env` file

### 3. Email Setup (Optional)

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Add credentials to `.env`

**For SendGrid/AWS SES:** See deployment section

---

## 💻 Usage

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Test Conversation Flow

1. Open http://localhost:3000
2. Click "Sign Up" and create account
3. Start conversation:
   ```
   You: "Hi, tell me about your pricing"
   Agent: [Explains pricing plans]
   
   You: "I want the Pro plan for YouTube"
   Agent: [Asks for name]
   
   You: "John Doe"
   Agent: [Asks for email]
   
   You: "john@example.com"
   Agent: [Captures lead + sends email]
   ```

---

## 🏗 Architecture

### System Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│   FastAPI    │─────▶│  LangGraph  │
│  Frontend   │◀─────│   Backend    │◀─────│   Agent     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │    SMTP      │      │    FAISS    │
                     │   Server     │      │ Vector Store│
                     └──────────────┘      └─────────────┘
```

### LangGraph State Machine

```
classify_intent
    ├─[inquiry/greeting]─► retrieve_docs ─► generate_response
    └─[high_intent]──────► qualify_lead
                               ├─[ready]──► execute_tool ─► generate_response
                               └─[missing]─► generate_response
```

### Key Components

**1. Intent Classifier**
- Analyzes user messages
- Classifies into: greeting, inquiry, high_intent
- Routes to appropriate handler

**2. RAG Retrieval**
- Semantic search over knowledge base
- FAISS vector store with embeddings
- Returns top-3 relevant documents

**3. Lead Qualification**
- Extracts: name, email, platform
- Validates completeness
- Triggers tool when ready

**4. Tool Execution**
- Calls `mock_lead_capture()`
- Sends welcome email
- Returns confirmation

**5. Response Generator**
- Generates natural language replies
- Injects RAG context
- Handles multi-turn conversations

---

## 🌐 Deployment

### Option 1: Cloud Platforms

**Backend (Railway/Render/Fly.io)**

```bash
# Railway
railway up

# Render
render deploy

# Fly.io
fly deploy
```

**Frontend (Vercel/Netlify)**

```bash
# Vercel
vercel deploy

# Netlify
netlify deploy
```

### Option 2: Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Manual Server

```bash
# Backend
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
# Serve build/ folder with nginx or similar
```

### Environment Variables for Production

```env
# Production settings
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
LLM_TEMPERATURE=0.5
```

---

## 📚 API Documentation

### Endpoints

**POST /chat**
```json
{
  "message": "Hi, tell me about pricing",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "AutoStream offers two plans...",
  "session_id": "abc123",
  "intent": "inquiry",
  "lead_info": {},
  "lead_captured": false
}
```

**GET /health**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-21T12:00:00Z"
}
```

**GET /leads**
```json
[
  {
    "name": "John Doe",
    "email": "john@example.com",
    "platform": "YouTube",
    "captured_at": "2026-04-21T12:00:00Z"
  }
]
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write descriptive commit messages
- Add tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain/LangGraph** - Agent framework
- **HuggingFace** - LLM inference
- **FastAPI** - Backend framework
- **React** - Frontend framework
- **FAISS** - Vector similarity search

---

## 📞 Support

For questions or issues:

- **Email**: support@autostream.example.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/autostream-ai-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/autostream-ai-agent/discussions)

---

## 🎯 Roadmap

- [ ] Add more LLM providers (OpenAI, Anthropic)
- [ ] Implement user authentication with JWT
- [ ] Add conversation history persistence
- [ ] Create admin dashboard
- [ ] Add analytics and metrics
- [ ] Support multiple languages
- [ ] Add voice input/output
- [ ] Integrate with CRM systems

---

**Built with ❤️ for ServiceHive · Inflx Assignment**

*AutoStream AI Agent - Transforming conversations into opportunities*
