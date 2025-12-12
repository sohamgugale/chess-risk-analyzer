"""
Chess Risk Analyzer - Simple & Fast Version
For beginners in quantitative finance
"""
import streamlit as st
import chess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.game_analyzer import GameAnalyzer
from src.risk_calculator import RiskCalculator
from src.visualizer import RiskVisualizer
from src.chess_api import ChessComAPI, get_famous_games

# Page config
st.set_page_config(
    page_title="Chess Risk Analyzer",
    page_icon="♟️",
    layout="wide"
)

# Simple CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">♟️ Chess Risk Analyzer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Simple Quantitative Chess Analysis for Beginners</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    mode = st.radio(
        "Choose Mode",
        ["📚 Sample Games", "📝 Your Games", "📁 Upload PGN"],
        help="Select how you want to analyze"
    )
    
    st.divider()
    
    max_moves = st.slider(
        "Moves to Analyze",
        min_value=5,
        max_value=30,
        value=15,
        step=5,
        help="Analyzing fewer moves is faster"
    )
    
    st.divider()
    
    st.info("""
    **How to use:**
    1. Select a game mode
    2. Choose a game
    3. Click "Analyze"
    4. View results!
    
    **Fast Analysis:** We analyze only the first 15 moves for speed.
    """)

# Sample games
def get_simple_sample_games():
    """Beginner-friendly sample games"""
    return {
        "🎯 Scholar's Mate (4 moves)": """[Event "Beginner Trap"]
[White "White"]
[Black "Black"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0""",
        
        "🏰 Italian Game Opening": """[Event "Italian Game"]
[White "White"]
[Black "Black"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Bd2 Bxd2+ 8. Nbxd2 d5 9. exd5 Nxd5 10. Qb3 *""",
        
        "🐉 Sicilian Defense": """[Event "Sicilian"]
[White "White"]
[Black "Black"]
[Result "*"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Be2 e5 7. Nb3 Be7 8. O-O O-O 9. Be3 Be6 10. f4 *""",
        
        "👑 Queen's Gambit": """[Event "Queen's Gambit"]
[White "White"]
[Black "Black"]
[Result "*"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Be7 5. e3 O-O 6. Nf3 h6 7. Bh4 b6 8. cxd5 Nxd5 9. Bxe7 Qxe7 10. Nxd5 *""",
        
        "⚔️ King's Indian Defense": """[Event "King's Indian"]
[White "White"]
[Black "Black"]
[Result "*"]

1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. O-O Nc6 8. d5 Ne7 9. Ne1 Nd7 10. Be3 *"""
    }

# Main content
if mode == "📚 Sample Games":
    st.subheader("📚 Learn from Sample Games")
    
    sample_games = get_simple_sample_games()
    selected = st.selectbox("Choose a game:", list(sample_games.keys()))
    
    pgn_input = sample_games[selected]
    
    # Show PGN
    with st.expander("📄 View PGN"):
        st.code(pgn_input, language="text")

elif mode == "📝 Your Games":
    st.subheader("📝 Your Chess.com Games")
    
    st.info("Loading games from Chess.com username: **Sohamgugale**")
    
    try:
        api = ChessComAPI("sohamgugale")
        
        with st.spinner("Fetching games..."):
            games = api.get_recent_games(n_months=1)
        
        if games:
            st.success(f"Found {len(games)} recent games!")
            
            # Show last 10 games
            game_options = []
            for i, game in enumerate(games[-10:], 1):
                info = api.format_game_info(game)
                label = f"Game {i}: {info['white']} vs {info['black']} ({info['time_class']})"
                game_options.append((label, info['pgn']))
            
            selected_idx = st.selectbox(
                "Select a game:",
                range(len(game_options)),
                format_func=lambda x: game_options[x][0]
            )
            
            pgn_input = game_options[selected_idx][1]
            
            with st.expander("📄 View PGN"):
                st.code(pgn_input, language="text")
        else:
            st.warning("No games found. Try uploading a PGN instead!")
            pgn_input = None
    
    except Exception as e:
        st.error(f"Couldn't load Chess.com games: {e}")
        st.info("Try using Sample Games or Upload PGN instead")
        pgn_input = None

