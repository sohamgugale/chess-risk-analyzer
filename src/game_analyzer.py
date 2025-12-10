"""
Analyze complete games and generate risk profiles
"""
import chess
import chess.pgn
from typing import List, Dict
import pandas as pd
from dataclasses import dataclass, asdict
import sys
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.risk_calculator import RiskCalculator, RiskMetrics
from src.game_parser import GameParser


@dataclass
class MoveAnalysis:
    """Analysis for a single move in a game"""
    move_number: int
    move: str
    fen_before: str
    fen_after: str
    white_to_move: bool
    eval_before: float
    eval_after: float
    eval_change: float
    is_best_move: bool
    risk_score: float
    risk_metrics: Dict
    was_blunder: bool
    was_mistake: bool
    was_inaccuracy: bool


class GameAnalyzer:
    """Analyze complete chess games"""
    
    BLUNDER_THRESHOLD = 300
    MISTAKE_THRESHOLD = 150
    INACCURACY_THRESHOLD = 50
    
    def __init__(self, stockfish_path: str = None, n_simulations: int = 15, depth: int = 12):
        """Initialize game analyzer"""
        self.risk_calc = RiskCalculator(
            stockfish_path=stockfish_path,
            n_simulations=n_simulations,
            depth=depth
        )
        self.parser = GameParser()
    
    def analyze_move(self, board: chess.Board, move: chess.Move) -> MoveAnalysis:
        """Analyze a single move"""
        fen_before = board.fen()
        white_to_move = board.turn == chess.WHITE
        move_san = board.san(move)
        
        # Calculate risk before move
        risk_metrics_before = self.risk_calc.calculate_risk_metrics(board)
        risk_score = self.risk_calc.risk_score(risk_metrics_before)
        
        # Evaluate position before
        eval_before = self.risk_calc.analyzer.evaluate_position(board).score
        
        # Get best move
        best_move_data = self.risk_calc.analyzer.evaluate_position(board)
        best_move = best_move_data.best_move
        is_best = (move.uci() == best_move)
        
        # Make the move
        board.push(move)
        fen_after = board.fen()
        
        # Evaluate after
        eval_after = -self.risk_calc.analyzer.evaluate_position(board).score
        
        # Undo move
        board.pop()
        
        # Calculate eval change
        eval_change = eval_after - eval_before
        
        # Classify move quality
        was_blunder = eval_change < -self.BLUNDER_THRESHOLD
        was_mistake = -self.MISTAKE_THRESHOLD > eval_change >= -self.BLUNDER_THRESHOLD
        was_inaccuracy = -self.INACCURACY_THRESHOLD > eval_change >= -self.MISTAKE_THRESHOLD
        
        return MoveAnalysis(
            move_number=board.fullmove_number,
            move=move_san,
            fen_before=fen_before,
            fen_after=fen_after,
            white_to_move=white_to_move,
            eval_before=eval_before,
            eval_after=eval_after,
            eval_change=eval_change,
            is_best_move=is_best,
            risk_score=risk_score,
            risk_metrics=asdict(risk_metrics_before),
            was_blunder=was_blunder,
            was_mistake=was_mistake,
            was_inaccuracy=was_inaccuracy
        )
    
    def analyze_game(self, game: chess.pgn.Game, game_id: str = "", max_moves: int = None) -> List[MoveAnalysis]:
        """Analyze all moves in a game"""
        if game is None:
            return []
        
        analyses = []
        board = game.board()
        
        moves = list(game.mainline_moves())
        
        # Limit moves if specified
        if max_moves:
            moves = moves[:max_moves]
        
        print(f"Analyzing {len(moves)} moves...")
        
        for move in tqdm(moves, desc="Analyzing moves"):
            try:
                analysis = self.analyze_move(board, move)
                analyses.append(analysis)
                board.push(move)
            except Exception as e:
                print(f"Error analyzing move {move}: {e}")
                continue
        
        return analyses
    
    def generate_game_report(self, analyses: List[MoveAnalysis]) -> Dict:
        """Generate summary statistics for a game"""
        if not analyses:
            return {
                "total_moves": 0,
                "white": {},
                "black": {},
                "highest_risk_move": 0,
                "total_blunders": 0,
                "total_mistakes": 0
            }
        
        white_analyses = [a for a in analyses if a.white_to_move]
        black_analyses = [a for a in analyses if not a.white_to_move]
        
        def color_stats(color_analyses):
            if not color_analyses:
                return {
                    "avg_risk_score": 0,
                    "max_risk_score": 0,
                    "num_blunders": 0,
                    "num_mistakes": 0,
                    "num_inaccuracies": 0,
                    "num_best_moves": 0,
                    "avg_eval_loss": 0,
                    "accuracy": 0
                }
            
            return {
                "avg_risk_score": sum(a.risk_score for a in color_analyses) / len(color_analyses),
                "max_risk_score": max(a.risk_score for a in color_analyses),
                "num_blunders": sum(a.was_blunder for a in color_analyses),
                "num_mistakes": sum(a.was_mistake for a in color_analyses),
                "num_inaccuracies": sum(a.was_inaccuracy for a in color_analyses),
                "num_best_moves": sum(a.is_best_move for a in color_analyses),
                "avg_eval_loss": sum(min(0, a.eval_change) for a in color_analyses) / len(color_analyses),
                "accuracy": sum(a.is_best_move for a in color_analyses) / len(color_analyses) * 100
            }
        
        report = {
            "total_moves": len(analyses),
            "white": color_stats(white_analyses),
            "black": color_stats(black_analyses),
            "highest_risk_move": max(analyses, key=lambda a: a.risk_score).move_number if analyses else 0,
            "total_blunders": sum(a.was_blunder for a in analyses),
            "total_mistakes": sum(a.was_mistake for a in analyses),
        }
        
        return report
    
    def analyze_pgn_string(self, pgn_string: str, max_moves: int = None) -> tuple:
        """Analyze a game from PGN string"""
        game = self.parser.parse_pgn_string(pgn_string)
        if game is None:
            return [], {}
        
        analyses = self.analyze_game(game, max_moves=max_moves)
        report = self.generate_game_report(analyses)
        
        return analyses, report
    
    def export_to_dataframe(self, analyses: List[MoveAnalysis]) -> pd.DataFrame:
        """Export analyses to pandas DataFrame"""
        data = []
        for analysis in analyses:
            row = {
                "move_number": analysis.move_number,
                "move": analysis.move,
                "white_to_move": analysis.white_to_move,
                "eval_before": analysis.eval_before,
                "eval_after": analysis.eval_after,
                "eval_change": analysis.eval_change,
                "risk_score": analysis.risk_score,
                "is_best_move": analysis.is_best_move,
                "was_blunder": analysis.was_blunder,
                "was_mistake": analysis.was_mistake,
                "was_inaccuracy": analysis.was_inaccuracy,
            }
            row.update({f"risk_{k}": v for k, v in analysis.risk_metrics.items()})
            data.append(row)
        
        return pd.DataFrame(data)
    
    def close(self):
        """Clean up resources"""
        self.risk_calc.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    sample_pgn = """[Event "Test Game"]
[Site "Chess.com"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0"""
    
    print("Testing game analyzer...")
    print("="*50)
    
    with GameAnalyzer(n_simulations=5, depth=10) as analyzer:
        analyses, report = analyzer.analyze_pgn_string(sample_pgn)
        
        if not analyses:
            print("❌ No moves analyzed")
        else:
            print(f"✅ Analyzed {len(analyses)} moves\n")
            print(f"Total moves: {report['total_moves']}")
            print(f"Total blunders: {report['total_blunders']}")
            
            if report.get('white'):
                print(f"\nWhite accuracy: {report['white']['accuracy']:.1f}%")
            if report.get('black'):
                print(f"Black accuracy: {report['black']['accuracy']:.1f}%")