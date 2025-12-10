"""
Stockfish integration for position evaluation
"""
import chess
import chess.engine
from typing import Dict, Optional, List
from dataclasses import dataclass
import os
import shutil


def get_stockfish_path():
    """Get Stockfish path for local or cloud environment"""
    # Try common local paths first
    local_paths = [
        "/opt/homebrew/bin/stockfish",
        "/usr/local/bin/stockfish",
        "/usr/bin/stockfish",
        "/usr/games/stockfish"
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            return path
    
    # Try to find in PATH
    if shutil.which("stockfish"):
        return shutil.which("stockfish")
    
    raise FileNotFoundError(
        "Stockfish not found! Install with: brew install stockfish (Mac) or apt-get install stockfish (Linux)"
    )


@dataclass
class PositionEvaluation:
    """Container for position evaluation data"""
    score: float  # In centipawns (100 = 1 pawn advantage)
    mate_in: Optional[int]  # Moves to mate if applicable
    best_move: str
    depth: int


class StockfishAnalyzer:
    """Wrapper for Stockfish engine analysis"""
    
    def __init__(self, stockfish_path: str = None, depth: int = 15, threads: int = 4):
        """
        Initialize Stockfish engine
        
        Args:
            stockfish_path: Path to Stockfish binary (auto-detected if None)
            depth: Search depth (15 is good balance of speed/accuracy)
            threads: Number of CPU threads to use
        """
        if stockfish_path is None:
            stockfish_path = get_stockfish_path()
        
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = depth
        self.threads = threads
        
        # Configure engine
        self.engine.configure({"Threads": threads})
    
    def evaluate_position(self, board: chess.Board) -> PositionEvaluation:
        """
        Evaluate a chess position
        
        Returns:
            PositionEvaluation with score and best move
        """
        info = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
        
        score_value = info["score"].relative.score()
        mate_score = info["score"].relative.mate()
        best_move = info.get("pv", [None])[0]
        
        # Convert to float score (centipawns or mate score)
        if mate_score is not None:
            # Mate in N moves - use large score
            score = 10000 if mate_score > 0 else -10000
        else:
            score = score_value if score_value is not None else 0
        
        return PositionEvaluation(
            score=score,
            mate_in=mate_score,
            best_move=str(best_move) if best_move else "",
            depth=self.depth
        )
    
    def analyze_move(self, board: chess.Board, move: chess.Move) -> Dict[str, float]:
        """
        Analyze quality of a specific move
        
        Returns:
            Dictionary with move quality metrics
        """
        # Evaluate position before move
        eval_before = self.evaluate_position(board)
        
        # Make the move
        board.push(move)
        eval_after = self.evaluate_position(board)
        board.pop()
        
        # Calculate move quality
        # Flip sign because it's opponent's perspective after move
        score_change = eval_before.score - (-eval_after.score)
        
        return {
            "eval_before": eval_before.score,
            "eval_after": -eval_after.score,  # Flip for same perspective
            "score_change": score_change,  # Positive = good, negative = bad
            "is_best": str(move) == eval_before.best_move
        }
    
    def get_top_moves(self, board: chess.Board, num_moves: int = 3) -> List[Dict]:
        """
        Get top N moves with evaluations
        """
        try:
            info = self.engine.analyse(
                board, 
                chess.engine.Limit(depth=self.depth),
                multipv=num_moves
            )
        except:
            return []
        
        results = []
        for pv_info in info:
            score = pv_info["score"].relative.score()
            if score is None:
                score = 0
            
            results.append({
                "move": str(pv_info["pv"][0]),
                "score": score,
                "pv": [str(m) for m in pv_info["pv"][:5]]  # First 5 moves
            })
        
        return results
    
    def close(self):
        """Clean up engine"""
        self.engine.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Test Stockfish integration
    board = chess.Board()
    
    print(f"Stockfish path: {get_stockfish_path()}")
    
    with StockfishAnalyzer(depth=10) as analyzer:
        eval_result = analyzer.evaluate_position(board)
        print(f"Starting position eval: {eval_result.score} centipawns")
        print(f"Best move: {eval_result.best_move}")
        
        # Analyze e4
        move = chess.Move.from_uci("e2e4")
        move_quality = analyzer.analyze_move(board, move)
        print(f"\nMove e4 analysis: {move_quality}")
        
        # Get top 3 moves
        top_moves = analyzer.get_top_moves(board, 3)
        print("\nTop 3 moves:")
        for i, move_data in enumerate(top_moves, 1):
            print(f"{i}. {move_data['move']}: {move_data['score']} cp")
