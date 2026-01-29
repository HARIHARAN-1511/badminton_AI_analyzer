"""
Player Comparison Module
Provides side-by-side analysis of both players for each rally.
Generates weaknesses, mistakes, and improvement suggestions.
"""

from typing import Dict, List, Optional, Tuple
import random

class PlayerComparison:
    """
    Generates side-by-side player comparisons for rallies.
    Analyzes mistakes, weaknesses, and provides improvement suggestions.
    """
    
    # Weakness categories and their indicators
    WEAKNESS_INDICATORS = {
        'net_play': {
            'shot_types': ['net_shot', 'return_net', 'cross_court_net'],
            'mistakes': ['net_error'],
            'description': 'Net Play',
            'improvements': [
                'Practice net kill drills to improve reactions',
                'Work on soft hands for better touch at the net',
                'Focus on racket preparation before net shots',
                'Develop deceptive net shot techniques'
            ]
        },
        'defense': {
            'shot_types': ['lob', 'defensive_lob', 'defensive_drive'],
            'mistakes': ['missed_return', 'weak_return'],
            'description': 'Defensive Skills',
            'improvements': [
                'Improve footwork for better court coverage',
                'Practice defensive lifts from difficult positions',
                'Work on reaction speed with multi-shuttle drills',
                'Develop stronger core for recovery shots'
            ]
        },
        'power': {
            'shot_types': ['smash', 'wrist_smash', 'clear'],
            'mistakes': ['out_long', 'out_wide'],
            'description': 'Power Control',
            'improvements': [
                'Focus on timing rather than raw power',
                'Work on follow-through consistency',
                'Practice power shots with specific targets',
                'Develop better body rotation technique'
            ]
        },
        'accuracy': {
            'shot_types': ['drop', 'push'],
            'mistakes': ['out_long', 'out_wide', 'net_error'],
            'description': 'Shot Accuracy',
            'improvements': [
                'Use target practice for precision training',
                'Focus on consistent contact point',
                'Develop better depth perception',
                'Practice shots at different speeds with same accuracy'
            ]
        },
        'positioning': {
            'shot_types': [],
            'mistakes': ['poor_positioning', 'missed_return'],
            'description': 'Court Positioning',
            'improvements': [
                'Return to base position after each shot',
                'Anticipate opponent\'s shots better',
                'Work on split-step timing',
                'Study opponent patterns to predict shots'
            ]
        },
        'tactics': {
            'shot_types': [],
            'mistakes': ['poor_shot_selection', 'predictable_pattern'],
            'description': 'Tactical Awareness',
            'improvements': [
                'Vary shot selection to be unpredictable',
                'Read opponent\'s body language',
                'Develop match strategy before playing',
                'Analyze opponent weaknesses during play'
            ]
        }
    }
    
    # Better shot recommendations
    BETTER_SHOT_RECOMMENDATIONS = {
        'smash_after_lob': {
            'situation': 'After receiving a high lob',
            'weak_choice': 'Another lob',
            'better_choice': 'Smash or drop shot',
            'reason': 'Take the offensive opportunity instead of neutralizing'
        },
        'net_after_drop': {
            'situation': 'After opponent plays a drop',
            'weak_choice': 'High clear',
            'better_choice': 'Tight net shot or push',
            'reason': 'Keep pressure on the net rather than giving opponent time'
        },
        'cross_court_under_pressure': {
            'situation': 'When under pressure from smash',
            'weak_choice': 'Weak straight return',
            'better_choice': 'Cross-court lift or block',
            'reason': 'Cross-court gives more time to recover position'
        }
    }
    
    def __init__(self):
        """Initialize the player comparison module."""
        pass
    
    def compare_players_for_rally(self, rally: Dict, 
                                  player_a_name: str = "Player A",
                                  player_b_name: str = "Player B") -> Dict:
        """
        Generate side-by-side comparison of both players for a rally.
        
        Args:
            rally: Rally data with shots, mistakes, winner, etc.
            player_a_name: Name of player A
            player_b_name: Name of player B
            
        Returns:
            Dictionary with comparison data for both players
        """
        shots = rally.get('shots', [])
        mistakes = rally.get('mistakes', [])
        winner = rally.get('winner', 'Player A')
        
        # Separate data by player
        player_a_shots = [s for s in shots if 'A' in s.get('player', '')]
        player_b_shots = [s for s in shots if 'B' in s.get('player', '')]
        
        player_a_mistakes = [m for m in mistakes if 'A' in m.get('player', '')]
        player_b_mistakes = [m for m in mistakes if 'B' in m.get('player', '')]
        
        return {
            'rally_number': rally.get('rally_number', 1),
            'winner': winner,
            'player_a': {
                'name': player_a_name,
                'shots_played': len(player_a_shots),
                'shot_types': self._count_shot_types(player_a_shots),
                'mistakes': player_a_mistakes,
                'mistakes_count': len(player_a_mistakes),
                'weaknesses': self._identify_weaknesses(player_a_shots, player_a_mistakes),
                'improvements': self._generate_improvements(player_a_shots, player_a_mistakes),
                'better_choices': self._suggest_better_choices(player_a_shots, rally),
                'performance_score': self._calculate_performance_score(
                    player_a_shots, player_a_mistakes, 'A' in winner
                )
            },
            'player_b': {
                'name': player_b_name,
                'shots_played': len(player_b_shots),
                'shot_types': self._count_shot_types(player_b_shots),
                'mistakes': player_b_mistakes,
                'mistakes_count': len(player_b_mistakes),
                'weaknesses': self._identify_weaknesses(player_b_shots, player_b_mistakes),
                'improvements': self._generate_improvements(player_b_shots, player_b_mistakes),
                'better_choices': self._suggest_better_choices(player_b_shots, rally),
                'performance_score': self._calculate_performance_score(
                    player_b_shots, player_b_mistakes, 'B' in winner
                )
            },
            'comparison_summary': self._generate_comparison_summary(
                player_a_shots, player_b_shots, 
                player_a_mistakes, player_b_mistakes,
                winner, player_a_name, player_b_name
            )
        }
    
    def _count_shot_types(self, shots: List[Dict]) -> Dict[str, int]:
        """Count shot types played by a player."""
        counts = {}
        for shot in shots:
            shot_type = shot.get('shot_type', 'unknown')
            counts[shot_type] = counts.get(shot_type, 0) + 1
        return counts
    
    def _identify_weaknesses(self, shots: List[Dict], 
                            mistakes: List[Dict]) -> List[Dict]:
        """Identify weaknesses based on shots and mistakes."""
        weaknesses = []
        
        for weakness_key, indicators in self.WEAKNESS_INDICATORS.items():
            weakness_score = 0
            
            # Check mistakes
            for mistake in mistakes:
                if mistake.get('mistake_type') in indicators['mistakes']:
                    weakness_score += 2
            
            # Check if player avoided certain shot types (might indicate weakness)
            shot_types = [s.get('shot_type') for s in shots]
            for weak_shot in indicators['shot_types']:
                if weak_shot not in shot_types and len(shots) > 3:
                    weakness_score += 0.5
            
            if weakness_score > 0:
                weaknesses.append({
                    'area': indicators['description'],
                    'severity': 'high' if weakness_score >= 3 else 'medium' if weakness_score >= 1 else 'low',
                    'score': weakness_score,
                    'indicators': [m.get('description') for m in mistakes if m.get('mistake_type') in indicators['mistakes']]
                })
        
        # Sort by severity
        weaknesses.sort(key=lambda x: x['score'], reverse=True)
        return weaknesses[:3]  # Top 3 weaknesses
    
    def _generate_improvements(self, shots: List[Dict], 
                               mistakes: List[Dict]) -> List[str]:
        """Generate improvement suggestions based on weaknesses."""
        improvements = []
        
        for mistake in mistakes:
            mistake_type = mistake.get('mistake_type', '')
            
            for weakness_key, indicators in self.WEAKNESS_INDICATORS.items():
                if mistake_type in indicators['mistakes']:
                    improvement = random.choice(indicators['improvements'])
                    if improvement not in improvements:
                        improvements.append(improvement)
        
        # If no specific improvements, add general ones
        if not improvements:
            improvements = [
                'Maintain consistent footwork throughout rallies',
                'Focus on shot placement rather than power',
                'Work on physical conditioning for longer rallies'
            ]
        
        return improvements[:4]  # Max 4 suggestions
    
    def _suggest_better_choices(self, player_shots: List[Dict], 
                                rally: Dict) -> List[Dict]:
        """Suggest better shot choices the player could have made."""
        suggestions = []
        all_shots = rally.get('shots', [])
        
        for i, shot in enumerate(player_shots):
            shot_type = shot.get('shot_type', '')
            
            # Find this shot in full rally
            shot_index = None
            for j, s in enumerate(all_shots):
                if s.get('frame') == shot.get('frame'):
                    shot_index = j
                    break
            
            if shot_index is None or shot_index == 0:
                continue
            
            prev_shot = all_shots[shot_index - 1]
            prev_type = prev_shot.get('shot_type', '')
            
            # Check for suboptimal choices
            if prev_type == 'lob' and shot_type == 'lob':
                suggestions.append({
                    'shot_number': shot.get('shot_number', i+1),
                    'time': shot.get('time', 0),
                    'played': shot_type,
                    'recommended': 'smash or drop',
                    'reason': 'After receiving a lob, attack with smash or drop instead of lifting again'
                })
            
            if prev_type == 'smash' and shot_type in ['net_shot', 'drop']:
                suggestions.append({
                    'shot_number': shot.get('shot_number', i+1),
                    'time': shot.get('time', 0),
                    'played': shot_type,
                    'recommended': 'defensive lob or block',
                    'reason': 'Under smash pressure, prioritize defense over counter-attack'
                })
        
        return suggestions[:3]  # Max 3 suggestions
    
    def _calculate_performance_score(self, shots: List[Dict], 
                                     mistakes: List[Dict], 
                                     won: bool) -> int:
        """Calculate a performance score (0-100) for the rally."""
        score = 50  # Base score
        
        # Winning adds points
        if won:
            score += 20
        
        # Each shot adds small points (active play)
        score += min(len(shots) * 2, 20)
        
        # Attacking shots add points
        attack_shots = sum(1 for s in shots if s.get('shot_type') in ['smash', 'drop', 'rush', 'push'])
        score += min(attack_shots * 3, 15)
        
        # Mistakes subtract points
        score -= len(mistakes) * 10
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def _generate_comparison_summary(self, a_shots: List, b_shots: List,
                                     a_mistakes: List, b_mistakes: List,
                                     winner: str, a_name: str, b_name: str) -> str:
        """Generate a textual summary comparing both players."""
        parts = []
        
        # Shot volume comparison
        if len(a_shots) > len(b_shots) + 2:
            parts.append(f"{a_name} was more active, playing {len(a_shots)} shots compared to {b_name}'s {len(b_shots)}.")
        elif len(b_shots) > len(a_shots) + 2:
            parts.append(f"{b_name} was more involved, playing {len(b_shots)} shots compared to {a_name}'s {len(a_shots)}.")
        
        # Attack comparison
        a_attacks = sum(1 for s in a_shots if s.get('shot_type') in ['smash', 'drop', 'rush'])
        b_attacks = sum(1 for s in b_shots if s.get('shot_type') in ['smash', 'drop', 'rush'])
        
        if a_attacks > b_attacks:
            parts.append(f"{a_name} showed more aggression with {a_attacks} attacking shots.")
        elif b_attacks > a_attacks:
            parts.append(f"{b_name} was more attacking with {b_attacks} offensive shots.")
        
        # Mistake comparison
        if len(a_mistakes) > len(b_mistakes):
            parts.append(f"{a_name} struggled more with {len(a_mistakes)} mistakes.")
        elif len(b_mistakes) > len(a_mistakes):
            parts.append(f"{b_name} had more difficulty with {len(b_mistakes)} mistakes.")
        
        # Winner statement
        winner_name = a_name if 'A' in winner else b_name
        parts.append(f"{winner_name} won this rally.")
        
        return " ".join(parts) if parts else f"{winner} won the rally in a balanced exchange."
    
    def get_match_comparison(self, rallies: List[Dict],
                            player_a_name: str = "Player A",
                            player_b_name: str = "Player B") -> Dict:
        """
        Generate overall match comparison between two players.
        
        Returns aggregated statistics and analysis.
        """
        total_a_shots = 0
        total_b_shots = 0
        total_a_mistakes = 0
        total_b_mistakes = 0
        a_wins = 0
        b_wins = 0
        a_scores = []
        b_scores = []
        all_a_weaknesses = {}
        all_b_weaknesses = {}
        
        for rally in rallies:
            comparison = self.compare_players_for_rally(rally, player_a_name, player_b_name)
            
            total_a_shots += comparison['player_a']['shots_played']
            total_b_shots += comparison['player_b']['shots_played']
            total_a_mistakes += comparison['player_a']['mistakes_count']
            total_b_mistakes += comparison['player_b']['mistakes_count']
            
            a_scores.append(comparison['player_a']['performance_score'])
            b_scores.append(comparison['player_b']['performance_score'])
            
            winner = rally.get('winner', '')
            if 'A' in winner:
                a_wins += 1
            else:
                b_wins += 1
            
            # Aggregate weaknesses
            for w in comparison['player_a']['weaknesses']:
                area = w['area']
                all_a_weaknesses[area] = all_a_weaknesses.get(area, 0) + w['score']
            
            for w in comparison['player_b']['weaknesses']:
                area = w['area']
                all_b_weaknesses[area] = all_b_weaknesses.get(area, 0) + w['score']
        
        return {
            'player_a': {
                'name': player_a_name,
                'rallies_won': a_wins,
                'total_shots': total_a_shots,
                'total_mistakes': total_a_mistakes,
                'average_score': sum(a_scores) / len(a_scores) if a_scores else 50,
                'main_weaknesses': sorted(all_a_weaknesses.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            'player_b': {
                'name': player_b_name,
                'rallies_won': b_wins,
                'total_shots': total_b_shots,
                'total_mistakes': total_b_mistakes,
                'average_score': sum(b_scores) / len(b_scores) if b_scores else 50,
                'main_weaknesses': sorted(all_b_weaknesses.items(), key=lambda x: x[1], reverse=True)[:3]
            },
            'total_rallies': len(rallies)
        }
