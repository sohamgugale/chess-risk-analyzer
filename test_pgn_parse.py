from src.game_parser import GameParser
import chess.pgn

sample_pgn = """[Event "Test"]
[Site "?"]
[Date "2024.01.01"]
[White "White"]
[Black "Black"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0
"""

print("Testing PGN parsing...")
print("PGN:")
print(sample_pgn)
print()

parser = GameParser()
game = parser.parse_pgn_string(sample_pgn)

if game is None:
    print("❌ Failed to parse!")
else:
    print("✓ Parsed successfully!")
    
    moves = list(game.mainline_moves())
    print(f"✓ Found {len(moves)} moves")
    
    if moves:
        print("✓ Moves:", [str(m) for m in moves])
        
        # Get positions
        positions = parser.extract_positions(game, "test_1")
        print(f"✓ Extracted {len(positions)} positions")
        
        for pos in positions[:3]:
            print(f"  Move {pos.move_number}: {pos.move_played}")
    else:
        print("❌ No moves found!")
