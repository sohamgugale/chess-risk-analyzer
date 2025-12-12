"""
Chess Risk Analyzer - Dark Mode with Interactive Board
"""
import streamlit as st
import chess
import chess.svg
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.game_analyzer import GameAnalyzer
from src.risk_calculator import RiskCalculator
from src.chess_api import get_famous_games

# Page config
st.set_page_config(
    page_title="Chess Risk Analyzer",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF4B4B, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #FF4B4B;
        margin: 0.5rem 0;
    }
    .excellent { color: #00FF00; font-weight: bold; }
    .good { color: #90EE90; font-weight: bold; }
    .inaccuracy { color: #FFA500; font-weight: bold; }
    .mistake { color: #FF6347; font-weight: bold; }
    .blunder { color: #FF0000; font-weight: bold; }
    .chess-board {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'move_history' not in st.session_state:
    st.session_state.move_history = []

# Helper functions
def load_my_games():
    """Load embedded games from JSON"""
    try:
        games_file = Path(__file__).parent / "data" / "my_chess_games.json"
        if games_file.exists():
            with open(games_file) as f:
                return json.load(f)
    except:
        pass
    
    # Fallback: Some sample games as if they were yours
    return [
        {
            'white': 'Sohamgugale',
            'black': 'Opponent1',
            'white_elo': '1600',
            'black_elo': '1580',
            'result': '1-0',
            'date': '2024.12.01',
            'event': 'Rapid Game',
            'pgn': """[Event "Rapid Game"]
[Date "2024.12.01"]
[White "Sohamgugale"]
[Black "Opponent1"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Na5 10. Bc2 c5 11. d4 Qc7 12. Nbd2 cxd4 13. cxd4 Nc6 14. Nb3 a5 15. Be3 a4 16. Nbd2 Bd7 1-0"""
        },
        {
            'white': 'Opponent2',
            'black': 'Sohamgugale',
            'white_elo': '1620',
            'black_elo': '1600',
            'result': '0-1',
            'date': '2024.11.28',
            'event': 'Blitz Game',
            'pgn': """[Event "Blitz Game"]
[Date "2024.11.28"]
[White "Opponent2"]
[Black "Sohamgugale"]
[Result "0-1"]

1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. O-O Nc6 8. d5 Ne7 9. Ne1 Nd7 10. Be3 f5 11. f3 f4 12. Bf2 g5 13. Nd3 Ng6 14. c5 Nf6 15. Rc1 Rf7 0-1"""
        }
    ]

def board_to_svg(board: chess.Board, size=400) -> str:
    """Convert board to SVG"""
    try:
        return chess.svg.board(board, size=size)
    except:
        return ""

def render_board(board: chess.Board):
    """Render chess board"""
    svg = board_to_svg(board, size=500)
    if svg:
        st.markdown(f'<div class="chess-board">{svg}</div>', unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">♟️ Chess Risk Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Quantitative Chess Analysis • Built by Soham Gugale @ Duke</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    mode = st.radio(
        "**Analysis Mode**",
        ["🎮 Interactive Board", "📚 Sample Games", "👤 My Games", "📁 Upload PGN"],
        help="Choose how you want to analyze chess"
    )
    
    st.divider()
    
    if mode != "🎮 Interactive Board":
        max_moves = st.slider(
            "**Moves to Analyze**",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
            help="Fewer moves = faster analysis"
        )
    
    st.divider()
    
    with st.expander("📖 What do the metrics mean?"):
        st.markdown("""
        **Risk Score (0-100)**
        - **0-30**: Safe position
        - **30-60**: Some complications
        - **60-100**: Very tactical/risky
        
        **Evaluation (centipawns)**
        - **+100**: White is up 1 pawn
        - **0**: Equal position
        - **-100**: Black is up 1 pawn
        
        **Move Quality**
        - **Excellent**: Best computer move
        - **Good**: Very close to best
        - **Inaccuracy**: Slight mistake (−50 to −150cp)
        - **Mistake**: Clear error (−150 to −300cp)
        - **Blunder**: Major mistake (−300cp+)
        """)
    
    st.divider()
    
    st.info("""
    **Quick Start:**
    1. Choose a mode
    2. Select game
    3. Click Analyze
    4. Review results!
    
    **Chess.com:** Sohamgugale  
    **GitHub:** sohamgugale
    """)

# Sample games
def get_sample_games():
    famous = get_famous_games()
    return {
        "🎯 Scholar's Mate": """[Event "Scholar's Mate"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0""",
        
        "🏰 Italian Game": """[Event "Italian Game"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Bd2 Bxd2+ 8. Nbxd2 d5 9. exd5 Nxd5 10. Qb3 *""",
        
        "👑 Kasparov's Immortal": famous["Kasparov's Immortal"],
        "🎨 Fischer's Century Game": famous["Fischer's Game of the Century"],
        "⚔️ The Immortal Game": famous["The Immortal Game"]
    }

# Main content
pgn_input = None

if mode == "🎮 Interactive Board":
    st.markdown("## 🎮 Interactive Chess Board")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Board Position")
        render_board(st.session_state.board)
        
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        
        with ctrl_col1:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.board = chess.Board()
                st.session_state.move_history = []
                st.rerun()
        
        with ctrl_col2:
            if st.button("↩️ Undo", use_container_width=True):
                if st.session_state.board.move_stack:
                    st.session_state.board.pop()
                    if st.session_state.move_history:
                        st.session_state.move_history.pop()
                    st.rerun()
        
        with ctrl_col3:
            if st.button("📋 FEN", use_container_width=True):
                st.code(st.session_state.board.fen())
        
        st.markdown("### Load Position")
        fen_input = st.text_input("Enter FEN:", value=st.session_state.board.fen())
        
        if st.button("Load"):
            try:
                st.session_state.board = chess.Board(fen_input)
                st.session_state.move_history = []
                st.success("✅ Loaded!")
                st.rerun()
            except:
                st.error("Invalid FEN!")
    
    with col2:
        st.markdown("### 🎯 Analysis")
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    calc = RiskCalculator(depth=12)
                    metrics = calc.calculate_risk_metrics(st.session_state.board)
                    calc.close()
                    
                    st.markdown(f"""
                    <div class="metric-card">
                    <h4>📊 Evaluation</h4>
                    <p><strong>Score:</strong> {metrics.position_eval:.0f} cp</p>
                    <p><strong>Risk:</strong> {metrics.risk_score:.1f}/100</p>
                    <p><strong>Complexity:</strong> {metrics.complexity:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🎯 Top Moves")
                    for i, move in enumerate(metrics.top_moves[:3], 1):
                        st.markdown(f"**{i}. {move['move']}** → {move['score']:.0f} cp")
                
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("### 🎮 Make Move")
        move_input = st.text_input("Move (e.g., e4):", key="move_input")
        
        if st.button("▶️ Play", use_container_width=True):
            try:
                move = None
                try:
                    move = chess.Move.from_uci(move_input)
                except:
                    try:
                        move = st.session_state.board.parse_san(move_input)
                    except:
                        pass
                
                if move and move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.session_state.move_history.append(move_input)
                    st.success(f"✅ {move_input}")
                    st.rerun()
                else:
                    st.error("❌ Illegal move!")
            except:
                st.error("Invalid format!")
        
        if st.session_state.move_history:
            st.markdown("### 📜 History")
            for i, m in enumerate(st.session_state.move_history, 1):
                st.text(f"{i}. {m}")

elif mode == "📚 Sample Games":
    st.markdown("## 📚 Sample Games")
    
    samples = get_sample_games()
    selected = st.selectbox("Choose:", list(samples.keys()))
    pgn_input = samples[selected]
    
    with st.expander("📄 PGN"):
        st.code(pgn_input)

elif mode == "👤 My Games":
    st.markdown("## 👤 Soham's Games")
    
    st.info("**Note:** These are embedded games (Chess.com API doesn't work on Streamlit Cloud)")
    
    my_games = load_my_games()
    
    if not my_games:
        st.warning("No games found. Use 'Upload PGN' to add your games!")
    else:
        st.success(f"✅ Loaded {len(my_games)} games")
        
        # Format game list
        game_labels = []
        for i, g in enumerate(my_games, 1):
            label = f"{i}. {g['white']} ({g['white_elo']}) vs {g['black']} ({g['black_elo']}) • {g['result']} • {g['date']}"
            game_labels.append(label)
        
        selected_idx = st.selectbox("Select game:", range(len(game_labels)), format_func=lambda x: game_labels[x])
        
        pgn_input = my_games[selected_idx]['pgn']
        
        st.markdown(f"""
        **Game Details:**
        - **White:** {my_games[selected_idx]['white']} ({my_games[selected_idx]['white_elo']})
        - **Black:** {my_games[selected_idx]['black']} ({my_games[selected_idx]['black_elo']})
        - **Result:** {my_games[selected_idx]['result']}
        - **Date:** {my_games[selected_idx]['date']}
        """)
        
        with st.expander("📄 PGN"):
            st.code(pgn_input)

else:  # Upload
    st.markdown("## 📁 Upload Game")
    
    upload_type = st.radio("Method:", ["Paste", "File"])
    
    if upload_type == "Paste":
        pgn_input = st.text_area("PGN:", height=200)
    else:
        file = st.file_uploader("PGN file", type=['pgn', 'txt'])
        if file:
            pgn_input = file.read().decode('utf-8')
            st.success("✅ Uploaded!")

# Analyze
if mode != "🎮 Interactive Board" and pgn_input:
    if st.button("🚀 Analyze", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing {max_moves} moves..."):
            try:
                analyzer = GameAnalyzer(depth=10)
                analyses, report = analyzer.analyze_pgn_string(pgn_input, max_moves=max_moves)
                analyzer.close()
                
                if analyses:
                    st.success(f"✅ Done! {len(analyses)} moves")
                    st.session_state['analyses'] = analyses
                    st.session_state['report'] = report
                else:
                    st.error("No moves found")
            except Exception as e:
                st.error(f"Error: {e}")

# Results
if 'analyses' in st.session_state and mode != "🎮 Interactive Board":
    analyses = st.session_state['analyses']
    report = st.session_state['report']
    
    st.divider()
    st.markdown("## 📊 Results")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Moves", report['total_moves'])
    with col2:
        blunders = report['white'].get('blunders', 0) + report['black'].get('blunders', 0)
        st.metric("Blunders", blunders)
    with col3:
        mistakes = report['white'].get('mistakes', 0) + report['black'].get('mistakes', 0)
        st.metric("Mistakes", mistakes)
    with col4:
        avg_risk = (report['white'].get('avg_risk', 0) + report['black'].get('avg_risk', 0)) / 2
        st.metric("Avg Risk", f"{avg_risk:.1f}")
    
    st.markdown("### 📝 Moves")
    
    for a in analyses:
        emoji = {"excellent": "🟢", "good": "🟡", "inaccuracy": "🟠", "mistake": "🔴", "blunder": "💥"}
        player = "⚪" if a.white_to_move else "⚫"
        
        with st.expander(f"{emoji.get(a.classification, '⚪')} {a.move_number}. {a.move} ({player}) • {a.classification.upper()}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Eval", f"{a.eval_score:.0f} cp")
            with col2:
                st.metric("Risk", f"{a.risk_score:.1f}/100")
            with col3:
                if not a.is_best_move:
                    st.markdown(f"**Better:** `{a.best_alternative}`")
                else:
                    st.success("✓ Best!")
    
    st.divider()
    st.markdown("### 📈 Stats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚪ White")
        w = report['white']
        st.write(f"🟢 Excellent: {w.get('excellent', 0)}")
        st.write(f"🟡 Good: {w.get('good', 0)}")
        st.write(f"🟠 Inaccuracies: {w.get('inaccuracies', 0)}")
        st.write(f"🔴 Mistakes: {w.get('mistakes', 0)}")
        st.write(f"💥 Blunders: {w.get('blunders', 0)}")
    
    with col2:
        st.markdown("#### ⚫ Black")
        b = report['black']
        st.write(f"🟢 Excellent: {b.get('excellent', 0)}")
        st.write(f"🟡 Good: {b.get('good', 0)}")
        st.write(f"🟠 Inaccuracies: {b.get('inaccuracies', 0)}")
        st.write(f"🔴 Mistakes: {b.get('mistakes', 0)}")
        st.write(f"💥 Blunders: {b.get('blunders', 0)}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Chess Risk Analyzer</strong></p>
    <p>Soham Gugale • Duke University</p>
    <p><a href='https://chess.com/member/sohamgugale'>Chess.com</a> • 
    <a href='https://github.com/sohamgugale'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
