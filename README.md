# 🤖 FitScore Calculator - AI-Powered Candidate Evaluation

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive candidate evaluation system that calculates a "FitScore" to assess how well a candidate matches a job position. Features GPT-4o-mini integration for intelligent analysis and a beautiful web interface.

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set OpenAI API Key (Optional)**
```bash
# Option 1: Environment variable
export OPENAI_API_KEY="your-api-key-here"

# Option 2: .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### **3. Run the Application**
```bash
python main.py
```

### **4. Open Your Browser**
Go to: **http://localhost:8000**

## 🌐 Features

- **🤖 GPT-4o-mini Integration**: Smart context detection and enhanced analysis
- **📊 Comprehensive Scoring**: 7 evaluation categories with dynamic weights
- **🎯 Elite Standards**: 8.2+ score threshold for submittable candidates
- **🌐 Beautiful Web Interface**: Modern UI with interactive charts
- **🔌 RESTful API**: Full API endpoints for integration
- **📱 Responsive Design**: Works on desktop, tablet, and mobile

## 📁 Project Structure

```
fitscore-calculator/
├── main.py                          # FastAPI application
├── fitscore_calculator.py           # Core FitScore calculator
├── templates/
│   └── index.html                   # Web interface
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
├── LICENSE                         # MIT license
└── .gitignore                      # Git ignore rules
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| POST | `/calculate-fitscore` | JSON-based calculation |
| POST | `/calculate-fitscore-form` | Form-based calculation |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API docs |

## 📊 Scoring Categories

- **Education (20%)**: Tier-based school evaluation
- **Career Trajectory (20%)**: Progression analysis
- **Company Relevance (15%)**: Industry-specific matching
- **Tenure Stability (15%)**: Job stability evaluation
- **Most Important Skills (20%)**: Skills matching
- **Bonus Signals (5%)**: Exceptional achievements
- **Red Flags (-15%)**: Risk assessment

## 🚀 Deployment

### **Local Development**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Docker**
```bash
docker build -t fitscore-calculator .
docker run -p 8000:8000 fitscore-calculator
```

### **Cloud Platforms**
- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **Render**: Connect GitHub repo
- **AWS/GCP/Azure**: Use provided Dockerfile

## 🔒 Security

- API keys stored as environment variables
- Input validation with Pydantic
- HTTPS recommended for production
- Rate limiting for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎉 Ready to evaluate candidates with AI-powered insights!**

Visit `http://localhost:8000` to start using the FitScore Calculator. 
