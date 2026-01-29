"""
Statistics Generator Module
Generates comprehensive statistics and visualizations for match analysis.
Adapted from CoachAI Visualization Platform statistics components.

Statistics Include:
- Rally duration analysis
- Shot type distribution
- Landing position heatmaps
- Player comparison charts
- Win/loss breakdown
- Performance metrics
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import os
from io import BytesIO
import base64

class StatisticsGenerator:
    """
    Generates statistical analysis and visualizations for badminton match data.
    Produces graphs similar to CoachAI's stimulateTabCtrl.py visualizations.
    """
    
    # Court dimensions for heatmap (in cm)
    COURT_WIDTH = 610
    COURT_LENGTH = 1340
    HALF_COURT_LENGTH = 670
    
    # Color schemes
    PLAYER_A_COLOR = '#FF7F27'  # Orange
    PLAYER_B_COLOR = '#FF00FF'  # Magenta
    BACKGROUND_COLOR = '#007F66'  # Dark green (court color)
    
    def __init__(self, output_dir: str):
        """
        Initialize statistics generator.
        
        Args:
            output_dir: Directory to save generated graphs
        """
        self.output_dir = output_dir
        self.graphs_dir = os.path.join(output_dir, "graphs")
        os.makedirs(self.graphs_dir, exist_ok=True)
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['font.size'] = 12
        plt.rcParams['figure.figsize'] = (10, 6)
    
    def generate_all_stats(self, rallies: List[Dict], 
                          player_a: str, player_b: str) -> Dict:
        """
        Generate all statistics from rally data.
        
        Returns:
            Dictionary containing all computed statistics
        """
        stats = {
            'match_summary': self._generate_match_summary(rallies, player_a, player_b),
            'rally_durations': self._calculate_rally_durations(rallies),
            'shot_distribution': self._calculate_shot_distribution(rallies),
            'shot_distribution_by_player': self._calculate_shot_by_player(rallies),
            'landing_positions': self._calculate_landing_positions(rallies),
            'win_loss_breakdown': self._calculate_win_loss(rallies, player_a, player_b),
            'error_analysis': self._calculate_error_stats(rallies),
            'player_comparison': self._generate_player_comparison(rallies, player_a, player_b),
            'rally_length_stats': self._calculate_rally_length_stats(rallies),
            'momentum_analysis': self._calculate_momentum(rallies, player_a, player_b)
        }
        
        return stats
    
    def generate_all_graphs(self, statistics: Dict) -> List[str]:
        """
        Generate all visualization graphs.
        
        Returns:
            List of paths to generated graph images
        """
        graph_paths = []
        
        # 1. Rally Duration Graph
        path = self.generate_rally_duration_graph(
            statistics.get('rally_durations', [])
        )
        if path:
            graph_paths.append(path)
        
        # 2. Shot Type Distribution
        path = self.generate_shot_distribution_chart(
            statistics.get('shot_distribution', {})
        )
        if path:
            graph_paths.append(path)
        
        # 3. Shot Distribution by Player
        path = self.generate_player_shot_comparison(
            statistics.get('shot_distribution_by_player', {})
        )
        if path:
            graph_paths.append(path)
        
        # 4. Win/Loss Pie Chart
        path = self.generate_win_loss_pie(
            statistics.get('win_loss_breakdown', {})
        )
        if path:
            graph_paths.append(path)
        
        # 5. Error Analysis Chart
        path = self.generate_error_chart(
            statistics.get('error_analysis', {})
        )
        if path:
            graph_paths.append(path)
        
        # 6. Player Comparison Radar
        path = self.generate_player_comparison_radar(
            statistics.get('player_comparison', {})
        )
        if path:
            graph_paths.append(path)
        
        # 7. Rally Length Distribution
        path = self.generate_rally_length_histogram(
            statistics.get('rally_length_stats', {})
        )
        if path:
            graph_paths.append(path)
        
        # 8. Momentum Graph
        path = self.generate_momentum_graph(
            statistics.get('momentum_analysis', {})
        )
        if path:
            graph_paths.append(path)
        
        # 9. Landing Position Heatmaps
        landing_data = statistics.get('landing_positions', {})
        path_a = self.generate_landing_heatmap(
            landing_data.get('player_a', []),
            "Player A Landing Positions",
            "landing_heatmap_a.png"
        )
        path_b = self.generate_landing_heatmap(
            landing_data.get('player_b', []),
            "Player B Landing Positions",
            "landing_heatmap_b.png"
        )
        if path_a:
            graph_paths.append(path_a)
        if path_b:
            graph_paths.append(path_b)
        
        return graph_paths
    
    def _generate_match_summary(self, rallies: List[Dict], 
                               player_a: str, player_b: str) -> Dict:
        """Generate match summary statistics"""
        total_rallies = len(rallies)
        
        if not rallies:
            return {
                'total_rallies': 0,
                'player_a': player_a,
                'player_b': player_b
            }
        
        # Count wins
        a_wins = sum(1 for r in rallies if r.get('winner') == player_a or r.get('winner') == 'Player A')
        b_wins = sum(1 for r in rallies if r.get('winner') == player_b or r.get('winner') == 'Player B')
        
        # Calculate average rally duration
        durations = [r.get('duration', 0) for r in rallies if r.get('duration')]
        avg_duration = np.mean(durations) if durations else 0
        
        # Total shots
        total_shots = sum(len(r.get('shots', [])) for r in rallies)
        
        return {
            'total_rallies': total_rallies,
            'player_a': player_a,
            'player_b': player_b,
            'player_a_wins': a_wins,
            'player_b_wins': b_wins,
            'average_rally_duration': round(avg_duration, 2),
            'total_shots': total_shots,
            'average_shots_per_rally': round(total_shots / total_rallies, 1) if total_rallies else 0
        }
    
    def _calculate_rally_durations(self, rallies: List[Dict]) -> List[Dict]:
        """Calculate duration for each rally"""
        durations = []
        for i, rally in enumerate(rallies):
            durations.append({
                'rally_number': i + 1,
                'duration': rally.get('duration', 0),
                'winner': rally.get('winner', 'Unknown'),
                'shots': len(rally.get('shots', []))
            })
        return durations
    
    def _calculate_shot_distribution(self, rallies: List[Dict]) -> Dict:
        """Calculate overall shot type distribution"""
        shot_counts = {}
        
        for rally in rallies:
            for shot in rally.get('shots', []):
                shot_type = shot.get('shot_type', 'unknown')
                shot_counts[shot_type] = shot_counts.get(shot_type, 0) + 1
        
        total = sum(shot_counts.values())
        
        return {
            'counts': shot_counts,
            'percentages': {k: round(v/total*100, 1) for k, v in shot_counts.items()} if total else {},
            'total': total
        }
    
    def _calculate_shot_by_player(self, rallies: List[Dict]) -> Dict:
        """Calculate shot distribution by player"""
        player_a_shots = {}
        player_b_shots = {}
        
        for rally in rallies:
            for shot in rally.get('shots', []):
                shot_type = shot.get('shot_type', 'unknown')
                player = shot.get('player', 'A')
                
                if player in ['A', 'Player A']:
                    player_a_shots[shot_type] = player_a_shots.get(shot_type, 0) + 1
                else:
                    player_b_shots[shot_type] = player_b_shots.get(shot_type, 0) + 1
        
        return {
            'player_a': player_a_shots,
            'player_b': player_b_shots
        }
    
    def _calculate_landing_positions(self, rallies: List[Dict]) -> Dict:
        """Extract landing positions for heatmap"""
        player_a_landings = []
        player_b_landings = []
        
        for rally in rallies:
            for shot in rally.get('shots', []):
                landing = shot.get('landing', {})
                x = landing.get('x', 0)
                y = landing.get('y', 0)
                player = shot.get('player', 'A')
                
                if x and y:
                    if player in ['A', 'Player A']:
                        player_a_landings.append((x, y))
                    else:
                        player_b_landings.append((x, y))
        
        return {
            'player_a': player_a_landings,
            'player_b': player_b_landings
        }
    
    def _calculate_win_loss(self, rallies: List[Dict], 
                           player_a: str, player_b: str) -> Dict:
        """Calculate win/loss statistics"""
        results = {
            'player_a_name': player_a,
            'player_b_name': player_b,
            'player_a_wins': 0,
            'player_b_wins': 0,
            'by_reason': {
                'net_error': {'a': 0, 'b': 0},
                'out': {'a': 0, 'b': 0},
                'winner': {'a': 0, 'b': 0}
            }
        }
        
        for rally in rallies:
            winner = rally.get('winner', '')
            end_reason = rally.get('end_reason', 'unknown')
            
            if 'A' in winner or player_a in winner:
                results['player_a_wins'] += 1
                # A won, so B made the error or A hit a winner
                if end_reason == 'net':
                    results['by_reason']['net_error']['b'] += 1
                elif end_reason == 'out':
                    results['by_reason']['out']['b'] += 1
                else:
                    results['by_reason']['winner']['a'] += 1
            elif 'B' in winner or player_b in winner:
                results['player_b_wins'] += 1
                if end_reason == 'net':
                    results['by_reason']['net_error']['a'] += 1
                elif end_reason == 'out':
                    results['by_reason']['out']['a'] += 1
                else:
                    results['by_reason']['winner']['b'] += 1
        
        return results
    
    def _calculate_error_stats(self, rallies: List[Dict]) -> Dict:
        """Calculate error statistics"""
        errors = {
            'player_a': {'net': 0, 'out': 0, 'tactical': 0},
            'player_b': {'net': 0, 'out': 0, 'tactical': 0}
        }
        
        for rally in rallies:
            for mistake in rally.get('mistakes', []):
                player = mistake.get('player', '')
                mistake_type = mistake.get('mistake_type', '')
                
                key = 'player_a' if 'A' in player else 'player_b'
                
                if 'net' in mistake_type:
                    errors[key]['net'] += 1
                elif 'out' in mistake_type:
                    errors[key]['out'] += 1
                else:
                    errors[key]['tactical'] += 1
        
        return errors
    
    def _generate_player_comparison(self, rallies: List[Dict],
                                   player_a: str, player_b: str) -> Dict:
        """Generate metrics for player comparison radar chart"""
        metrics = {
            'player_a': {
                'name': player_a,
                'attack': 0,
                'defense': 0,
                'net_play': 0,
                'consistency': 0,
                'power': 0
            },
            'player_b': {
                'name': player_b,
                'attack': 0,
                'defense': 0,
                'net_play': 0,
                'consistency': 0,
                'power': 0
            }
        }
        
        # Calculate based on shot types
        attack_shots = ['smash', 'wrist_smash', 'rush', 'drop']
        defense_shots = ['lob', 'defensive_lob', 'defensive_drive']
        net_shots = ['net_shot', 'return_net', 'cross_court_net', 'push']
        power_shots = ['smash', 'clear', 'drive']
        
        a_shots = []
        b_shots = []
        
        for rally in rallies:
            for shot in rally.get('shots', []):
                player = shot.get('player', 'A')
                if 'A' in player:
                    a_shots.append(shot.get('shot_type', ''))
                else:
                    b_shots.append(shot.get('shot_type', ''))
        
        # Calculate percentages (normalized to 0-100)
        def calc_percentage(shots, target_types):
            if not shots:
                return 50
            count = sum(1 for s in shots if s in target_types)
            return min(100, int((count / len(shots)) * 300 + 30))
        
        metrics['player_a']['attack'] = calc_percentage(a_shots, attack_shots)
        metrics['player_a']['defense'] = calc_percentage(a_shots, defense_shots)
        metrics['player_a']['net_play'] = calc_percentage(a_shots, net_shots)
        metrics['player_a']['power'] = calc_percentage(a_shots, power_shots)
        metrics['player_a']['consistency'] = 100 - len([r for r in rallies if 'A' in r.get('winner', '')]) * 2
        
        metrics['player_b']['attack'] = calc_percentage(b_shots, attack_shots)
        metrics['player_b']['defense'] = calc_percentage(b_shots, defense_shots)
        metrics['player_b']['net_play'] = calc_percentage(b_shots, net_shots)
        metrics['player_b']['power'] = calc_percentage(b_shots, power_shots)
        metrics['player_b']['consistency'] = 100 - len([r for r in rallies if 'B' in r.get('winner', '')]) * 2
        
        return metrics
    
    def _calculate_rally_length_stats(self, rallies: List[Dict]) -> Dict:
        """Calculate rally length statistics"""
        shot_counts = [len(r.get('shots', [])) for r in rallies]
        
        if not shot_counts:
            return {'bins': [], 'counts': []}
        
        return {
            'shot_counts': shot_counts,
            'min': min(shot_counts),
            'max': max(shot_counts),
            'average': round(np.mean(shot_counts), 1),
            'median': int(np.median(shot_counts))
        }
    
    def _calculate_momentum(self, rallies: List[Dict],
                           player_a: str, player_b: str) -> Dict:
        """Calculate momentum throughout the match"""
        momentum = []
        a_score = 0
        b_score = 0
        
        for i, rally in enumerate(rallies):
            winner = rally.get('winner', '')
            if 'A' in winner or player_a in winner:
                a_score += 1
            else:
                b_score += 1
            
            momentum.append({
                'rally': i + 1,
                'score_a': a_score,
                'score_b': b_score,
                'diff': a_score - b_score  # Positive favors A
            })
        
        return {
            'data': momentum,
            'final_a': a_score,
            'final_b': b_score
        }
    
    # Graph Generation Methods
    
    def generate_rally_duration_graph(self, durations: List[Dict]) -> Optional[str]:
        """Generate rally duration bar chart"""
        if not durations:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 5))
        
        rally_nums = [d['rally_number'] for d in durations]
        duration_vals = [d['duration'] for d in durations]
        colors = [self.PLAYER_A_COLOR if 'A' in d.get('winner', '') else self.PLAYER_B_COLOR 
                  for d in durations]
        
        bars = ax.bar(rally_nums, duration_vals, color=colors, alpha=0.7)
        
        ax.set_xlabel('Rally Number')
        ax.set_ylabel('Duration (seconds)')
        ax.set_title('Rally Duration Analysis')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.PLAYER_A_COLOR, alpha=0.7, label='Player A Won'),
            Patch(facecolor=self.PLAYER_B_COLOR, alpha=0.7, label='Player B Won')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Add average line
        avg_duration = np.mean(duration_vals)
        ax.axhline(y=avg_duration, color='red', linestyle='--', 
                   label=f'Average: {avg_duration:.1f}s')
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'rally_duration.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_shot_distribution_chart(self, shot_dist: Dict) -> Optional[str]:
        """Generate shot type distribution bar chart"""
        counts = shot_dist.get('counts', {})
        if not counts:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        shot_types = list(counts.keys())
        values = list(counts.values())
        
        # Sort by frequency
        sorted_pairs = sorted(zip(shot_types, values), key=lambda x: x[1], reverse=True)
        shot_types, values = zip(*sorted_pairs)
        
        bars = ax.bar(range(len(shot_types)), values, color='steelblue', alpha=0.8)
        
        ax.set_xlabel('Shot Type')
        ax.set_ylabel('Count')
        ax.set_title('Shot Type Distribution')
        ax.set_xticks(range(len(shot_types)))
        ax.set_xticklabels(shot_types, rotation=45, ha='right')
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   str(val), ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'shot_distribution.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_player_shot_comparison(self, shot_by_player: Dict) -> Optional[str]:
        """Generate player shot comparison grouped bar chart"""
        a_shots = shot_by_player.get('player_a', {})
        b_shots = shot_by_player.get('player_b', {})
        
        if not a_shots and not b_shots:
            return None
        
        # Get all shot types
        all_types = sorted(set(list(a_shots.keys()) + list(b_shots.keys())))
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        x = np.arange(len(all_types))
        width = 0.35
        
        a_vals = [a_shots.get(t, 0) for t in all_types]
        b_vals = [b_shots.get(t, 0) for t in all_types]
        
        bars_a = ax.bar(x - width/2, a_vals, width, label='Player A', 
                        color=self.PLAYER_A_COLOR, alpha=0.8)
        bars_b = ax.bar(x + width/2, b_vals, width, label='Player B',
                        color=self.PLAYER_B_COLOR, alpha=0.8)
        
        ax.set_xlabel('Shot Type')
        ax.set_ylabel('Count')
        ax.set_title('Shot Distribution by Player')
        ax.set_xticks(x)
        ax.set_xticklabels(all_types, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'player_shot_comparison.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_win_loss_pie(self, win_loss: Dict) -> Optional[str]:
        """Generate win/loss pie chart"""
        a_wins = win_loss.get('player_a_wins', 0)
        b_wins = win_loss.get('player_b_wins', 0)
        
        if a_wins == 0 and b_wins == 0:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Overall wins
        labels = [f"Player A ({a_wins})", f"Player B ({b_wins})"]
        sizes = [a_wins, b_wins]
        colors = [self.PLAYER_A_COLOR, self.PLAYER_B_COLOR]
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, explode=(0.05, 0))
        ax1.set_title('Rally Wins Distribution')
        
        # By reason
        by_reason = win_loss.get('by_reason', {})
        reasons = []
        values = []
        
        for reason, data in by_reason.items():
            if data.get('a', 0) + data.get('b', 0) > 0:
                reasons.append(f"{reason} (A)")
                values.append(data.get('a', 0))
                reasons.append(f"{reason} (B)")
                values.append(data.get('b', 0))
        
        if values:
            ax2.bar(range(len(reasons)), values, color='steelblue', alpha=0.7)
            ax2.set_xticks(range(len(reasons)))
            ax2.set_xticklabels(reasons, rotation=45, ha='right')
            ax2.set_ylabel('Count')
            ax2.set_title('Points by Reason')
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'win_loss_breakdown.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_error_chart(self, error_stats: Dict) -> Optional[str]:
        """Generate error analysis chart"""
        a_errors = error_stats.get('player_a', {})
        b_errors = error_stats.get('player_b', {})
        
        if not a_errors and not b_errors:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = ['Net Errors', 'Out Errors', 'Tactical Errors']
        a_vals = [a_errors.get('net', 0), a_errors.get('out', 0), a_errors.get('tactical', 0)]
        b_vals = [b_errors.get('net', 0), b_errors.get('out', 0), b_errors.get('tactical', 0)]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax.bar(x - width/2, a_vals, width, label='Player A', color=self.PLAYER_A_COLOR)
        ax.bar(x + width/2, b_vals, width, label='Player B', color=self.PLAYER_B_COLOR)
        
        ax.set_xlabel('Error Type')
        ax.set_ylabel('Count')
        ax.set_title('Error Analysis by Player')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'error_analysis.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_player_comparison_radar(self, comparison: Dict) -> Optional[str]:
        """Generate player comparison radar chart"""
        a_metrics = comparison.get('player_a', {})
        b_metrics = comparison.get('player_b', {})
        
        if not a_metrics or not b_metrics:
            return None
        
        categories = ['Attack', 'Defense', 'Net Play', 'Consistency', 'Power']
        
        a_vals = [
            a_metrics.get('attack', 50),
            a_metrics.get('defense', 50),
            a_metrics.get('net_play', 50),
            a_metrics.get('consistency', 50),
            a_metrics.get('power', 50)
        ]
        
        b_vals = [
            b_metrics.get('attack', 50),
            b_metrics.get('defense', 50),
            b_metrics.get('net_play', 50),
            b_metrics.get('consistency', 50),
            b_metrics.get('power', 50)
        ]
        
        # Radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        
        # Complete the loop
        a_vals += a_vals[:1]
        b_vals += b_vals[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        ax.plot(angles, a_vals, 'o-', linewidth=2, label='Player A', 
                color=self.PLAYER_A_COLOR)
        ax.fill(angles, a_vals, alpha=0.25, color=self.PLAYER_A_COLOR)
        
        ax.plot(angles, b_vals, 'o-', linewidth=2, label='Player B',
                color=self.PLAYER_B_COLOR)
        ax.fill(angles, b_vals, alpha=0.25, color=self.PLAYER_B_COLOR)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('Player Comparison', size=14, y=1.1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'player_comparison_radar.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_rally_length_histogram(self, rally_stats: Dict) -> Optional[str]:
        """Generate rally length distribution histogram"""
        shot_counts = rally_stats.get('shot_counts', [])
        
        if not shot_counts:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(shot_counts, bins=range(0, max(shot_counts) + 3, 2),
                color='steelblue', alpha=0.7, edgecolor='black')
        
        ax.axvline(x=rally_stats.get('average', 0), color='red', 
                   linestyle='--', label=f"Average: {rally_stats.get('average', 0)}")
        ax.axvline(x=rally_stats.get('median', 0), color='green',
                   linestyle='--', label=f"Median: {rally_stats.get('median', 0)}")
        
        ax.set_xlabel('Number of Shots per Rally')
        ax.set_ylabel('Frequency')
        ax.set_title('Rally Length Distribution')
        ax.legend()
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'rally_length_histogram.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_momentum_graph(self, momentum: Dict) -> Optional[str]:
        """Generate match momentum graph"""
        data = momentum.get('data', [])
        
        if not data:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 5))
        
        rallies = [d['rally'] for d in data]
        diffs = [d['diff'] for d in data]
        
        # Color based on who's leading
        colors = [self.PLAYER_A_COLOR if d >= 0 else self.PLAYER_B_COLOR for d in diffs]
        
        ax.bar(rallies, diffs, color=colors, alpha=0.7)
        ax.axhline(y=0, color='black', linewidth=1)
        
        ax.set_xlabel('Rally Number')
        ax.set_ylabel('Score Difference (A - B)')
        ax.set_title('Match Momentum')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.PLAYER_A_COLOR, alpha=0.7, label='Player A Leading'),
            Patch(facecolor=self.PLAYER_B_COLOR, alpha=0.7, label='Player B Leading')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, 'momentum_graph.png')
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def generate_landing_heatmap(self, positions: List[Tuple], 
                                 title: str, filename: str) -> Optional[str]:
        """Generate landing position heatmap"""
        if not positions:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 12))
        
        # Set court background
        ax.set_facecolor(self.BACKGROUND_COLOR)
        
        # Draw court lines
        self._draw_court(ax)
        
        # Extract x, y coordinates
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        # Create heatmap using hexbin
        hb = ax.hexbin(x_coords, y_coords, gridsize=15, cmap='YlOrRd',
                       mincnt=1, alpha=0.7)
        
        # Also plot individual points
        ax.scatter(x_coords, y_coords, c='blue', s=20, alpha=0.3)
        
        ax.set_xlim(0, self.COURT_WIDTH)
        ax.set_ylim(0, self.COURT_LENGTH)
        ax.set_title(title)
        ax.set_aspect('equal')
        
        plt.colorbar(hb, ax=ax, label='Shot Count')
        plt.tight_layout()
        
        path = os.path.join(self.graphs_dir, filename)
        plt.savefig(path, dpi=120, bbox_inches='tight')
        plt.close()
        
        return path
    
    def _draw_court(self, ax):
        """Draw badminton court lines"""
        # Outer boundary
        ax.add_patch(patches.Rectangle((0, 0), self.COURT_WIDTH, self.COURT_LENGTH,
                                       fill=False, edgecolor='white', linewidth=2))
        
        # Net line
        ax.axhline(y=self.HALF_COURT_LENGTH, color='white', linewidth=2)
        
        # Service lines
        service_line = 195  # 1.95m from net
        ax.axhline(y=self.HALF_COURT_LENGTH - service_line, color='white', linewidth=1)
        ax.axhline(y=self.HALF_COURT_LENGTH + service_line, color='white', linewidth=1)
        
        # Center line
        center_x = self.COURT_WIDTH / 2
        ax.axvline(x=center_x, color='white', linewidth=1, 
                   ymin=0, ymax=service_line/self.COURT_LENGTH)
        ax.axvline(x=center_x, color='white', linewidth=1,
                   ymin=1-service_line/self.COURT_LENGTH, ymax=1)
