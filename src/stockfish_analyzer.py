"""
Stockfish integration for position evaluation - FIXED FOR STREAMLIT CLOUD
"""
import chess
import chess.engine
from typing import Dict, Optional, List
from dataclasses import dataclass
import os
import shutil
import sys


def get_stockfish_path():
    """Get Stockfish path - works on Streamlit Cloud and local"""
    
    # STREAMLIT CLOUD PATHS - Check these first
    streamlit_paths = [
        "/usr/games/stockfish",
        "/usr/bin/stockfish",
        "/app/.apt/usr/games/stockfish",
        "/home/appuser/.apt/usr/games/stockfish",
    ]
    
    for path in streamlit_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            print(f"✓ Found Stockfish at: {path}", file=sys.stderr)
            return path
    
    # LOCAL PATHS (Mac/Linux)
    local_paths = [
        "/opt/homebrew/bin/stockfish",
        "/usr/local/bin/stockfish",
        "/opt/local/bin/stockfish",
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            return path
    
    # Try finding in system PATH
    which_result = shutil.which("stockfish")
    if which_result:
        return which_result
    
    # If we're here, Stockfish wasn't found
    print("ERROR: Stockfish not found in any location!", file=sys.stderr)
    print("Searched paths:", file=sys.stderr)
    for p in streamlit_paths + local_paths:
        print(f"  {p}: {'EXISTS' if os.path.exists(p) else 'NOT FOUND'}", file=sys.stderr)
    
    raise FileNotFoundError(
        "Stockfish not found! "
        "On Streamlit Cloud: Add 'stockfish' to packages.txt. "
        "Locally: brew install stockfish (Mac) or apt-get install stockfish (Linux)"
    )


@dataclass
class PositionEvaluation:
    """Container for position evaluation data"""
    score: float
    mate_in: Optional[int]
    best_move: str
    depth: int


class StockfishAnalyzer:
    """Wrapper for Stockfish engine analysis"""
    
    def __init__(self, stockfish_path: str = None, depth: int = 15, threads: int = 2):
        """Initialize Stockfish engine"""
        if stockfish_path is None:
            stockfish_path = get_stockfish_path()
        
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = depth
        self.threads = threads
        self.engine.configure({"Threads": threads})
    
    def evaluate_position(self, board: chess.Board) -> PositionEvaluation:
        """Evaluate a chess position"""
        info = self.engine.analyse(board, chess.engine.Limit(depth=self.depth))
        
        score_value = info["score"].relative.score()
        mate_score = info["score"].relative.mate()
        best_move = info.get("pv", [None])[0]
        
        if mate_score is not None:
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
        """Analyze quality of a specific move"""
        eval_before = self.evaluate_position(board)
        board.push(move)
        eval_after = self.evaluate_position(board)
        board.pop()
        
        score_change = eval_before.score - (-eval_after.score)
        
        return {
            "eval_before": eval_before.score,
            "eval_after": -eval_after.score,
            "score_change": score_change,
            "is_best": str(move) == eval_before.best_move
        }
    
    def get_top_moves(self, board: chess.Board, num_moves: int = 3) -> List[Dict]:
        """Get top N moves with evaluations"""
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
                "pv": [str(m) for m in pv_info["pv"][:5]]
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
    print("Testing Stockfish integration...")
    try:
        path = get_stockfish_path()
        print(f"✓ Stockfish found at: {path}")
        
        board = chess.Board()
        with StockfishAnalyzer(depth=10) as analyzer:
            eval_result = analyzer.evaluate_position(board)
            print(f"✓ Starting position eval: {eval_result.score} cp")
            print(f"✓ Best move: {eval_result.best_move}")
        print("✓ All tests passed!")
    except Exception as e:
        print(f"✗ Error: {e}")
