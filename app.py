"""
Chess Risk Analyzer - Streamlit Web Interface
Quantitative chess analysis using financial risk modeling concepts
"""
import streamlit as st
import chess
import chess.pgn
from io import StringIO
import pandas as pd
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import traceback

sys.path.insert(0, str(Path(__file__).parent))

from src.game_analyzer import GameAnalyzer
from src.risk_calculator import RiskCalculator
from src.visualizer import RiskVisualizer
from src.chess_api import ChessComAPI, LichessAPI, get_famous_games

# Page config
st.set_page_config(
    page_title="Chess Risk Analyzer",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def get_soham_games():
    """Get Soham's recent games from Chess.com"""
    try:
        api = ChessComAPI("sohamgugale")
        
        # Get player stats
        stats = api.get_player_stats()
        profile = api.get_player_profile()
        
        # Get recent games
        games = api.get_recent_games(n_months=1)
        
        # Format games
        game_list = []
        for game in games[-10:]:  # Last 10 games
            formatted = api.format_game_info(game)
            if formatted['pgn']:
                game_list.append({
                    'name': f"{formatted['white']} vs {formatted['black']} ({formatted['time_class']})",
                    'pgn': formatted['pgn'],
                    'info': formatted
                })
        
        return game_list, stats, profile
    except Exception as e:
        st.error(f"Could not load Chess.com games: {e}")
        return [], {}, {}


def get_sample_games_extended():
    """Extended collection of sample games"""
    famous = get_famous_games()
    
    samples = {
        "🔥 Scholar's Mate (Beginner Trap)": """[Event "Scholar's Mate Example"]
[Site "?"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0""",
        
        "🎯 Italian Game (Classic Opening)": """[Event "Italian Game"]
[Site "?"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Nc3 Nxe4 8. O-O Bxc3 9. bxc3 d5 10. Ba3 *""",
        
        "🐉 Sicilian Dragon (Aggressive)": """[Event "Sicilian Dragon"]
[Site "?"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "*"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 g6 6. Be3 Bg7 7. f3 O-O 8. Qd2 Nc6 9. Bc4 Bd7 10. O-O-O Rc8 11. Bb3 Ne5 12. h4 h5 *""",
        
        "👑 Kasparov's Immortal": famous["Kasparov's Immortal"],
        "🎨 Fischer's Game of the Century": famous["Fischer's Game of the Century"],
        "⚔️ The Immortal Game": famous["The Immortal Game"],
        "🎭 Opera Game (Morphy)": famous["Opera Game"],
        "🌲 Evergreen Game": famous["Evergreen Game"],
    }
    
    return samples


def main():
    # Header
    st.markdown('<h1 class="main-header">♟️ Chess Risk Analyzer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Quantitative Analysis Using Financial Risk Modeling • Created for Chess Enthusiasts</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/PedroPinhata/phpkXK09k.png", width=100)
        st.header("⚙️ Configuration")
        
        analysis_mode = st.radio(
            "Analysis Mode",
            ["📁 Upload PGN", "📝 Paste PGN", "🎮 Sample Games", "👤 Soham's Games", "🎯 Live Position"],
            help="Choose how to input your game"
        )
        
        st.divider()
        
        st.subheader("Analysis Settings")
        n_simulations = st.slider(
            "Monte Carlo Simulations",
            min_value=5,
            max_value=25,
            value=12,
            step=3,
            help="More simulations = more accurate but slower"
        )
        
        depth = st.slider(
            "Engine Depth",
            min_value=8,
            max_value=16,
            value=12,
            step=2,
            help="Search depth for position evaluation"
        )
        
        max_moves = st.number_input(
            "Max Moves to Analyze",
            min_value=10,
            max_value=100,
            value=40,
            step=5,
            help="Limit analysis to first N moves (for speed)"
        )
        
        st.divider()
        
        st.subheader("📊 About the Metrics")
        with st.expander("Risk Score"):
            st.write("""
            **0-30**: Low risk, stable position
            **30-60**: Medium risk, tactical complications
            **60-100**: High risk, sharp position
            """)
        
        with st.expander("Volatility"):
            st.write("Standard deviation of evaluations across simulated continuations. Higher = more uncertainty.")
        
        with st.expander("Value at Risk (VaR)"):
            st.write("Worst-case evaluation at 95% confidence. Shows downside exposure.")
        
        st.divider()
        
        st.markdown("### 👨‍💻 About")
        st.info("""
        **Chess Risk Analyzer** applies quantitative finance concepts to chess:
        
        - 📈 Monte Carlo simulation
        - 📊 Volatility analysis
        - 🎯 Risk scoring
        - 📉 Downside risk metrics
        
        Built by a 1600-rated chess enthusiast studying quant finance at Duke.
        """)
        
        st.markdown("---")
        st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-View_Source-black?logo=github)](https://github.com/yourusername/chess-risk-analyzer)")
    
    # Main content
    pgn_input = None
    game_info = None
    
    if analysis_mode == "📁 Upload PGN":
        st.subheader("📁 Upload PGN File")
        uploaded_file = st.file_uploader(
            "Choose a PGN file",
            type=['pgn', 'txt'],
            help="Upload a PGN file from chess.com, lichess, or any other source"
        )
        
        if uploaded_file:
            pgn_input = uploaded_file.read().decode('utf-8')
            st.success("✅ File uploaded successfully!")
    
    elif analysis_mode == "📝 Paste PGN":
        st.subheader("📝 Paste PGN")
        pgn_input = st.text_area(
            "Paste your PGN here",
            height=250,
            placeholder="[Event \"Casual Game\"]\n[Site \"?\"]\n...\n\n1. e4 e5 2. Nf3...",
            help="Copy PGN from chess.com or lichess and paste here"
        )
    
    elif analysis_mode == "🎮 Sample Games":
        st.subheader("🎮 Sample Games Collection")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            Explore famous games and common openings:
            - 🔥 Tactical traps and tricks
            - 🎯 Classic opening theory
            - 👑 Legendary grandmaster games
            """)
        
        sample_games = get_sample_games_extended()
        selected_game = st.selectbox("Choose a game", list(sample_games.keys()))
        
        if st.button("🚀 Load Game", type="primary", use_container_width=True):
            pgn_input = sample_games[selected_game]
            st.success(f"✅ Loaded: {selected_game}")
    
    elif analysis_mode == "👤 Soham's Games":
        st.subheader("👤 Soham's Recent Games")
        
        with st.spinner("Loading games from Chess.com..."):
            games_list, stats, profile = get_soham_games()
        
        if games_list:
            # Display player info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("👤 Username", "Sohamgugale")
            with col2:
                rapid_rating = stats.get('chess_rapid', {}).get('last', {}).get('rating', 'N/A')
                st.metric("⚡ Rapid Rating", rapid_rating)
            with col3:
                followers = profile.get('followers', 'N/A')
                st.metric("👥 Followers", followers)
            
            st.divider()
            
            # Select game
            game_names = [g['name'] for g in games_list]
            selected_idx = st.selectbox("Select a game to analyze", range(len(game_names)), 
                                       format_func=lambda x: game_names[x])
            
            if st.button("🚀 Analyze This Game", type="primary", use_container_width=True):
                selected_game = games_list[selected_idx]
                pgn_input = selected_game['pgn']
                game_info = selected_game['info']
                st.success(f"✅ Loaded: {selected_game['name']}")
        else:
            st.warning("Could not load games. Check the username or try again later.")
    
    elif analysis_mode == "🎯 Live Position":
        st.subheader("🎯 Analyze Single Position")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fen_input = st.text_input(
                "FEN String",
                value="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                help="Paste a FEN string of the position you want to analyze"
            )
        
        with col2:
            st.markdown("#### Quick FENs")
            if st.button("Starting Position"):
                fen_input = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            if st.button("Open Italian"):
                fen_input = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        
        if st.button("🔍 Analyze Position", type="primary", use_container_width=True):
            with st.spinner("Calculating risk metrics..."):
                try:
                    board = chess.Board(fen_input)
                    
                    # Display board
                    viz = RiskVisualizer()
                    svg = viz.create_board_svg(fen_input)
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.image(svg, use_container_width=True)
                    
                    with col2:
                        with RiskCalculator(n_simulations=n_simulations, depth=depth) as calc:
                            metrics = calc.calculate_risk_metrics(board)
                            risk_score = calc.risk_score(metrics)
                            
                            # Display metrics
                            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                            
                            with metric_col1:
                                st.metric("Overall Risk", f"{risk_score:.1f}/100")
                            with metric_col2:
                                st.metric("Volatility", f"{metrics.volatility:.1f}")
                            with metric_col3:
                                st.metric("Complexity", f"{metrics.complexity_risk:.1f}")
                            with metric_col4:
                                st.metric("Tactical", f"{metrics.tactical_density:.1f}")
                            
                            # Detailed metrics
                            with st.expander("📊 Detailed Metrics"):
                                detail_col1, detail_col2 = st.columns(2)
                                
                                with detail_col1:
                                    st.write("**Position Evaluation**")
                                    st.write(f"Expected Value: {metrics.expected_value:.0f} cp")
                                    st.write(f"VaR (95%): {metrics.var_95:.0f} cp")
                                    st.write(f"Downside Risk: {metrics.downside_risk:.1%}")
                                
                                with detail_col2:
                                    st.write("**Strategic Factors**")
                                    st.write(f"Best Move Edge: {metrics.best_move_edge:.0f} cp")
                                    st.write(f"Complexity: {metrics.complexity_risk:.1f}")
                                    st.write(f"Tactical Density: {metrics.tactical_density:.1f}")
                            
                            # Risk interpretation
                            st.markdown("### 💡 Risk Interpretation")
                            if risk_score < 30:
                                st.success("**🟢 Low Risk Position** - Relatively stable with clear plan")
                            elif risk_score < 60:
                                st.warning("**🟡 Medium Risk Position** - Some tactical complications present")
                            else:
                                st.error("**🔴 High Risk Position** - Sharp, requires precise play")
                
                except Exception as e:
                    st.error(f"Error analyzing position: {str(e)}")
                    st.code(traceback.format_exc())
    
    # Analyze game if PGN provided
    if pgn_input and analysis_mode != "🎯 Live Position":
        if st.button("🚀 Analyze Game", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Analyzing game (max {max_moves} moves)... This may take a few minutes."):
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Initializing analyzer...")
                    progress_bar.progress(10)
                    
                    # Create analyzer
                    analyzer = GameAnalyzer(n_simulations=n_simulations, depth=depth)
                    
                    status_text.text("Analyzing moves...")
                    progress_bar.progress(30)
                    
                    # Parse and analyze
                    analyses, report = analyzer.analyze_pgn_string(pgn_input, max_moves=max_moves)
                    analyzer.close()
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    if not analyses:
                        st.error("❌ No moves found in PGN. Please check the format.")
                        return
                    
                    # Store in session state
                    st.session_state['analyses'] = analyses
                    st.session_state['report'] = report
                    st.session_state['game_info'] = game_info
                    
                    st.success(f"✅ Analyzed {len(analyses)} moves successfully!")
                    st.balloons()
            
            except Exception as e:
                st.error(f"❌ Error analyzing game: {str(e)}")
                st.code(traceback.format_exc())
    
    # Display results if available
    if 'analyses' in st.session_state and 'report' in st.session_state:
        analyses = st.session_state['analyses']
        report = st.session_state['report']
        game_info = st.session_state.get('game_info')
        
        st.divider()
        st.header("📊 Analysis Results")
        
        # Game info if available
        if game_info:
            st.markdown(f"""
            **Game**: {game_info['white']} ({game_info['white_rating']}) vs {game_info['black']} ({game_info['black_rating']})  
            **Time Control**: {game_info['time_control']} • **Result**: {game_info['result']}
            """)
            st.divider()
        
        # Summary metrics
        st.subheader("📈 Game Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Moves", report['total_moves'])
        with col2:
            st.metric("Blunders", report['total_blunders'], 
                     delta=None, delta_color="inverse")
        with col3:
            st.metric("Mistakes", report['total_mistakes'],
                     delta=None, delta_color="inverse")
        with col4:
            highest_risk = report.get('highest_risk_move', 0)
            st.metric("Highest Risk", f"Move #{highest_risk}")
        with col5:
            avg_risk = (report.get('white', {}).get('avg_risk_score', 0) + 
                       report.get('black', {}).get('avg_risk_score', 0)) / 2
            st.metric("Avg Risk", f"{avg_risk:.1f}")
        
        st.divider()
        
        # Player comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚪ White Performance")
            if report.get('white'):
                white_stats = report['white']
                
                # Big accuracy metric
                accuracy = white_stats.get('accuracy', 0)
                st.metric("🎯 Accuracy", f"{accuracy:.1f}%")
                
                # Other stats in columns
                wcol1, wcol2 = st.columns(2)
                with wcol1:
                    st.metric("Avg Risk", f"{white_stats.get('avg_risk_score', 0):.1f}")
                    st.metric("Best Moves", white_stats.get('num_best_moves', 0))
                with wcol2:
                    st.metric("Blunders", white_stats.get('num_blunders', 0))
                    st.metric("Mistakes", white_stats.get('num_mistakes', 0))
        
        with col2:
            st.markdown("### ⚫ Black Performance")
            if report.get('black'):
                black_stats = report['black']
                
                # Big accuracy metric
                accuracy = black_stats.get('accuracy', 0)
                st.metric("🎯 Accuracy", f"{accuracy:.1f}%")
                
                # Other stats in columns
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    st.metric("Avg Risk", f"{black_stats.get('avg_risk_score', 0):.1f}")
                    st.metric("Best Moves", black_stats.get('num_best_moves', 0))
                with bcol2:
                    st.metric("Blunders", black_stats.get('num_blunders', 0))
                    st.metric("Mistakes", black_stats.get('num_mistakes', 0))
        
        st.divider()
        
        # Tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Risk Timeline", "📊 Move Quality", "🎯 Detailed Analysis", "📥 Export Data"])
        
        with tab1:
            st.subheader("Risk Score Evolution")
            viz = RiskVisualizer()
            
            fig = viz.plot_risk_over_time(analyses)
            st.pyplot(fig)
            plt.close()
            
            st.subheader("Evaluation vs Risk")
            fig = viz.plot_eval_and_risk(analyses)
            st.pyplot(fig)
            plt.close()
        
        with tab2:
            st.subheader("Move Quality Distribution")
            viz = RiskVisualizer()
            
            fig = viz.plot_move_quality_distribution(analyses)
            st.pyplot(fig)
            plt.close()
            
            st.subheader("Risk by Game Phase")
            fig = viz.plot_risk_heatmap_by_phase(analyses)
            st.pyplot(fig)
            plt.close()
        
        with tab3:
            st.subheader("Move-by-Move Analysis")
            
            # Create DataFrame
            df_data = []
            for a in analyses:
                quality = ('Best' if a.is_best_move else 
                          'Blunder' if a.was_blunder else
                          'Mistake' if a.was_mistake else
                          'Inaccuracy' if a.was_inaccuracy else 'Good')
                
                df_data.append({
                    'Move': f"{a.move_number}. {a.move}",
                    'Player': '⚪' if a.white_to_move else '⚫',
                    'Risk': f"{a.risk_score:.1f}",
                    'Eval': f"{a.eval_after:.0f}",
                    'Δ Eval': f"{a.eval_change:.0f}",
                    'Quality': quality
                })
            
            df = pd.DataFrame(df_data)
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                player_filter = st.multiselect(
                    "Filter by Player",
                    ['⚪', '⚫'],
                    default=['⚪', '⚫']
                )
            with col2:
                quality_filter = st.multiselect(
                    "Filter by Quality",
                    ['Best', 'Good', 'Inaccuracy', 'Mistake', 'Blunder'],
                    default=['Best', 'Good', 'Inaccuracy', 'Mistake', 'Blunder']
                )
            with col3:
                min_risk = st.slider("Min Risk Score", 0, 100, 0)
            
            # Apply filters
            filtered_df = df[
                (df['Player'].isin(player_filter)) &
                (df['Quality'].isin(quality_filter)) &
                (df['Risk'].astype(float) >= min_risk)
            ]
            
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Critical moments
            st.subheader("🚨 Critical Moments")
            critical_moves = [a for a in analyses if a.was_blunder or a.risk_score > 70]
            
            if critical_moves:
                for move in critical_moves[:5]:
                    with st.expander(f"Move {move.move_number}. {move.move} - Risk: {move.risk_score:.1f}/100"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Before Move**")
                            viz = RiskVisualizer()
                            svg = viz.create_board_svg(move.fen_before)
                            if svg:
                                st.image(svg, width=300)
                        
                        with col2:
                            st.markdown("**After Move**")
                            svg = viz.create_board_svg(move.fen_after)
                            if svg:
                                st.image(svg, width=300)
                        
                        st.markdown(f"**Eval Change**: {move.eval_change:.0f} centipawns")
                        if move.was_blunder:
                            st.error("💥 This was a blunder!")
                        elif move.was_mistake:
                            st.warning("⚠️ This was a mistake")
            else:
                st.success("✅ No critical moments found - solid game!")
        
        with tab4:
            st.subheader("Export Analysis Data")
            
            col1, col2, col3 = st.columns(3)
            
            # Export DataFrame
            analyzer = GameAnalyzer(n_simulations=5, depth=10)
            df_export = analyzer.export_to_dataframe(analyses)
            analyzer.close()
            
            with col1:
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="chess_analysis.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                json_data = df_export.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name="chess_analysis.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col3:
                # Summary report
                import json
                summary = {
                    "game_summary": report,
                    "total_analyses": len(analyses),
                    "settings": {
                        "n_simulations": n_simulations,
                        "depth": depth
                    }
                }
                st.download_button(
                    label="📥 Download Report",
                    data=json.dumps(summary, indent=2),
                    file_name="game_report.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.info("💡 **Tip**: Use CSV for Excel analysis, JSON for programming")
            
            # Preview data
            with st.expander("📊 Preview Export Data"):
                st.dataframe(df_export.head(10), use_container_width=True)


if __name__ == "__main__":
    main()