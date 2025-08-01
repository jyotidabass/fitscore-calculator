# 🎯 FitScore Calculator

Advanced AI-powered candidate evaluation system with GPT-4o-mini integration for comprehensive hiring assessments.

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://fitscore-calculator.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple?style=for-the-badge&logo=openai)](https://openai.com)

## 🌐 Live Application

**🔗 Production URL:** [https://fitscore-calculator.vercel.app/](https://fitscore-calculator.vercel.app/)

## 🚀 Features

- **🤖 AI-Powered Analysis**: GPT-4o-mini integration for enhanced candidate evaluation
- **📊 Comprehensive Scoring**: Multi-dimensional assessment across 6 key categories
- **🎯 Smart Criteria Generation**: Dynamic evaluation criteria based on job context
- **📈 Visual Analytics**: Interactive charts and detailed breakdowns
- **⚡ Real-time Processing**: Fast evaluation with immediate results
- **🌍 Global Deployment**: Accessible worldwide via Vercel CDN

## 📋 Evaluation Categories

| Category | Weight | Description |
|----------|--------|-------------|
| **Education** | 20% | Academic background, institution tier, degree relevance |
| **Career Trajectory** | 20% | Professional progression, leadership experience |
| **Company Relevance** | 15% | Industry alignment, company type match |
| **Tenure Stability** | 15% | Job duration, career consistency |
| **Skills Match** | 20% | Technical skills alignment with job requirements |
| **Bonus Signals** | 5% | Additional positive indicators (awards, publications, etc.) |
| **Red Flags** | -15% | Negative indicators and concerns |

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **AI Integration**: OpenAI GPT-4o-mini
- **Charts**: Chart.js
- **Deployment**: Vercel
- **Database**: In-memory processing

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fitscore-calculator.git
   cd fitscore-calculator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Optional: Set your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open [http://localhost:8000](http://localhost:8000)
   - Start evaluating candidates!

### Production Deployment

The application is automatically deployed to Vercel and available at:
**https://fitscore-calculator.vercel.app/**

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface for candidate evaluation |
| `/calculate-fitscore` | POST | JSON API for FitScore calculation |
| `/calculate-fitscore-form` | POST | Form-based API for web interface |
| `/health` | GET | Health check endpoint |
| `/api-docs` | GET | API documentation |

## 🎯 Usage Examples

### Web Interface
1. Visit [https://fitscore-calculator.vercel.app/](https://fitscore-calculator.vercel.app/)
2. Enter candidate resume and job description
3. Click "Calculate FitScore"
4. View comprehensive results and recommendations

### API Usage
```python
import requests

response = requests.post(
    "https://fitscore-calculator.vercel.app/calculate-fitscore",
    json={
        "resume_text": "Candidate resume content...",
        "job_description": "Job description content...",
        "use_gpt4": True
    }
)

result = response.json()
print(f"FitScore: {result['total_score']}")
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `PORT`: Server port (default: 8000)

### Customization
- Modify scoring weights in `fitscore_calculator.py`
- Add new evaluation criteria
- Customize the UI in `templates/index.html`

## 📈 Performance

- **Response Time**: < 5 seconds for standard evaluations
- **AI Processing**: Enhanced with GPT-4o-mini for complex analysis
- **Scalability**: Serverless deployment on Vercel
- **Availability**: 99.9% uptime with global CDN

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini integration
- FastAPI for the excellent web framework
- Vercel for seamless deployment
- Tailwind CSS for beautiful styling

## 📞 Support

- **Live Demo**: [https://fitscore-calculator.vercel.app/](https://fitscore-calculator.vercel.app/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/fitscore-calculator/issues)
- **Documentation**: [API Docs](https://fitscore-calculator.vercel.app/api-docs)

---

**⭐ Star this repository if you find it helpful!** 
