"""
Visualization utilities for risk analysis
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict
import chess
import chess.svg
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class RiskVisualizer:
    """Create visualizations for risk analysis"""
    
    def __init__(self):
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def plot_risk_over_time(self, analyses: List, save_path: str = None) -> plt.Figure:
        """Plot risk score evolution throughout the game"""
        fig, ax = plt.subplots(figsize=(14, 6))
        
        if not analyses:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            return fig
        
        white_moves = [(a.move_number, a.risk_score) for a in analyses if a.white_to_move]
        black_moves = [(a.move_number, a.risk_score) for a in analyses if not a.white_to_move]
        
        if white_moves:
            white_x, white_y = zip(*white_moves)
            ax.plot(white_x, white_y, 'o-', color='#3498db', 
                   label='White', linewidth=2.5, markersize=7, alpha=0.8)
        
        if black_moves:
            black_x, black_y = zip(*black_moves)
            ax.plot(black_x, black_y, 's-', color='#34495e', 
                   label='Black', linewidth=2.5, markersize=7, alpha=0.8)
        
        # Mark blunders
        blunders = [(a.move_number, a.risk_score) for a in analyses if a.was_blunder]
        if blunders:
            blunder_x, blunder_y = zip(*blunders)
            ax.scatter(blunder_x, blunder_y, color='#e74c3c', s=250, 
                      marker='X', zorder=5, label='Blunder', alpha=0.9, edgecolors='darkred', linewidth=2)
        
        ax.set_xlabel('Move Number', fontsize=13, fontweight='bold')
        ax.set_ylabel('Risk Score', fontsize=13, fontweight='bold')
        ax.set_title('Position Risk Throughout Game', fontsize=15, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # Risk zones with labels
        ax.axhspan(0, 30, alpha=0.15, color='green', zorder=0)
        ax.axhspan(30, 60, alpha=0.15, color='yellow', zorder=0)
        ax.axhspan(60, 100, alpha=0.15, color='red', zorder=0)
        
        ax.text(0.02, 15, 'Low Risk', transform=ax.get_yaxis_transform(), 
               fontsize=9, color='green', fontweight='bold', alpha=0.7)
        ax.text(0.02, 45, 'Medium Risk', transform=ax.get_yaxis_transform(), 
               fontsize=9, color='orange', fontweight='bold', alpha=0.7)
        ax.text(0.02, 80, 'High Risk', transform=ax.get_yaxis_transform(), 
               fontsize=9, color='red', fontweight='bold', alpha=0.7)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_eval_and_risk(self, analyses: List, save_path: str = None) -> plt.Figure:
        """Plot evaluation and risk on dual axes"""
        fig, ax1 = plt.subplots(figsize=(14, 7))
        
        if not analyses:
            ax1.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax1.transAxes)
            return fig
        
        move_numbers = [a.move_number for a in analyses]
        evals = [min(max(a.eval_after, -500), 500) for a in analyses]  # Cap at ±500
        risks = [a.risk_score for a in analyses]
        
        # Plot evaluation
        color = '#3498db'
        ax1.set_xlabel('Move Number', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Evaluation (centipawns)', color=color, fontsize=13, fontweight='bold')
        ax1.plot(move_numbers, evals, color=color, linewidth=2.5, label='Evaluation', alpha=0.9)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.axhline(y=0, color='black', linestyle='--', linewidth=1.5, alpha=0.5)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-500, 500)
        
        # Plot risk on secondary axis
        ax2 = ax1.twinx()
        color = '#e74c3c'
        ax2.set_ylabel('Risk Score', color=color, fontsize=13, fontweight='bold')
        ax2.plot(move_numbers, risks, color=color, linewidth=2.5, 
                linestyle='--', label='Risk', alpha=0.8)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylim(0, 100)
        
        # Mark critical moments
        blunders = [a.move_number for a in analyses if a.was_blunder]
        for move_num in blunders:
            ax1.axvline(x=move_num, color='red', alpha=0.2, linewidth=3, zorder=0)
        
        plt.title('Evaluation vs Risk Throughout Game', fontsize=15, fontweight='bold', pad=20)
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_move_quality_distribution(self, analyses: List, save_path: str = None) -> plt.Figure:
        """Plot distribution of move qualities for each player"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        white_analyses = [a for a in analyses if a.white_to_move]
        black_analyses = [a for a in analyses if not a.white_to_move]
        
        def plot_player_quality(ax, player_analyses, player_name):
            if not player_analyses:
                ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes, fontsize=14)
                ax.set_title(f'{player_name} Move Quality', fontweight='bold', fontsize=13)
                return
            
            categories = ['Best', 'Good', 'Inaccuracy', 'Mistake', 'Blunder']
            
            best = sum(a.is_best_move for a in player_analyses)
            good = len(player_analyses) - best - sum(a.was_inaccuracy or a.was_mistake or a.was_blunder 
                                                     for a in player_analyses)
            inaccuracies = sum(a.was_inaccuracy for a in player_analyses)
            mistakes = sum(a.was_mistake for a in player_analyses)
            blunders = sum(a.was_blunder for a in player_analyses)
            
            counts = [best, good, inaccuracies, mistakes, blunders]
            colors_list = ['#27ae60', '#3498db', '#f39c12', '#e67e22', '#e74c3c']
            
            bars = ax.bar(categories, counts, color=colors_list, alpha=0.85, edgecolor='black', linewidth=1.2)
            ax.set_ylabel('Number of Moves', fontweight='bold', fontsize=12)
            ax.set_title(f'{player_name} Move Quality', fontweight='bold', fontsize=13)
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                           f'{int(height)}',
                           ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            # Calculate accuracy
            accuracy = (best / len(player_analyses) * 100) if player_analyses else 0
            ax.text(0.5, 0.97, f'Accuracy: {accuracy:.1f}%',
                   transform=ax.transAxes, ha='center', va='top',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', alpha=0.9, edgecolor='gray'),
                   fontweight='bold', fontsize=12)
        
        plot_player_quality(ax1, white_analyses, '⚪ White')
        plot_player_quality(ax2, black_analyses, '⚫ Black')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_risk_heatmap_by_phase(self, analyses: List, save_path: str = None) -> plt.Figure:
        """Create heatmap of risk by game phase"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not analyses:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            return fig
        
        # Divide game into phases
        total_moves = len(analyses)
        opening = analyses[:min(10, total_moves)]
        middlegame = analyses[10:max(10, total_moves-10)] if total_moves > 20 else []
        endgame = analyses[max(10, total_moves-10):] if total_moves > 10 else []
        
        phases = []
        for phase_name, phase_analyses in [('Opening', opening), 
                                           ('Middlegame', middlegame), 
                                           ('Endgame', endgame)]:
            if not phase_analyses:
                continue
            
            white = [a.risk_score for a in phase_analyses if a.white_to_move]
            black = [a.risk_score for a in phase_analyses if not a.white_to_move]
            
            phases.append({
                'Phase': phase_name,
                'White Avg': np.mean(white) if white else 0,
                'Black Avg': np.mean(black) if black else 0,
            })
        
        if not phases:
            ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', transform=ax.transAxes)
            return fig
        
        df = pd.DataFrame(phases)
        df_plot = df.set_index('Phase')[['White Avg', 'Black Avg']]
        
        sns.heatmap(df_plot.T, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                   cbar_kws={'label': 'Risk Score'}, ax=ax,
                   vmin=0, vmax=100, linewidths=2, linecolor='white',
                   annot_kws={'fontsize': 12, 'fontweight': 'bold'})
        
        ax.set_title('Average Risk by Game Phase', fontweight='bold', fontsize=14, pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('', fontsize=12)
        ax.tick_params(labelsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_board_svg(self, fen: str, highlight_squares: List[int] = None) -> str:
        """Create SVG representation of board position"""
        try:
            board = chess.Board(fen)
            
            fill = {}
            if highlight_squares:
                for square in highlight_squares:
                    fill[square] = '#ff000060'
            
            svg = chess.svg.board(board, fill=fill, size=400)
            return svg
        except Exception as e:
            print(f"Error creating board SVG: {e}")
            return ""


if __name__ == "__main__":
    print("Visualizer module loaded successfully")