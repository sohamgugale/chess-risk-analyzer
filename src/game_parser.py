"""
Parse chess games and extract positions for analysis
"""
import chess
import chess.pgn
from typing import List, Dict, Generator
from dataclasses import dataclass
import io
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class GamePosition:
    """Single position from a game"""
    fen: str
    move_number: int
    move_played: str
    white_to_move: bool
    game_id: str


class GameParser:
    """Parse PGN games and extract positions"""
    
    def __init__(self):
        pass
    
    def parse_pgn_file(self, filepath: str) -> Generator[chess.pgn.Game, None, None]:
        """
        Parse PGN file and yield games one at a time
        
        Args:
            filepath: Path to PGN file
            
        Yields:
            chess.pgn.Game objects
        """
        try:
            with open(filepath) as pgn_file:
                while True:
                    game = chess.pgn.read_game(pgn_file)
                    if game is None:
                        break
                    yield game
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return
        except Exception as e:
            print(f"Error parsing PGN file: {e}")
            return
    
    def parse_pgn_string(self, pgn_string: str) -> chess.pgn.Game:
        """Parse single game from PGN string"""
        try:
            # Clean up the PGN string
            pgn_string = pgn_string.strip()
            pgn = io.StringIO(pgn_string)
            game = chess.pgn.read_game(pgn)
            return game
        except Exception as e:
            print(f"Error parsing PGN string: {e}")
            return None
    
    def extract_positions(self, game: chess.pgn.Game, 
                         game_id: str = "") -> List[GamePosition]:
        """
        Extract all positions from a game
        
        Args:
            game: chess.pgn.Game object
            game_id: Identifier for the game
            
        Returns:
            List of GamePosition objects
        """
        if game is None:
            return []
        
        positions = []
        board = game.board()
        
        try:
            for move_num, move in enumerate(game.mainline_moves(), 1):
                # Store position before move
                pos = GamePosition(
                    fen=board.fen(),
                    move_number=move_num,
                    move_played=board.san(move),
                    white_to_move=board.turn == chess.WHITE,
                    game_id=game_id
                )
                positions.append(pos)
                
                # Make the move
                board.push(move)
        except Exception as e:
            print(f"Error extracting positions: {e}")
        
        return positions
    
    def get_game_metadata(self, game: chess.pgn.Game) -> Dict[str, str]:
        """Extract metadata from game headers"""
        if game is None:
            return {}
        
        return {
            "event": game.headers.get("Event", "Unknown"),
            "white": game.headers.get("White", "Unknown"),
            "black": game.headers.get("Black", "Unknown"),
            "result": game.headers.get("Result", "*"),
            "date": game.headers.get("Date", "Unknown"),
            "white_elo": game.headers.get("WhiteElo", "?"),
            "black_elo": game.headers.get("BlackElo", "?"),
        }
    
    def filter_by_rating(self, game: chess.pgn.Game, 
                        min_rating: int = 1800) -> bool:
        """
        Check if game meets minimum rating threshold
        
        Args:
            game: chess.pgn.Game object
            min_rating: Minimum Elo rating
            
        Returns:
            True if both players meet threshold
        """
        if game is None:
            return False
        
        try:
            white_elo = int(game.headers.get("WhiteElo", "0"))
            black_elo = int(game.headers.get("BlackElo", "0"))
            return white_elo >= min_rating and black_elo >= min_rating
        except (ValueError, TypeError):
            return False


if __name__ == "__main__":
    # Test with a sample game
    sample_pgn = """[Event "Casual Game"]
[Site "?"]
[Date "2024.01.01"]
[Round "?"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0"""
    
    parser = GameParser()
    game = parser.parse_pgn_string(sample_pgn)
    
    if game:
        print("✓ Game metadata:")
        print(parser.get_game_metadata(game))
        
        print("\n✓ Positions:")
        positions = parser.extract_positions(game, "test_game_1")
        for pos in positions[:3]:  # Show first 3
            print(f"Move {pos.move_number}: {pos.move_played}")
    else:
        print("✗ Failed to parse game")