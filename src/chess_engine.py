"""
Core chess engine wrapper for position analysis
"""
import chess
import chess.pgn
from typing import List, Dict, Optional
import io


class ChessEngine:
    """Wrapper for chess operations and position analysis"""
    
    def __init__(self):
        self.board = chess.Board()
    
    def load_pgn(self, pgn_string: str) -> chess.pgn.Game:
        """Load a game from PGN string"""
        pgn = io.StringIO(pgn_string)
        game = chess.pgn.read_game(pgn)
        return game
    
    def load_fen(self, fen: str):
        """Load position from FEN string"""
        self.board = chess.Board(fen)
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves in current position"""
        return list(self.board.legal_moves)
    
    def make_move(self, move: chess.Move):
        """Make a move on the board"""
        self.board.push(move)
    
    def undo_move(self):
        """Undo last move"""
        self.board.pop()
    
    def reset(self):
        """Reset board to starting position"""
        self.board = chess.Board()
    
    def get_fen(self) -> str:
        """Get current position as FEN"""
        return self.board.fen()
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.board.is_game_over()
    
    def get_result(self) -> Optional[str]:
        """Get game result if game is over"""
        if self.board.is_checkmate():
            return "1-0" if self.board.turn == chess.BLACK else "0-1"
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            return "1/2-1/2"
        return None


if __name__ == "__main__":
    # Test the engine
    engine = ChessEngine()
    print("Starting position FEN:", engine.get_fen())
    print("Legal moves:", len(engine.get_legal_moves()))
    
    # Make a move
    move = chess.Move.from_uci("e2e4")
    engine.make_move(move)
    print("After e4, legal moves:", len(engine.get_legal_moves()))
