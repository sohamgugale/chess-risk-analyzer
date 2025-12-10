"""
Core risk calculation using Monte Carlo simulation and stochastic modeling
"""
import chess
import chess.engine
from typing import List, Dict
import numpy as np
from dataclasses import dataclass
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stockfish_analyzer import StockfishAnalyzer
from src.position_features import PositionFeatures


@dataclass
class RiskMetrics:
    """Container for position risk metrics"""
    volatility: float
    expected_value: float
    downside_risk: float
    var_95: float
    complexity_risk: float
    tactical_density: float
    best_move_edge: float


class RiskCalculator:
    """Calculate position risk metrics using stochastic methods"""
    
    def __init__(self, stockfish_path: str = None, n_simulations: int = 20, depth: int = 12):
        """
        Initialize risk calculator
        
        Args:
            stockfish_path: Path to Stockfish binary (auto-detected if None)
            n_simulations: Number of Monte Carlo simulations
            depth: Stockfish search depth
        """
        self.analyzer = StockfishAnalyzer(stockfish_path, depth=depth)
        self.feature_extractor = PositionFeatures()
        self.n_simulations = n_simulations
    
    def sample_plausible_moves(self, board: chess.Board, n_samples: int = 10) -> List[chess.Move]:
        """Sample plausible moves using Stockfish top moves"""
        top_moves = self.analyzer.get_top_moves(board, num_moves=min(5, board.legal_moves.count()))
        
        if not top_moves:
            return []
        
        # Convert scores to probabilities using softmax
        scores = np.array([m["score"] for m in top_moves])
        scores = scores - scores.min() + 1
        
        temperature = 100
        probs = np.exp(scores / temperature) / np.sum(np.exp(scores / temperature))
        
        sampled_moves = []
        for _ in range(n_samples):
            idx = np.random.choice(len(top_moves), p=probs)
            move_str = top_moves[idx]["move"]
            try:
                move = chess.Move.from_uci(move_str)
                sampled_moves.append(move)
            except:
                continue
        
        return sampled_moves
    
    def monte_carlo_simulation(self, board: chess.Board, depth_horizon: int = 2) -> List[float]:
        """Run Monte Carlo simulation of possible continuations"""
        evaluations = []
        
        for _ in range(self.n_simulations):
            sim_board = board.copy()
            
            for _ in range(depth_horizon * 2):
                if sim_board.is_game_over():
                    break
                
                moves = self.sample_plausible_moves(sim_board, n_samples=1)
                if not moves:
                    break
                
                sim_board.push(moves[0])
            
            try:
                eval_result = self.analyzer.evaluate_position(sim_board)
                if sim_board.turn != board.turn:
                    evaluations.append(-eval_result.score)
                else:
                    evaluations.append(eval_result.score)
            except:
                continue
        
        return evaluations
    
    def calculate_volatility(self, evaluations: List[float]) -> float:
        """Calculate volatility (standard deviation)"""
        if len(evaluations) < 2:
            return 0.0
        return float(np.std(evaluations))
    
    def calculate_var(self, evaluations: List[float], percentile: float = 5) -> float:
        """Calculate Value at Risk (VaR)"""
        if not evaluations:
            return 0.0
        return float(np.percentile(evaluations, percentile))
    
    def calculate_downside_risk(self, evaluations: List[float], threshold: float = -100) -> float:
        """Calculate probability of evaluation dropping below threshold"""
        if not evaluations:
            return 0.0
        below_threshold = sum(1 for e in evaluations if e < threshold)
        return below_threshold / len(evaluations)
    
    def calculate_tactical_density(self, board: chess.Board) -> float:
        """Estimate tactical density of position"""
        legal_moves = list(board.legal_moves)
        
        checks = sum(1 for move in legal_moves if board.gives_check(move))
        captures = sum(1 for move in legal_moves if board.is_capture(move))
        
        # Hanging pieces
        hanging_count = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                attackers = len(board.attackers(not piece.color, square))
                defenders = len(board.attackers(piece.color, square))
                if attackers > defenders and attackers > 0:
                    hanging_count += 1
        
        tactical_density = (checks * 5 + captures * 2 + hanging_count * 3)
        return min(tactical_density, 100)
    
    def calculate_move_edge(self, board: chess.Board) -> float:
        """Calculate evaluation gap between best and second-best move"""
        top_moves = self.analyzer.get_top_moves(board, num_moves=3)
        
        if len(top_moves) < 2:
            return 0.0
        
        best_score = top_moves[0]["score"]
        second_score = top_moves[1]["score"]
        
        return abs(best_score - second_score)
    
    def calculate_risk_metrics(self, board: chess.Board) -> RiskMetrics:
        """Calculate comprehensive risk metrics for a position"""
        # Run Monte Carlo simulation
        evaluations = self.monte_carlo_simulation(board, depth_horizon=2)
        
        # Calculate base evaluation
        current_eval = self.analyzer.evaluate_position(board)
        
        # Calculate all metrics
        volatility = self.calculate_volatility(evaluations)
        expected_value = float(np.mean(evaluations)) if evaluations else current_eval.score
        downside_risk = self.calculate_downside_risk(evaluations, threshold=-100)
        var_95 = self.calculate_var(evaluations, percentile=5)
        
        # Get position features for complexity
        features = self.feature_extractor.extract_all_features(board)
        complexity_risk = features["complexity"]
        
        # Tactical metrics
        tactical_density = self.calculate_tactical_density(board)
        best_move_edge = self.calculate_move_edge(board)
        
        return RiskMetrics(
            volatility=volatility,
            expected_value=expected_value,
            downside_risk=downside_risk,
            var_95=var_95,
            complexity_risk=complexity_risk,
            tactical_density=tactical_density,
            best_move_edge=best_move_edge
        )
    
    def risk_score(self, metrics: RiskMetrics) -> float:
        """Calculate overall risk score (0-100)"""
        vol_component = min(metrics.volatility / 10, 100) * 0.3
        downside_component = metrics.downside_risk * 100 * 0.25
        complexity_component = metrics.complexity_risk * 0.2
        tactical_component = metrics.tactical_density * 0.15
        edge_reduction = min(metrics.best_move_edge / 100, 1) * 0.1 * 100
        
        risk = vol_component + downside_component + complexity_component + tactical_component - edge_reduction
        
        return max(0, min(risk, 100))
    
    def close(self):
        """Clean up resources"""
        self.analyzer.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    board = chess.Board()
    
    print("Testing risk calculator...")
    print("This will take about 1 minute...\n")
    
    with RiskCalculator(n_simulations=10, depth=10) as calc:
        print("1. Starting position:")
        metrics = calc.calculate_risk_metrics(board)
        risk = calc.risk_score(metrics)
        print(f"   Risk Score: {risk:.1f}/100")
        print(f"   Volatility: {metrics.volatility:.1f}")
        print(f"   Expected Value: {metrics.expected_value:.1f}")
        print(f"   Tactical Density: {metrics.tactical_density:.1f}")
        
        # Tactical position
        board.set_fen("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
        print("\n2. Tactical position (Italian Game):")
        metrics = calc.calculate_risk_metrics(board)
        risk = calc.risk_score(metrics)
        print(f"   Risk Score: {risk:.1f}/100")
        print(f"   Volatility: {metrics.volatility:.1f}")
        print(f"   Tactical Density: {metrics.tactical_density:.1f}")
    
    print("\n✅ Risk calculator working!")