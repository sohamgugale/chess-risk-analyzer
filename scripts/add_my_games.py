"""
Extract your recent games and embed them in the app
"""
import chess.pgn
import json
from pathlib import Path


def extract_games_from_pgn(pgn_file: str, max_games: int = 20):
    """Extract games from PGN file"""
    games_data = []
    
    with open(pgn_file) as f:
        game_count = 0
        while game_count < max_games:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            
            # Extract metadata
            headers = game.headers
            
            # Get PGN string
            exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
            pgn_string = game.accept(exporter)
            
            game_info = {
                'white': headers.get('White', 'Unknown'),
                'black': headers.get('Black', 'Unknown'),
                'white_elo': headers.get('WhiteElo', '?'),
                'black_elo': headers.get('BlackElo', '?'),
                'result': headers.get('Result', '*'),
                'date': headers.get('Date', '?'),
                'event': headers.get('Event', '?'),
                'pgn': pgn_string
            }
            
            games_data.append(game_info)
            game_count += 1
    
    return games_data


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python add_my_games.py <path_to_pgn_file>")
        print("Example: python scripts/add_my_games.py ~/Downloads/my_games.pgn")
        sys.exit(1)
    
    pgn_file = sys.argv[1]
    
    print(f"Reading games from: {pgn_file}")
    games = extract_games_from_pgn(pgn_file, max_games=20)
    
    print(f"\nExtracted {len(games)} games")
    
    # Save to JSON
    output_file = Path(__file__).parent.parent / "data" / "my_chess_games.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(games, f, indent=2)
    
    print(f"Saved to: {output_file}")
    
    # Print sample
    if games:
        print(f"\nSample game:")
        print(f"  {games[0]['white']} vs {games[0]['black']}")
        print(f"  Result: {games[0]['result']}")
        print(f"  Date: {games[0]['date']}")
