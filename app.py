"""
Chess Risk Analyzer - Interactive Board with Drag & Drop
"""
import streamlit as st
import chess
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from src.game_analyzer import GameAnalyzer
from src.risk_calculator import RiskCalculator
from src.chess_api import get_famous_games

# Try to import interactive chess board
try:
    from streamlit_chess_board import st_chess_board
    HAS_INTERACTIVE_BOARD = True
except ImportError:
    HAS_INTERACTIVE_BOARD = False
    import chess.svg

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
if 'board_key' not in st.session_state:
    st.session_state.board_key = 0

# Helper functions
def load_my_games():
    """Load embedded games"""
    try:
        games_file = Path(__file__).parent / "data" / "my_chess_games.json"
        if games_file.exists():
            with open(games_file) as f:
                return json.load(f)
    except:
        pass
    
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
        }
    ]

def render_interactive_board():
    """Render interactive drag-and-drop board"""
    if HAS_INTERACTIVE_BOARD:
        # Use interactive board with drag & drop
        board_dict = st_chess_board(
            board_fen=st.session_state.board.fen(),
            dark_square_color="#769656",
            light_square_color="#eeeed2",
            key=f"board_{st.session_state.board_key}"
        )
        
        # Handle move from interactive board
        if board_dict and 'move' in board_dict:
            move_str = board_dict['move']
            try:
                move = chess.Move.from_uci(move_str)
                if move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.session_state.move_history.append(st.session_state.board.san(move))
                    st.session_state.board_key += 1
                    st.rerun()
            except:
                pass
    else:
        # Fallback to SVG board
        svg = chess.svg.board(st.session_state.board, size=500)
        st.markdown(f'<div class="chess-board">{svg}</div>', unsafe_allow_html=True)
        st.info("💡 **Tip:** Install `streamlit-chess-board` for drag-and-drop functionality")

# Title
st.markdown('<h1 class="main-title">♟️ Chess Risk Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Quantitative Chess Analysis • Built by Soham Gugale @ Duke</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    mode = st.radio(
        "**Analysis Mode**",
        ["🎮 Interactive Board", "📚 Sample Games", "👤 My Games", "📁 Upload PGN"],
        help="Choose analysis mode"
    )
    
    st.divider()
    
    if mode != "🎮 Interactive Board":
        max_moves = st.slider(
            "**Moves to Analyze**",
            min_value=10,
            max_value=50,
            value=30,
            step=5,
            help="Analyze up to 50 moves (longer games take more time)"
        )
        
        st.info(f"⏱️ **Est. time:** ~{max_moves * 2} seconds")
    
    st.divider()
    
    with st.expander("📖 Metrics Guide"):
        st.markdown("""
        **Risk Score (0-100)**
        - **0-30**: Safe
        - **30-60**: Complications
        - **60-100**: Very risky
        
        **Evaluation**
        - **+100**: White up 1 pawn
        - **0**: Equal
        - **-100**: Black up 1 pawn
        
        **Move Quality**
        - 🟢 **Excellent**: Best move
        - 🟡 **Good**: Near best
        - 🟠 **Inaccuracy**: −50 to −150cp
        - 🔴 **Mistake**: −150 to −300cp
        - 💥 **Blunder**: −300cp+
        """)
    
    st.divider()
    st.info("""
    **Quick Start:**
    1. Choose mode
    2. Select game
    3. Analyze
    
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

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Bd2 Bxd2+ 8. Nbxd2 d5 9. exd5 Nxd5 10. Qb3 Nce7 11. O-O O-O 12. Rfe1 c6 13. a3 Nf4 14. Ne5 Ned5 15. Rac1 *""",
        
        "👑 Kasparov's Immortal": famous["Kasparov's Immortal"],
        "🎨 Fischer's Century Game": famous["Fischer's Game of the Century"],
        "⚔️ The Immortal Game": famous["The Immortal Game"]
    }

# Main content
pgn_input = None

