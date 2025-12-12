"""
Simplified risk calculation - FAST version for beginners
"""
import chess
import numpy as np
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stockfish_analyzer import StockfishAnalyzer
from src.position_features import PositionFeatures


@dataclass
class RiskMetrics:
    """Simple risk metrics"""
    risk_score: float  # 0-100
    position_eval: float  # Centipawns
    complexity: float  # 0-100
    best_move: str
    top_moves: list  # Top 3 moves with scores


class RiskCalculator:
    """Fast, simplified risk calculator"""
    
    def __init__(self, stockfish_path: str = None, depth: int = 12):
        """Initialize with lower depth for speed"""
        self.analyzer = StockfishAnalyzer(stockfish_path, depth=depth, threads=2)
        self.feature_extractor = PositionFeatures()
    
    def calculate_risk_score(self, board: chess.Board) -> float:
        """Simple risk score based on position features"""
        features = self.feature_extractor.extract_all_features(board)
        
        # Simplified risk calculation
        complexity = features["complexity"]
        mobility = features["current_player_mobility"]
        
        # Count tactical elements
        legal_moves = list(board.legal_moves)
        checks = sum(1 for move in legal_moves if board.gives_check(move))
        captures = sum(1 for move in legal_moves if board.is_capture(move))
        
        tactical_density = min((checks * 5 + captures * 2), 50)
        
        # Combine factors (0-100 scale)
        risk = (complexity * 0.5) + (tactical_density * 0.5)
        
        return min(max(risk, 0), 100)
    
    def calculate_risk_metrics(self, board: chess.Board) -> RiskMetrics:
        """Calculate all metrics for a position"""
        # Get evaluation and best moves
        eval_result = self.analyzer.evaluate_position(board)
        top_moves = self.analyzer.get_top_moves(board, num_moves=3)
        
        # Calculate risk
        risk_score = self.calculate_risk_score(board)
        
        # Get complexity
        features = self.feature_extractor.extract_all_features(board)
        
        return RiskMetrics(
            risk_score=risk_score,
            position_eval=eval_result.score,
            complexity=features["complexity"],
            best_move=eval_result.best_move,
            top_moves=top_moves
        )
    
    def close(self):
        """Clean up"""
        self.analyzer.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