else:  # Upload PGN
    st.subheader("📁 Upload Your Game")
    
    upload_method = st.radio("How to provide PGN:", ["Paste Text", "Upload File"])
    
    if upload_method == "Paste Text":
        pgn_input = st.text_area(
            "Paste PGN here:",
            height=200,
            placeholder="[Event \"My Game\"]\n\n1. e4 e5 2. Nf3..."
        )
    else:
        uploaded = st.file_uploader("Upload PGN file", type=['pgn', 'txt'])
        if uploaded:
            pgn_input = uploaded.read().decode('utf-8')
            st.success("✅ File uploaded!")
        else:
            pgn_input = None

# Analyze button
if 'pgn_input' in locals() and pgn_input:
    if st.button("🚀 Analyze Game", type="primary", use_container_width=True):
        
        with st.spinner(f"Analyzing first {max_moves} moves... (takes ~30 seconds)"):
            try:
                # Create analyzer
                analyzer = GameAnalyzer(depth=10)  # Lower depth for speed
                
                # Analyze
                analyses, report = analyzer.analyze_pgn_string(pgn_input, max_moves=max_moves)
                analyzer.close()
                
                if not analyses:
                    st.error("No moves found in PGN")
                else:
                    st.success(f"✅ Analyzed {len(analyses)} moves!")
                    
                    # Store results
                    st.session_state['analyses'] = analyses
                    st.session_state['report'] = report
            
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

# Display results
if 'analyses' in st.session_state:
    analyses = st.session_state['analyses']
    report = st.session_state['report']
    
    st.divider()
    st.header("📊 Analysis Results")
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Moves Analyzed", report['total_moves'])
    with col2:
        blunders = report['white'].get('blunders', 0) + report['black'].get('blunders', 0)
        st.metric("Blunders", blunders, delta=None, delta_color="inverse")
    with col3:
        mistakes = report['white'].get('mistakes', 0) + report['black'].get('mistakes', 0)
        st.metric("Mistakes", mistakes, delta=None, delta_color="inverse")
    with col4:
        avg_risk = (report['white'].get('avg_risk', 0) + report['black'].get('avg_risk', 0)) / 2
        st.metric("Avg Risk", f"{avg_risk:.1f}/100")
    
    st.divider()
    
    # Move by move
    st.subheader("📝 Move-by-Move Analysis")
    
    for analysis in analyses:
        player = "⚪ White" if analysis.white_to_move else "⚫ Black"
        
        # Color code by quality
        if analysis.classification == "excellent":
            color = "🟢"
        elif analysis.classification == "good":
            color = "🟡"
        elif analysis.classification == "inaccuracy":
            color = "🟠"
        elif analysis.classification == "mistake":
            color = "🔴"
        else:  # blunder
            color = "💥"
        
        with st.expander(f"{color} Move {analysis.move_number}. {analysis.move} ({player}) - {analysis.classification.upper()}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Evaluation", f"{analysis.eval_score:.0f} cp")
            with col2:
                st.metric("Risk Score", f"{analysis.risk_score:.1f}/100")
            with col3:
                st.write("**Best Move:**")
                st.code(analysis.best_alternative if not analysis.is_best_move else "✓ Played best move!")
    
    # Simple stats
    st.divider()
    st.subheader("📈 Player Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚪ White")
        w = report['white']
        st.write(f"**Excellent moves:** {w.get('excellent', 0)}")
        st.write(f"**Good moves:** {w.get('good', 0)}")
        st.write(f"**Inaccuracies:** {w.get('inaccuracies', 0)}")
        st.write(f"**Mistakes:** {w.get('mistakes', 0)}")
        st.write(f"**Blunders:** {w.get('blunders', 0)}")
        st.write(f"**Avg Risk:** {w.get('avg_risk', 0):.1f}/100")
    
    with col2:
        st.markdown("### ⚫ Black")
        b = report['black']
        st.write(f"**Excellent moves:** {b.get('excellent', 0)}")
        st.write(f"**Good moves:** {b.get('good', 0)}")
        st.write(f"**Inaccuracies:** {b.get('inaccuracies', 0)}")
        st.write(f"**Mistakes:** {b.get('mistakes', 0)}")
        st.write(f"**Blunders:** {b.get('blunders', 0)}")
        st.write(f"**Avg Risk:** {b.get('avg_risk', 0):.1f}/100")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
Built with ♟️ by Soham Gugale • Duke University • Chess.com: Sohamgugale
</div>
""", unsafe_allow_html=True)
