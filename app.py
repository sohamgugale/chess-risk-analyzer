"""
Chess Risk Analyzer - Interactive Board (Manual Input)
Analyze up to 50 moves per game
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

def render_board(board: chess.Board, size=500):
    """Render SVG chess board"""
    svg = chess.svg.board(board, size=size)
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
            help="More moves = longer analysis time"
        )
        
        st.info(f"⏱️ **Est. time:** ~{max_moves * 2} seconds")
    
    st.divider()
    
    with st.expander("📖 Metrics Guide"):
        st.markdown("""
        **Risk Score (0-100)**
        - **0-30**: Safe position
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
    3. Click Analyze
    
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
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Board Position")
        render_board(st.session_state.board)
        
        # Controls
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
        
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
            if st.button("🔄 Flip", use_container_width=True):
                # Flip by creating board from current FEN
                st.rerun()
        
        with ctrl_col4:
            if st.button("📋 Copy FEN", use_container_width=True):
                st.code(st.session_state.board.fen(), language="text")
        
        # Load position section
        st.markdown("### 📥 Load Position")
        fen_input = st.text_input("FEN String:", value=st.session_state.board.fen(), key="fen_input")
        
        if st.button("Load FEN"):
            try:
                st.session_state.board = chess.Board(fen_input)
                st.session_state.move_history = []
                st.success("✅ Position loaded!")
                st.rerun()
            except:
                st.error("❌ Invalid FEN string!")
    
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
                    <h4>📊 Position Analysis</h4>
                    <p><strong>Evaluation:</strong> {metrics.position_eval:.0f} cp</p>
                    <p><strong>Risk Score:</strong> {metrics.risk_score:.1f}/100</p>
                    <p><strong>Complexity:</strong> {metrics.complexity:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 🎯 Top 3 Moves")
                    for i, move in enumerate(metrics.top_moves[:3], 1):
                        st.markdown(f"**{i}. {move['move']}** → Eval: {move['score']:.0f} cp")
                
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Move input
        st.markdown("### ✍️ Make a Move")
        
        col_a, col_b = st.columns(2)
        with col_a:
            move_input = st.text_input("Move (e.g., e4, Nf3, e2e4):", key="move_input")
        with col_b:
            st.write("")  # Spacing
            st.write("")  # Spacing
            play_button = st.button("▶️ Play Move", use_container_width=True)
        
        if play_button and move_input:
            try:
                move = None
                # Try UCI format first (e2e4)
                try:
                    move = chess.Move.from_uci(move_input)
                except:
                    # Try SAN format (e4, Nf3)
                    try:
                        move = st.session_state.board.parse_san(move_input)
                    except:
                        pass
                
                if move and move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.session_state.move_history.append(st.session_state.board.san(move))
                    st.success(f"✅ Played: {move_input}")
                    st.rerun()
                else:
                    st.error("❌ Illegal move! Try format: e4 or e2e4")
            except Exception as e:
                st.error(f"Invalid move format: {e}")
        
        # Show legal moves
        if st.checkbox("Show Legal Moves"):
            legal_moves = list(st.session_state.board.legal_moves)
            legal_sans = [st.session_state.board.san(m) for m in legal_moves[:20]]  # Show first 20
            st.write(f"**Legal moves:** {', '.join(legal_sans)}")
            if len(legal_moves) > 20:
                st.caption(f"...and {len(legal_moves) - 20} more")
        
        # Move history
        if st.session_state.move_history:
            st.markdown("### 📜 Move History")
            # Format as proper chess notation
            history_text = ""
            for i, move in enumerate(st.session_state.move_history):
                if i % 2 == 0:
                    history_text += f"{(i//2)+1}. {move} "
                else:
                    history_text += f"{move}\n"
            
            st.text_area("Moves:", value=history_text.strip(), height=150, key="history_display")

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
        st.warning("No games found. Use 'Upload PGN' to add your games!")
    else:
        st.success(f"✅ {len(my_games)} games loaded")
        
        game_labels = []
        for i, g in enumerate(my_games, 1):
            label = f"{i}. {g['white']} ({g['white_elo']}) vs {g['black']} ({g['black_elo']}) • {g['result']}"
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
        
        with st.expander("📄 View PGN"):
            st.code(pgn_input, language="text")

else:  # Upload PGN
    st.markdown("## 📁 Upload Your Game")
    
    upload_type = st.radio("How to provide PGN:", ["Paste PGN", "Upload File"])
    
    if upload_type == "Paste PGN":
        pgn_input = st.text_area(
            "Paste PGN here:",
            height=200,
            placeholder="[Event \"My Game\"]\n[Site \"Chess.com\"]\n\n1. e4 e5 2. Nf3 Nc6..."
        )
    else:
        file = st.file_uploader("Choose PGN file", type=['pgn', 'txt'])
        if file:
            pgn_input = file.read().decode('utf-8')
            st.success("✅ File uploaded!")

# Analyze button (for non-interactive modes)
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
                    st.success(f"✅ Analysis complete! Analyzed {len(analyses)} moves")
                    st.balloons()
                    st.session_state['analyses'] = analyses
                    st.session_state['report'] = report
                else:
                    st.error("❌ No moves found in PGN")
            
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                with st.expander("🐛 Debug Info"):
                    st.code(traceback.format_exc())

# Display results
if 'analyses' in st.session_state and mode != "🎮 Interactive Board":
    analyses = st.session_state['analyses']
    report = st.session_state['report']
    
    st.divider()
    st.markdown("## 📊 Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Moves", report['total_moves'])
    with col2:
        blunders = report['white'].get('blunders', 0) + report['black'].get('blunders', 0)
        st.metric("💥 Blunders", blunders)
    with col3:
        mistakes = report['white'].get('mistakes', 0) + report['black'].get('mistakes', 0)
        st.metric("🔴 Mistakes", mistakes)
    with col4:
        avg_risk = (report['white'].get('avg_risk', 0) + report['black'].get('avg_risk', 0)) / 2
        st.metric("📊 Avg Risk", f"{avg_risk:.1f}")
    
    # Move-by-move analysis with board preview
    st.markdown("### 📝 Move-by-Move Analysis")
    
    for a in analyses:
        emoji = {"excellent": "🟢", "good": "🟡", "inaccuracy": "🟠", "mistake": "🔴", "blunder": "💥"}
        player = "⚪" if a.white_to_move else "⚫"
        
        with st.expander(
            f"{emoji.get(a.classification, '⚪')} Move {a.move_number}. {a.move} ({player}) • {a.classification.upper()}"
        ):
            mcol1, mcol2 = st.columns([1, 2])
            
            with mcol1:
                # Show board after move
                try:
                    board_after = chess.Board(a.fen_after)
                    svg = chess.svg.board(board_after, size=250)
                    st.markdown(f'<div style="display: flex; justify-content: center;">{svg}</div>', unsafe_allow_html=True)
                except:
                    st.write("Board preview unavailable")
            
            with mcol2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Eval", f"{a.eval_score:.0f} cp")
                with col2:
                    st.metric("Risk", f"{a.risk_score:.1f}/100")
                with col3:
                    if not a.is_best_move:
                        st.markdown(f"**Better Move:**")
                        st.code(a.best_alternative)
                    else:
                        st.success("✓ Best move!")
    
    # Player statistics
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
        st.metric("Average Risk", f"{w.get('avg_risk', 0):.1f}/100")
    
    with col2:
        st.markdown("#### ⚫ Black")
        b = report['black']
        st.write(f"🟢 Excellent: {b.get('excellent', 0)}")
        st.write(f"🟡 Good: {b.get('good', 0)}")
        st.write(f"🟠 Inaccuracies: {b.get('inaccuracies', 0)}")
        st.write(f"🔴 Mistakes: {b.get('mistakes', 0)}")
        st.write(f"💥 Blunders: {b.get('blunders', 0)}")
        st.metric("Average Risk", f"{b.get('avg_risk', 0):.1f}/100")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Chess Risk Analyzer</strong></p>
    <p>Soham Gugale • Duke University</p>
    <p><a href='https://chess.com/member/sohamgugale' target='_blank'>Chess.com: Sohamgugale</a> • 
    <a href='https://github.com/sohamgugale' target='_blank'>GitHub: sohamgugale</a></p>
</div>
""", unsafe_allow_html=True)
