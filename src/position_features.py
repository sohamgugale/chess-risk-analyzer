"""
Extract features from chess positions for risk analysis
"""
import chess
from typing import Dict
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class PositionFeatures:
    """Calculate position features for risk assessment"""
    
    # Piece values for material calculation
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0
    }
    
    def __init__(self):
        pass
    
    def calculate_material(self, board: chess.Board) -> Dict[str, int]:
        """
        Calculate material balance
        
        Returns:
            Dict with white_material, black_material, and balance
        """
        white_material = 0
        black_material = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.PIECE_VALUES.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
        
        return {
            "white_material": white_material,
            "black_material": black_material,
            "balance": white_material - black_material
        }
    
    def king_safety(self, board: chess.Board, color: chess.Color) -> Dict[str, float]:
        """
        Evaluate king safety
        
        Returns metrics like:
        - Number of attackers near king
        - Pawn shield quality
        """
        king_square = board.king(color)
        if king_square is None:
            return {"safety_score": 0, "attackers_near_king": 0, "pawn_shield": 0}
        
        # Count enemy pieces attacking squares around king
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        attackers_count = 0
        for file_offset in [-1, 0, 1]:
            for rank_offset in [-1, 0, 1]:
                new_file = king_file + file_offset
                new_rank = king_rank + rank_offset
                
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    square = chess.square(new_file, new_rank)
                    attackers_count += len(board.attackers(not color, square))
        
        # Check pawn shield
        pawn_shield = 0
        if color == chess.WHITE:
            shield_squares = [
                chess.square(king_file - 1, min(king_rank + 1, 7)) if king_file > 0 else None,
                chess.square(king_file, min(king_rank + 1, 7)),
                chess.square(king_file + 1, min(king_rank + 1, 7)) if king_file < 7 else None,
            ]
        else:
            shield_squares = [
                chess.square(king_file - 1, max(king_rank - 1, 0)) if king_file > 0 else None,
                chess.square(king_file, max(king_rank - 1, 0)),
                chess.square(king_file + 1, max(king_rank - 1, 0)) if king_file < 7 else None,
            ]
        
        for sq in shield_squares:
            if sq is not None:
                piece = board.piece_at(sq)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    pawn_shield += 1
        
        safety_score = pawn_shield * 10 - attackers_count * 5
        
        return {
            "safety_score": safety_score,
            "attackers_near_king": attackers_count,
            "pawn_shield": pawn_shield
        }
    
    def mobility(self, board: chess.Board) -> Dict[str, int]:
        """
        Calculate mobility (number of legal moves)
        """
        # Current player's mobility
        current_mobility = board.legal_moves.count()
        
        # Opponent's mobility (switch perspective temporarily)
        opponent_mobility = 0
        try:
            board.push(chess.Move.null())
            opponent_mobility = board.legal_moves.count()
            board.pop()
        except:
            # If null move is illegal (king in check), try another way
            opponent_mobility = 0
        
        return {
            "current_player_mobility": current_mobility,
            "opponent_mobility": opponent_mobility,
            "mobility_advantage": current_mobility - opponent_mobility
        }
    
    def center_control(self, board: chess.Board) -> Dict[str, int]:
        """
        Evaluate control of center squares (d4, d5, e4, e5)
        """
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        
        white_control = 0
        black_control = 0
        
        for square in center_squares:
            white_attackers = len(board.attackers(chess.WHITE, square))
            black_attackers = len(board.attackers(chess.BLACK, square))
            
            white_control += white_attackers
            black_control += black_attackers
            
            # Bonus for occupying center
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    white_control += 2
                else:
                    black_control += 2
        
        return {
            "white_center_control": white_control,
            "black_center_control": black_control,
            "center_control_advantage": white_control - black_control
        }
    
    def position_complexity(self, board: chess.Board) -> float:
        """
        Estimate position complexity
        Based on: material on board, number of pieces, mobility
        """
        material = self.calculate_material(board)
        total_material = material["white_material"] + material["black_material"]
        
        mobility = self.mobility(board)
        total_mobility = mobility["current_player_mobility"] + mobility["opponent_mobility"]
        
        # More pieces + more possible moves = more complex
        piece_count = len(board.piece_map())
        
        # Normalize complexity score to 0-100 range
        complexity = (piece_count * 2 + total_mobility / 10 + total_material / 100) / 3
        
        return min(complexity, 100)
    
    def extract_all_features(self, board: chess.Board) -> Dict:
        """
        Extract all features for a position
        
        Returns:
            Dict with all position features
        """
        features = {}
        
        # Material
        features.update(self.calculate_material(board))
        
        # King safety for both sides
        white_king_safety = self.king_safety(board, chess.WHITE)
        black_king_safety = self.king_safety(board, chess.BLACK)
        features["white_king_safety"] = white_king_safety["safety_score"]
        features["black_king_safety"] = black_king_safety["safety_score"]
        features["white_pawn_shield"] = white_king_safety["pawn_shield"]
        features["black_pawn_shield"] = black_king_safety["pawn_shield"]
        
        # Mobility
        features.update(self.mobility(board))
        
        # Center control
        features.update(self.center_control(board))
        
        # Complexity
        features["complexity"] = self.position_complexity(board)
        
        # Game phase
        total_material = features["white_material"] + features["black_material"]
        if board.fullmove_number < 10:
            features["game_phase"] = "opening"
        elif total_material > 2500:
            features["game_phase"] = "middlegame"
        else:
            features["game_phase"] = "endgame"
        
        return features


if __name__ == "__main__":
    # Test feature extraction
    board = chess.Board()
    extractor = PositionFeatures()
    
    print("Starting position features:")
    features = extractor.extract_all_features(board)
    for key, value in features.items():
        print(f"  {key}: {value}")
    
    # Test after some moves
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    
    print("\nAfter 1.e4 e5 2.Nf3:")
    features = extractor.extract_all_features(board)
    print(f"  Complexity: {features['complexity']:.1f}")
    print(f"  Center control advantage: {features['center_control_advantage']}")