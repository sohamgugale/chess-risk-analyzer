"""
Fast game analyzer - simplified for speed
"""
import chess
import chess.pgn
from typing import List, Dict
import pandas as pd
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk_calculator import RiskCalculator
from src.game_parser import GameParser


@dataclass
class MoveAnalysis:
    """Simple move analysis"""
    move_number: int
    move: str
    white_to_move: bool
    eval_score: float
    risk_score: float
    is_best_move: bool
    best_alternative: str
    classification: str  # "excellent", "good", "inaccuracy", "mistake", "blunder"


class GameAnalyzer:
    """Fast, simplified game analyzer"""
    
    def __init__(self, stockfish_path: str = None, depth: int = 10):
        """Initialize with lower depth for speed"""
        self.risk_calc = RiskCalculator(stockfish_path=stockfish_path, depth=depth)
        self.parser = GameParser()
    
    def classify_move(self, eval_before: float, eval_after: float, is_best: bool) -> str:
        """Classify move quality"""
        eval_change = eval_after - eval_before
        
        if is_best:
            return "excellent"
        elif eval_change >= -50:
            return "good"
        elif eval_change >= -150:
            return "inaccuracy"
        elif eval_change >= -300:
            return "mistake"
        else:
            return "blunder"
    
    def analyze_move(self, board: chess.Board, move: chess.Move) -> MoveAnalysis:
        """Analyze a single move quickly"""
        move_san = board.san(move)
        white_to_move = board.turn == chess.WHITE
        
        # Get position metrics
        metrics_before = self.risk_calc.calculate_risk_metrics(board)
        
        # Make move and evaluate
        board.push(move)
        eval_after = -self.risk_calc.analyzer.evaluate_position(board).score
        board.pop()
        
        # Check if best move
        is_best = (move.uci() == metrics_before.best_move)
        best_alternative = metrics_before.top_moves[0]['move'] if metrics_before.top_moves else ""
        
        # Classify
        classification = self.classify_move(
            metrics_before.position_eval,
            eval_after,
            is_best
        )
        
        return MoveAnalysis(
            move_number=board.fullmove_number,
            move=move_san,
            white_to_move=white_to_move,
            eval_score=eval_after,
            risk_score=metrics_before.risk_score,
            is_best_move=is_best,
            best_alternative=best_alternative,
            classification=classification
        )
    
    def analyze_game(self, game: chess.pgn.Game, max_moves: int = 15) -> List[MoveAnalysis]:
        """Analyze game - LIMITED to first N moves for speed"""
        if game is None:
            return []
        
        analyses = []
        board = game.board()
        moves = list(game.mainline_moves())[:max_moves]  # LIMIT MOVES
        
        print(f"Analyzing first {len(moves)} moves...")
        
        for i, move in enumerate(moves, 1):
            try:
                print(f"  Move {i}/{len(moves)}...", end='\r')
                analysis = self.analyze_move(board, move)
                analyses.append(analysis)
                board.push(move)
            except Exception as e:
                print(f"Error on move {i}: {e}")
                continue
        
        print(f"\nDone! Analyzed {len(analyses)} moves")
        return analyses
    
    def generate_report(self, analyses: List[MoveAnalysis]) -> Dict:
        """Generate simple report"""
        if not analyses:
            return {}
        
        white = [a for a in analyses if a.white_to_move]
        black = [a for a in analyses if not a.white_to_move]
        
        def stats(moves):
            if not moves:
                return {}
            return {
                "total_moves": len(moves),
                "excellent": sum(1 for m in moves if m.classification == "excellent"),
                "good": sum(1 for m in moves if m.classification == "good"),
                "inaccuracies": sum(1 for m in moves if m.classification == "inaccuracy"),
                "mistakes": sum(1 for m in moves if m.classification == "mistake"),
                "blunders": sum(1 for m in moves if m.classification == "blunder"),
                "avg_risk": sum(m.risk_score for m in moves) / len(moves)
            }
        
        return {
            "total_moves": len(analyses),
            "white": stats(white),
            "black": stats(black)
        }
    
    def analyze_pgn_string(self, pgn_string: str, max_moves: int = 15) -> tuple:
        """Analyze from PGN string"""
        game = self.parser.parse_pgn_string(pgn_string)
        analyses = self.analyze_game(game, max_moves=max_moves)
        report = self.generate_report(analyses)
        return analyses, report
    
    def close(self):
        self.risk_calc.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
