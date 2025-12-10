"""Fix import statements in all Python files"""
import os

files_to_fix = {
    'src/risk_calculator.py': [
        ('from src.stockfish_analyzer import StockfishAnalyzer\nfrom src.position_features import PositionFeatures',
         '''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stockfish_analyzer import StockfishAnalyzer
from src.position_features import PositionFeatures''')
    ],
    'src/game_analyzer.py': [
        ('from src.risk_calculator import RiskCalculator, RiskMetrics\nfrom src.game_parser import GameParser, GamePosition\nfrom src.stockfish_analyzer import StockfishAnalyzer',
         '''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk_calculator import RiskCalculator, RiskMetrics
from src.game_parser import GameParser, GamePosition
from src.stockfish_analyzer import StockfishAnalyzer''')
    ],
    'app.py': [
        ('from src.game_analyzer import GameAnalyzer\nfrom src.risk_calculator import RiskCalculator\nfrom src.visualizer import RiskVisualizer',
         '''import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.game_analyzer import GameAnalyzer
from src.risk_calculator import RiskCalculator
from src.visualizer import RiskVisualizer''')
    ]
}

for filepath, replacements in files_to_fix.items():
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"✓ Fixed {filepath}")
        
        with open(filepath, 'w') as f:
            f.write(content)
    else:
        print(f"✗ File not found: {filepath}")

print("\nDone! Now test with: python -m src.risk_calculator")
