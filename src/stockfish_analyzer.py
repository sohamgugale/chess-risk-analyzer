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
    # For Streamlit Cloud
    cloud_paths = [
        "/usr/games/stockfish",
        "/usr/bin/stockfish", 
        "/app/.apt/usr/games/stockfish",
        "/home/appuser/venv/bin/stockfish"
    ]
    
    for path in cloud_paths:
        if os.path.exists(path):
            print(f"Found Stockfish at: {path}")
            return path
    
    # For local development
    local_paths = [
        "/opt/homebrew/bin/stockfish",
        "/usr/local/bin/stockfish",
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            return path
    
    # Try PATH
    stockfish_in_path = shutil.which("stockfish")
    if stockfish_in_path:
        return stockfish_in_path
    
    raise FileNotFoundError(
        "Stockfish not found! Ensure 'stockfish' is in packages.txt and app is restarted."
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
        if stockfish_path is None:
            stockfish_path = get_stockfish_path()
        
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.depth = depth
        self.threads = threads
        self.engine.configure({"Threads": threads})
    
    def evaluate_position(self, board: chess.Board) -> PositionEvaluation:
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
        self.engine.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