if mode == "🎮 Interactive Board":
    st.markdown("## 🎮 Interactive Chess Board")
    
    if not HAS_INTERACTIVE_BOARD:
        st.warning("""
        ⚠️ **Interactive drag-and-drop not available**
        
        The `streamlit-chess-board` package isn't installed on Streamlit Cloud.
        You can still make moves manually using the text input below.
        """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Board Position")
        
        # Show if drag-and-drop is enabled
        if HAS_INTERACTIVE_BOARD:
            st.success("✅ **Drag & Drop Enabled** - Click and drag pieces to move!")
        
        render_interactive_board()
        
        # Controls
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
        
        with ctrl_col1:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.board = chess.Board()
                st.session_state.move_history = []
                st.session_state.board_key += 1
                st.rerun()
        
        with ctrl_col2:
            if st.button("↩️ Undo", use_container_width=True):
                if st.session_state.board.move_stack:
                    st.session_state.board.pop()
                    if st.session_state.move_history:
                        st.session_state.move_history.pop()
                    st.session_state.board_key += 1
                    st.rerun()
        
        with ctrl_col3:
            if st.button("🔄 Flip", use_container_width=True):
                st.session_state.board_key += 1
                st.rerun()
        
        with ctrl_col4:
            if st.button("📋 FEN", use_container_width=True):
                st.code(st.session_state.board.fen(), language="text")
        
        # Load position
        st.markdown("### 📥 Load Position")
        fen_input = st.text_input("FEN:", value=st.session_state.board.fen(), key="fen_input")
        
        if st.button("Load FEN"):
            try:
                st.session_state.board = chess.Board(fen_input)
                st.session_state.move_history = []
                st.session_state.board_key += 1
                st.success("✅ Position loaded!")
                st.rerun()
            except:
                st.error("❌ Invalid FEN!")
    
    with col2:
        st.markdown("### 🎯 Analysis")
        
        if st.button("🔍 Analyze Position", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    calc = RiskCalculator(depth=12)
                    metrics = calc.calculate_risk_metrics(st.session_state.board)
                    calc.close()
                    
                    st.markdown(f"""
                    <div class="metric-card">
                    <h4>📊 Position</h4>
                    <p><strong>Eval:</strong> {metrics.position_eval:.0f} cp</p>
                    <p><strong>Risk:</strong> {metrics.risk_score:.1f}/100</p>
                    <p><strong>Complexity:</strong> {metrics.complexity:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🎯 Top 3 Moves")
                    for i, move in enumerate(metrics.top_moves[:3], 1):
                        st.markdown(f"**{i}. {move['move']}** → {move['score']:.0f} cp")
                
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Manual move input
        if not HAS_INTERACTIVE_BOARD:
            st.markdown("### ✍️ Manual Move")
            move_input = st.text_input("Move (e.g., e4, Nf3):", key="move_input")
            
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
                        st.session_state.board_key += 1
                        st.success(f"✅ {move_input}")
                        st.rerun()
                    else:
                        st.error("❌ Illegal move!")
                except:
                    st.error("Invalid format!")
        
        # Move history
        if st.session_state.move_history:
            st.markdown("### 📜 Move History")
            history_text = " ".join([
                f"{(i//2)+1}.{move}" if i % 2 == 0 else move 
                for i, move in enumerate(st.session_state.move_history)
            ])
            st.text_area("Moves:", value=history_text, height=150, key="history")

elif mode == "📚 Sample Games":
    st.markdown("## 📚 Sample Games")
    
    samples = get_sample_games()
    selected = st.selectbox("Choose a game:", list(samples.keys()))
    pgn_input = samples[selected]
    
    with st.expander("📄 View PGN"):
        st.code(pgn_input, language="text")

elif mode == "👤 My Games":
    st.markdown("## 👤 Soham's Games")
    
    st.info("**Note:** Embedded games (Chess.com API blocked on Streamlit Cloud)")
    
    my_games = load_my_games()
    
    if not my_games:
        st.warning("No games found. Use 'Upload PGN' to add games!")
    else:
        st.success(f"✅ {len(my_games)} games loaded")
        
        game_labels = []
        for i, g in enumerate(my_games, 1):
            label = f"{i}. {g['white']} ({g['white_elo']}) vs {g['black']} ({g['black_elo']}) • {g['result']}"
            game_labels.append(label)
        
        selected_idx = st.selectbox("Select game:", range(len(game_labels)), format_func=lambda x: game_labels[x])
        
        pgn_input = my_games[selected_idx]['pgn']
        
        st.markdown(f"""
        **Details:**
        - **White:** {my_games[selected_idx]['white']} ({my_games[selected_idx]['white_elo']})
        - **Black:** {my_games[selected_idx]['black']} ({my_games[selected_idx]['black_elo']})
        - **Result:** {my_games[selected_idx]['result']}
        - **Date:** {my_games[selected_idx]['date']}
        """)
        
        with st.expander("📄 View PGN"):
            st.code(pgn_input, language="text")

else:  # Upload
    st.markdown("## 📁 Upload Your Game")
    
    upload_type = st.radio("Method:", ["Paste PGN", "Upload File"])
    
    if upload_type == "Paste PGN":
        pgn_input = st.text_area("Paste PGN here:", height=200, placeholder="[Event \"My Game\"]\n\n1. e4 e5...")
    else:
        file = st.file_uploader("Choose PGN file", type=['pgn', 'txt'])
        if file:
            pgn_input = file.read().decode('utf-8')
            st.success("✅ File uploaded!")

# Analyze button
if mode != "🎮 Interactive Board" and pgn_input:
    if st.button("🚀 Analyze Game", type="primary", use_container_width=True):
        with st.spinner(f"Analyzing up to {max_moves} moves... (est. {max_moves * 2} seconds)"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("Initializing analyzer...")
                progress_bar.progress(10)
                
                analyzer = GameAnalyzer(depth=10)
                
                status_text.text(f"Analyzing moves (max {max_moves})...")
                progress_bar.progress(30)
                
                analyses, report = analyzer.analyze_pgn_string(pgn_input, max_moves=max_moves)
                analyzer.close()
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
                if analyses:
                    st.success(f"✅ Analyzed {len(analyses)} moves!")
                    st.balloons()
                    st.session_state['analyses'] = analyses
                    st.session_state['report'] = report
                else:
                    st.error("No moves found in PGN")
            
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

# Display results
if 'analyses' in st.session_state and mode != "🎮 Interactive Board":
    analyses = st.session_state['analyses']
    report = st.session_state['report']
    
    st.divider()
    st.markdown("## 📊 Analysis Results")
    
    # Summary
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
    
    # Move-by-move with board preview
    st.markdown("### 📝 Move-by-Move Analysis")
    
    for a in analyses:
        emoji = {"excellent": "🟢", "good": "🟡", "inaccuracy": "🟠", "mistake": "🔴", "blunder": "💥"}
        player = "⚪" if a.white_to_move else "⚫"
        
        with st.expander(f"{emoji.get(a.classification, '⚪')} {a.move_number}. {a.move} ({player}) • {a.classification.upper()}"):
            mcol1, mcol2 = st.columns([1, 2])
            
            with mcol1:
                # Show board position after move
                board_after = chess.Board(a.fen_after)
                svg = chess.svg.board(board_after, size=250)
                st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
            
            with mcol2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Eval", f"{a.eval_score:.0f} cp")
                with col2:
                    st.metric("Risk", f"{a.risk_score:.1f}/100")
                with col3:
                    if not a.is_best_move:
                        st.markdown(f"**Better:**")
                        st.code(a.best_alternative)
                    else:
                        st.success("✓ Best move!")
    
    # Stats
    st.divider()
    st.markdown("### 📈 Player Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚪ White")
        w = report['white']
        st.write(f"🟢 Excellent: {w.get('excellent', 0)}")
        st.write(f"🟡 Good: {w.get('good', 0)}")
        st.write(f"🟠 Inaccuracies: {w.get('inaccuracies', 0)}")
        st.write(f"🔴 Mistakes: {w.get('mistakes', 0)}")
        st.write(f"💥 Blunders: {w.get('blunders', 0)}")
        st.metric("Avg Risk", f"{w.get('avg_risk', 0):.1f}/100")
    
    with col2:
        st.markdown("#### ⚫ Black")
        b = report['black']
        st.write(f"🟢 Excellent: {b.get('excellent', 0)}")
        st.write(f"🟡 Good: {b.get('good', 0)}")
        st.write(f"🟠 Inaccuracies: {b.get('inaccuracies', 0)}")
        st.write(f"🔴 Mistakes: {b.get('mistakes', 0)}")
        st.write(f"💥 Blunders: {b.get('blunders', 0)}")
        st.metric("Avg Risk", f"{b.get('avg_risk', 0):.1f}/100")

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
