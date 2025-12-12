"""
Chess Risk Analyzer - Dark Mode with Interactive Board
Simple quantitative analysis for chess enthusiasts
"""
import streamlit as st
import chess
import chess.svg
import sys
from pathlib import Path
import base64

sys.path.insert(0, str(Path(__file__).parent))

from src.game_analyzer import GameAnalyzer
from src.risk_calculator import RiskCalculator
from src.chess_api import ChessComAPI, get_famous_games

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
    /* Main styling */
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
    
    /* Metric cards */
    .metric-card {
        background: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #FF4B4B;
        margin: 0.5rem 0;
    }
    
    /* Move quality badges */
    .excellent { color: #00FF00; font-weight: bold; }
    .good { color: #90EE90; font-weight: bold; }
    .inaccuracy { color: #FFA500; font-weight: bold; }
    .mistake { color: #FF6347; font-weight: bold; }
    .blunder { color: #FF0000; font-weight: bold; }
    
    /* Chess board container */
    .chess-board {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: #1E1E1E;
        padding: 1rem;
        border-left: 4px solid #FF4B4B;
        border-radius: 5px;
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
        ["🎮 Interactive Board", "📚 Sample Games", "👤 My Games (Sohamgugale)", "📁 Upload PGN"],
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
    
    # Metrics explanation
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
        
        **Complexity**
        - Measures position difficulty
        - Based on: pieces on board, possible moves, tactics
        """)
    
    st.divider()
    
    st.info("""
    **Quick Start:**
    1. Choose a mode
    2. Select/upload game
    3. Click Analyze
    4. Review suggestions!
    
    **Chess.com:** Sohamgugale  
    **GitHub:** sohamgugale
    """)

# Sample games
def get_sample_games():
    return {
        "🎯 Scholar's Mate (Beginner Trap)": """[Event "Scholar's Mate"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0""",
        
        "🏰 Italian Game": """[Event "Italian Game"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Bd2 Bxd2+ 8. Nbxd2 d5 9. exd5 Nxd5 10. Qb3 Nce7 11. O-O O-O 12. Rfe1 *""",
        
        "🐉 Sicilian Defense": """[Event "Sicilian Dragon"]
[Result "*"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 6. Be3 Bg7 7. f3 O-O 8. Qd2 Nc6 9. Bc4 Bd7 10. O-O-O Rc8 11. Bb3 Ne5 *""",
        
        "👑 Queen's Gambit": """[Event "Queen's Gambit"]
[Result "*"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Be7 5. e3 O-O 6. Nf3 h6 7. Bh4 b6 8. cxd5 Nxd5 9. Bxe7 Qxe7 10. Nxd5 exd5 *""",
        
        "⚔️ King's Indian": """[Event "King's Indian Defense"]
[Result "*"]

1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. O-O Nc6 8. d5 Ne7 9. Ne1 Nd7 10. Be3 f5 *"""
    }

# Main content based on mode
pgn_input = None

if mode == "🎮 Interactive Board":
    st.markdown("## 🎮 Interactive Chess Board")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Board Position")
        render_board(st.session_state.board)
        
        # Board controls
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
        
        with ctrl_col1:
            if st.button("🔄 Reset Board"):
                st.session_state.board = chess.Board()
                st.session_state.move_history = []
                st.rerun()
        
        with ctrl_col2:
            if st.button("↩️ Undo Move"):
                if st.session_state.board.move_stack:
                    st.session_state.board.pop()
                    if st.session_state.move_history:
                        st.session_state.move_history.pop()
                    st.rerun()
        
        with ctrl_col3:
            if st.button("📋 Copy FEN"):
                st.code(st.session_state.board.fen())
        
        # FEN input
        st.markdown("### Load Position")
        fen_input = st.text_input(
            "Enter FEN:",
            value=st.session_state.board.fen(),
            help="Paste FEN to load a position"
        )
        
        if st.button("Load FEN"):
            try:
                st.session_state.board = chess.Board(fen_input)
                st.session_state.move_history = []
                st.success("✅ Position loaded!")
                st.rerun()
            except:
                st.error("Invalid FEN string!")
    
    with col2:
        st.markdown("### 🎯 Analysis & Suggestions")
        
        if st.button("🔍 Analyze Position", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    calc = RiskCalculator(depth=12)
                    metrics = calc.calculate_risk_metrics(st.session_state.board)
                    calc.close()
                    
                    # Display metrics
                    st.markdown(f"""
                    <div class="metric-card">
                    <h4>📊 Position Evaluation</h4>
                    <p><strong>Evaluation:</strong> {metrics.position_eval:.0f} cp</p>
                    <p><strong>Risk Score:</strong> {metrics.risk_score:.1f}/100</p>
                    <p><strong>Complexity:</strong> {metrics.complexity:.1f}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Top moves
                    st.markdown("### 🎯 Top 3 Moves")
                    for i, move in enumerate(metrics.top_moves[:3], 1):
                        st.markdown(f"""
                        **{i}. {move['move']}**  
                        Evaluation: {move['score']:.0f} cp
                        """)
                    
                    st.session_state['current_metrics'] = metrics
                
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Make move
        st.markdown("### 🎮 Make a Move")
        move_input = st.text_input(
            "Enter move (e.g., e2e4 or e4):",
            key="move_input"
        )
        
        if st.button("▶️ Play Move"):
            try:
                # Try UCI format first
                move = None
                try:
                    move = chess.Move.from_uci(move_input)
                except:
                    # Try SAN format
                    try:
                        move = st.session_state.board.parse_san(move_input)
                    except:
                        pass
                
                if move and move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.session_state.move_history.append(move_input)
                    st.success(f"✅ Played: {move_input}")
                    st.rerun()
                else:
                    st.error("❌ Illegal move!")
            except Exception as e:
                st.error(f"Invalid move format! Use: e2e4 or e4")
        
        # Move history
        if st.session_state.move_history:
            st.markdown("### 📜 Move History")
            for i, move in enumerate(st.session_state.move_history, 1):
                st.text(f"{i}. {move}")

elif mode == "📚 Sample Games":
    st.markdown("## 📚 Sample Games")
    
    samples = get_sample_games()
    selected = st.selectbox("Choose a game:", list(samples.keys()))
    pgn_input = samples[selected]
    
    with st.expander("📄 View PGN"):
        st.code(pgn_input)

elif mode == "👤 My Games (Sohamgugale)":
    st.markdown("## 👤 Your Chess.com Games")
    
    st.info("**Fetching games for:** Sohamgugale")
    
    # Test connection
    test_url = "https://api.chess.com/pub/player/sohamgugale"
    st.caption(f"Testing API: {test_url}")
    
    try:
        api = ChessComAPI("sohamgugale")
        
        with st.spinner("Loading your profile..."):
            profile = api.get_player_profile()
        
        if not profile:
            st.error("""
            ❌ **Cannot access Chess.com profile**
            
            **Possible reasons:**
            1. Your profile might be private
            2. Username might be incorrect
            3. Chess.com API might be down
            
            **To fix:**
            1. Go to: https://www.chess.com/settings
            2. Click "Privacy"
            3. Enable "Allow other members to see my profile"
            4. Wait a few minutes and try again
            
            **Alternative:** Use "Upload PGN" and download games manually from Chess.com
            """)
        else:
            st.success(f"✅ Connected to profile: **{profile.get('username', 'Unknown')}**")
            
            # Show profile info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Username", profile.get('username', 'N/A'))
            with col2:
                st.metric("Followers", profile.get('followers', 'N/A'))
            with col3:
                st.metric("Country", profile.get('country', 'N/A').split('/')[-1])
            
            # Get games
            with st.spinner("Fetching recent games..."):
                games = api.get_recent_games(n_months=1)
            
            if games:
                st.success(f"✅ Found {len(games)} games from the last month!")
                
                # Display game options
                game_options = []
                for i, game in enumerate(games[-15:], 1):  # Last 15 games
                    info = api.format_game_info(game)
                    label = f"{i}. {info['white']} vs {info['black']} • {info['time_class']} • {info['result']}"
                    game_options.append((label, info['pgn']))
                
                selected_idx = st.selectbox(
                    "Select a game to analyze:",
                    range(len(game_options)),
                    format_func=lambda x: game_options[x][0]
                )
                
                pgn_input = game_options[selected_idx][1]
                
                with st.expander("📄 View PGN"):
                    st.code(pgn_input)
            else:
                st.warning("No recent games found. Try uploading a PGN instead!")
    
    except Exception as e:
        st.error(f"**Error connecting to Chess.com:** {e}")
        st.info("Try using 'Upload PGN' mode instead")

else:  # Upload PGN
    st.markdown("## 📁 Upload Your Game")
    
    upload_type = st.radio("How to provide PGN:", ["Paste Text", "Upload File"])
    
    if upload_type == "Paste Text":
        pgn_input = st.text_area(
            "Paste PGN here:",
            height=250,
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
        with st.spinner(f"Analyzing first {max_moves} moves... (~30 seconds)"):
            try:
                analyzer = GameAnalyzer(depth=10)
                analyses, report = analyzer.analyze_pgn_string(pgn_input, max_moves=max_moves)
                analyzer.close()
                
                if analyses:
                    st.success(f"✅ Analysis complete! Analyzed {len(analyses)} moves")
                    st.session_state['analyses'] = analyses
                    st.session_state['report'] = report
                else:
                    st.error("No moves found in PGN")
            
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

# Display game analysis results
if 'analyses' in st.session_state and mode != "🎮 Interactive Board":
    analyses = st.session_state['analyses']
    report = st.session_state['report']
    
    st.divider()
    st.markdown("## 📊 Analysis Results")
    
    # Summary metrics
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
    
    # Move-by-move
    st.markdown("### 📝 Move-by-Move Analysis")
    
    for a in analyses:
        # Quality color
        quality_class = a.classification
        emoji = {"excellent": "🟢", "good": "🟡", "inaccuracy": "🟠", "mistake": "🔴", "blunder": "💥"}
        
        player = "⚪" if a.white_to_move else "⚫"
        
        with st.expander(
            f"{emoji.get(quality_class, '⚪')} Move {a.move_number}. {a.move} ({player}) • {quality_class.upper()}"
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Evaluation", f"{a.eval_score:.0f} cp")
            with col2:
                st.metric("Risk", f"{a.risk_score:.1f}/100")
            with col3:
                if not a.is_best_move:
                    st.markdown(f"**Better:** `{a.best_alternative}`")
                else:
                    st.success("✓ Best move!")
    
    # Player stats
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
    <p>Built by Soham Gugale • Duke University</p>
    <p>Chess.com: <a href='https://chess.com/member/sohamgugale' target='_blank'>Sohamgugale</a> • 
    GitHub: <a href='https://github.com/sohamgugale' target='_blank'>sohamgugale</a></p>
</div>
""", unsafe_allow_html=True)
