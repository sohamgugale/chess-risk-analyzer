# ♟️ Chess Risk Analyzer

**Quantitative chess analysis using financial risk modeling concepts**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 Features

- **📊 Risk Quantification**: Calculate position volatility, downside risk, and VaR
- **🎲 Monte Carlo Simulation**: Simulate possible continuations to assess uncertainty
- **🔍 Move Analysis**: Identify blunders, mistakes, and inaccuracies
- **📈 Visual Analytics**: Interactive charts and heatmaps
- **🌐 API Integration**: Analyze games from Chess.com and Lichess
- **👤 Personal Games**: Load your own games automatically

## 🚀 Quick Start

### Local Installation
```bash
# Clone repository
git clone https://github.com/sohamgugale/chess-risk-analyzer.git
cd chess-risk-analyzer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Stockfish
brew install stockfish  # Mac
# sudo apt-get install stockfish  # Linux

# Run the app
streamlit run app.py
```

### Docker Installation
```bash
docker build -t chess-risk-analyzer .
docker run -p 8501:8501 chess-risk-analyzer
```

## 📊 Risk Metrics Explained

### Risk Score (0-100)
Overall position risk combining multiple factors:
- **0-30**: Low risk, stable position
- **30-60**: Medium risk, some complications
- **60-100**: High risk, sharp tactical position

### Volatility
Standard deviation of evaluations across simulated continuations. Higher = more uncertain position.

### Value at Risk (VaR)
Worst-case evaluation at 95% confidence. Shows downside exposure.

### Tactical Density
Measure of tactical opportunities (checks, captures, threats).

## 📁 Project Structure
```
chess-risk-analyzer/
├── src/
│   ├── chess_engine.py          # Core chess operations
│   ├── stockfish_analyzer.py    # Engine integration
│   ├── game_parser.py           # PGN parsing
│   ├── position_features.py     # Feature extraction
│   ├── risk_calculator.py       # Risk metrics calculation
│   ├── game_analyzer.py         # Full game analysis
│   ├── visualizer.py            # Plotting utilities
│   └── chess_api.py             # Chess.com/Lichess API
├── app.py                       # Streamlit interface
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔧 Configuration

Adjust analysis settings in the sidebar:
- **Monte Carlo Simulations**: 5-25 (default: 12)
- **Engine Depth**: 8-16 (default: 12)
- **Max Moves**: 10-100 (default: 40)

## 📖 Usage Examples

### Analyze Your Games

1. Go to Chess.com and download your games
2. Upload PGN file or paste PGN text
3. Click "Analyze Game"
4. Explore visualizations and export data

### Compare Players
```python
from src.game_analyzer import GameAnalyzer

with GameAnalyzer(n_simulations=15, depth=12) as analyzer:
    analyses, report = analyzer.analyze_pgn_string(your_pgn)
    
    print(f"White accuracy: {report['white']['accuracy']:.1f}%")
    print(f"Black accuracy: {report['black']['accuracy']:.1f}%")
```

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

### Heroku
```bash
heroku create your-chess-analyzer
git push heroku main
heroku open
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Stockfish chess engine
- python-chess library
- Chess.com and Lichess APIs
- Financial risk modeling literature

## 📧 Contact

- GitHub: [@sohamgugale](https://github.com/sohamgugale)
- Chess.com: [Sohamgugale](https://chess.com/member/sohamgugale)
- Email: your.email@duke.edu

---

Built by a chess enthusiast