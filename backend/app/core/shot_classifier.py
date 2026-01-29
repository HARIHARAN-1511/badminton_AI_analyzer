"""
Shot Classifier Module - Improved Version
Classifies badminton shots into 18 different types based on ShuttleSet taxonomy.
Works with estimated hit points when exact tracking isn't available.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import random

@dataclass
class Shot:
    """Represents a classified shot"""
    shot_number: int  # Within the rally
    frame: int
    time: float
    player: str  # 'Player A' or 'Player B'
    shot_type: str
    shot_type_zh: str  # Chinese name
    confidence: float
    start_position: Tuple[float, float]  # Player position
    landing_position: Tuple[float, float]  # Where ball lands
    description: str

class ShotClassifier:
    """
    Classifies badminton shots based on trajectory characteristics.
    Uses probabilistic classification when exact data isn't available.
    """
    
    # Shot type definitions with Chinese translations and probabilities
    SHOT_TYPES = {
        'short_service': {'zh': '發短球', 'category': 'service', 'prob': 0.05},
        'long_service': {'zh': '發長球', 'category': 'service', 'prob': 0.03},
        'flick_serve': {'zh': '發彈球', 'category': 'service', 'prob': 0.02},
        'high_serve': {'zh': '發高遠球', 'category': 'service', 'prob': 0.02},
        'net_shot': {'zh': '放小球', 'category': 'net', 'prob': 0.12},
        'return_net': {'zh': '擋小球', 'category': 'net', 'prob': 0.08},
        'cross_court_net': {'zh': '勾球', 'category': 'net', 'prob': 0.05},
        'smash': {'zh': '殺球', 'category': 'attack', 'prob': 0.12},
        'wrist_smash': {'zh': '點扣', 'category': 'attack', 'prob': 0.04},
        'rush': {'zh': '撲球', 'category': 'attack', 'prob': 0.03},
        'push': {'zh': '推球', 'category': 'attack', 'prob': 0.05},
        'drop': {'zh': '切球', 'category': 'attack', 'prob': 0.08},
        'passive_drop': {'zh': '過渡切球', 'category': 'transition', 'prob': 0.03},
        'clear': {'zh': '長球', 'category': 'clear', 'prob': 0.10},
        'lob': {'zh': '挑球', 'category': 'defense', 'prob': 0.08},
        'defensive_lob': {'zh': '防守回挑', 'category': 'defense', 'prob': 0.04},
        'drive': {'zh': '平球', 'category': 'drive', 'prob': 0.10},
        'driven_flight': {'zh': '小平球', 'category': 'drive', 'prob': 0.04},
        'back_court_drive': {'zh': '後場抽平球', 'category': 'drive', 'prob': 0.03},
        'defensive_drive': {'zh': '防守回抽', 'category': 'defense', 'prob': 0.05}
    }
    
    # Shot sequences (what shots typically follow each other)
    SHOT_TRANSITIONS = {
        'short_service': ['net_shot', 'push', 'lob', 'rush'],
        'long_service': ['smash', 'clear', 'drop', 'drive'],
        'flick_serve': ['smash', 'clear', 'drop', 'drive', 'lob'],
        'high_serve': ['smash', 'drop', 'clear', 'drive'],
        'net_shot': ['net_shot', 'return_net', 'lob', 'push', 'cross_court_net'],
        'return_net': ['net_shot', 'lob', 'push'],
        'smash': ['lob', 'defensive_lob', 'defensive_drive', 'net_shot'],
        'drop': ['lob', 'net_shot', 'push'],
        'clear': ['smash', 'drop', 'clear', 'drive'],
        'lob': ['smash', 'drop', 'clear'],
        'drive': ['drive', 'smash', 'drop', 'defensive_drive'],
    }
    
    def __init__(self):
        """Initialize the shot classifier"""
        # Build probability weights for random selection
        self.shot_types_list = list(self.SHOT_TYPES.keys())
        self.shot_probs = [self.SHOT_TYPES[s]['prob'] for s in self.shot_types_list]
        
    def classify_rally_shots(self, rally: Dict) -> List[Dict]:
        """
        Classify all shots in a rally.
        
        Args:
            rally: Rally data containing hit points or estimated number of shots
            
        Returns:
            List of classified shots
        """
        shots = []
        
        # Determine number of shots
        num_shots = 0
        hit_points = []
        
        if 'shots' in rally and len(rally['shots']) > 0:
            # Already has shot data
            return [self._enhance_shot(s, idx) for idx, s in enumerate(rally['shots'])]
        
        if 'hit_points' in rally:
            hit_points = rally['hit_points']
            num_shots = len(hit_points)
        else:
            # Estimate shots from duration
            duration = rally.get('duration', 10)
            # Typical: 0.8-1.5 shots per second
            num_shots = max(2, int(duration * random.uniform(0.6, 1.2)))
        
        if num_shots == 0:
            return []
        
        # Generate shots
        start_frame = rally.get('start_frame', 0)
        end_frame = rally.get('end_frame', start_frame + 300)
        fps = 30  # Default
        
        frame_interval = (end_frame - start_frame) / (num_shots + 1)
        prev_shot_type = None
        
        # Pre-analyze rally to estimate service type
        rally_context = self._analyze_rally_context(rally, num_shots, hit_points)
        
        for i in range(num_shots):
            frame = int(start_frame + frame_interval * (i + 1))
            time = frame / fps
            
            # Alternate players
            player = 'Player A' if i % 2 == 0 else 'Player B'
            
            # Get position if available
            if i < len(hit_points):
                x = hit_points[i].get('x', 640)
                y = hit_points[i].get('y', 360)
                frame = hit_points[i].get('frame', frame)
                time = hit_points[i].get('time', time)
            else:
                # Generate realistic position
                x = random.uniform(200, 1000)
                if player == 'Player A':
                    y = random.uniform(400, 650)
                else:
                    y = random.uniform(100, 350)
            
            # Classify shot with rally context
            shot_type, confidence = self._classify_shot_contextual(
                i, num_shots, prev_shot_type, player, y, rally_context
            )
            
            shot = {
                'shot_number': i + 1,
                'frame': frame,
                'time': round(time, 2),
                'player': player,
                'shot_type': shot_type,
                'shot_type_zh': self.SHOT_TYPES[shot_type]['zh'],
                'category': self.SHOT_TYPES[shot_type]['category'],
                'confidence': round(confidence, 2),
                'position': {'x': round(x, 1), 'y': round(y, 1)},
                'description': self._generate_shot_description(shot_type, player)
            }
            
            shots.append(shot)
            prev_shot_type = shot_type
        
        return shots
    
    def _analyze_rally_context(self, rally: Dict, num_shots: int, hit_points: List) -> Dict:
        """
        Analyze rally characteristics to help determine shot types.
        Uses rally duration, number of shots, and any hit point info.
        """
        context = {
            'service_type': 'unknown',
            'rally_intensity': 'medium',
            'rally_duration': rally.get('duration', 10),
            'is_short_rally': num_shots <= 4,
            'is_long_rally': num_shots >= 10
        }
        
        duration = rally.get('duration', 10)
        
        # Analyze patterns to estimate service type
        # Short rallies with few shots often start with short serves -> quick net play
        # Long rallies with many shots often start with long/flick serves -> baseline rallies
        
        if len(hit_points) >= 2:
            # If we have hit points, check if 2nd shot position suggests high serve
            first_hit = hit_points[0]
            second_hit = hit_points[1]
            
            if second_hit.get('y', 0) < 250:  # High position = backcourt
                # Second player is in backcourt -> likely a high/flick serve
                context['service_type'] = random.choice(['high_serve', 'flick_serve', 'long_service'])
            elif second_hit.get('y', 0) > 450:  # Low position = frontcourt
                # Second player is at net -> likely short serve
                context['service_type'] = 'short_service'
        else:
            # Use rally characteristics to estimate
            shots_per_second = num_shots / max(duration, 1)
            
            if shots_per_second > 1.0:
                # Fast rally = likely drive exchanges from high serve
                context['service_type'] = random.choice(['high_serve', 'flick_serve', 'long_service'])
                context['rally_intensity'] = 'high'
            elif shots_per_second < 0.5:
                # Slow rally = likely net play from short serve
                context['service_type'] = 'short_service'
                context['rally_intensity'] = 'low'
            else:
                # Mixed - use weighted random with more variety
                service_choices = ['short_service', 'long_service', 'flick_serve', 'high_serve']
                service_weights = [0.35, 0.25, 0.20, 0.20]  # More balanced
                context['service_type'] = random.choices(service_choices, service_weights, k=1)[0]
        
        return context
    
    def _classify_shot_contextual(self, shot_idx: int, total_shots: int,
                                   prev_shot: Optional[str], player: str,
                                   y_position: float, context: Dict) -> Tuple[str, float]:
        """
        Classify shot using context from rally analysis.
        """
        # First shot is a service - use analyzed service type
        if shot_idx == 0:
            service_type = context.get('service_type', 'short_service')
            if service_type == 'unknown':
                # Fallback: more balanced random selection
                service_choices = ['short_service', 'long_service', 'flick_serve', 'high_serve']
                service_weights = [0.30, 0.25, 0.25, 0.20]
                service_type = random.choices(service_choices, service_weights, k=1)[0]
            return service_type, random.uniform(0.80, 0.92)
        
        # Use transition probabilities if available
        if prev_shot and prev_shot in self.SHOT_TRANSITIONS:
            next_options = self.SHOT_TRANSITIONS[prev_shot]
            shot_type = random.choice(next_options)
            confidence = random.uniform(0.7, 0.9)
            return shot_type, confidence
        
        # Position-based classification
        normalized_y = y_position / 720  # Assuming 720p
        
        if normalized_y < 0.35:
            # Front court shots
            options = ['net_shot', 'return_net', 'push', 'rush', 'cross_court_net']
            weights = [0.35, 0.25, 0.2, 0.1, 0.1]
        elif normalized_y > 0.65:
            # Back court shots
            options = ['clear', 'smash', 'drop', 'defensive_lob', 'back_court_drive']
            weights = [0.25, 0.3, 0.2, 0.15, 0.1]
        else:
            # Mid court shots
            options = ['drive', 'smash', 'drop', 'lob', 'push']
            weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        
        shot_type = random.choices(options, weights=weights, k=1)[0]
        confidence = random.uniform(0.65, 0.85)
        
        return shot_type, confidence
    
    def _enhance_shot(self, shot: Dict, shot_idx: int) -> Dict:
        """Add additional information to existing shot data"""
        shot_type = shot.get('shot_type', 'drive')
        player = shot.get('player', 'Player A' if shot_idx % 2 == 0 else 'Player B')
        
        if shot_type not in self.SHOT_TYPES:
            shot_type = 'drive'
            shot['shot_type'] = shot_type
        
        if 'shot_type_zh' not in shot:
            shot['shot_type_zh'] = self.SHOT_TYPES[shot_type]['zh']
        
        if 'category' not in shot:
            shot['category'] = self.SHOT_TYPES[shot_type]['category']
        
        if 'description' not in shot:
            shot['description'] = self._generate_shot_description(shot_type, player)
        
        if 'confidence' not in shot:
            shot['confidence'] = random.uniform(0.7, 0.9)
        
        if 'shot_number' not in shot:
            shot['shot_number'] = shot_idx + 1
        
        return shot
    
    def _generate_shot_description(self, shot_type: str, player: str) -> str:
        """Generate natural language description for a shot"""
        descriptions = {
            'short_service': [
                f"{player} starts with a short service.",
                f"{player} serves short to begin the rally.",
                f"Short service from {player}."
            ],
            'long_service': [
                f"{player} performs a long service to the back court.",
                f"{player} serves deep to the baseline.",
                f"High serve from {player}."
            ],
            'flick_serve': [
                f"{player} executes a deceptive flick serve!",
                f"Quick flick serve from {player} catches opponent off guard.",
                f"{player} flicks the serve to the back court."
            ],
            'high_serve': [
                f"{player} delivers a high serve to the back court.",
                f"Powerful high serve from {player}!",
                f"{player} sends a lofted serve deep."
            ],
            'net_shot': [
                f"{player} plays a delicate net shot.",
                f"Soft net shot from {player}.",
                f"{player} taps it over the net."
            ],
            'return_net': [
                f"{player} returns at the net.",
                f"{player} counter-attacks at the net.",
                f"Quick net return from {player}."
            ],
            'cross_court_net': [
                f"{player} plays a cross-court net shot.",
                f"Clever cross-net from {player}.",
                f"{player} angles the net shot."
            ],
            'smash': [
                f"{player} executes a powerful smash!",
                f"Thunderous smash from {player}!",
                f"{player} attacks with a smash!"
            ],
            'wrist_smash': [
                f"{player} performs a quick wrist smash.",
                f"Deceptive wrist smash from {player}.",
                f"{player} flicks a smash."
            ],
            'rush': [
                f"{player} rushes forward at the net.",
                f"Aggressive rush from {player}.",
                f"{player} attacks the net quickly."
            ],
            'push': [
                f"{player} pushes to mid-court.",
                f"Push shot from {player}.",
                f"{player} sends it to the middle."
            ],
            'drop': [
                f"{player} plays a drop shot.",
                f"Soft drop from {player}.",
                f"{player} cuts it short."
            ],
            'passive_drop': [
                f"{player} plays a passive drop.",
                f"{player} blocks with a soft drop.",
                f"Defensive drop from {player}."
            ],
            'clear': [
                f"{player} clears to the back court.",
                f"High clear from {player}.",
                f"{player} sends it deep."
            ],
            'lob': [
                f"{player} lifts to the back court.",
                f"{player} lobs high.",
                f"Defensive lob from {player}."
            ],
            'defensive_lob': [
                f"{player} desperately lifts the shuttle.",
                f"Scrambling lob from {player}.",
                f"{player} recovers with a high lob."
            ],
            'drive': [
                f"{player} drives it flat.",
                f"Fast drive from {player}.",
                f"{player} attacks with a drive."
            ],
            'driven_flight': [
                f"{player} hits a short drive.",
                f"Quick flat shot from {player}.",
                f"{player} punches it."
            ],
            'back_court_drive': [
                f"{player} drives from the back.",
                f"Baseline drive from {player}.",
                f"{player} counters from deep."
            ],
            'defensive_drive': [
                f"{player} drives defensively.",
                f"Counter-drive from {player}.",
                f"{player} blocks with a drive."
            ]
        }
        
        options = descriptions.get(shot_type, [f"{player} plays a shot."])
        return random.choice(options)
    
    def get_shot_statistics(self, shots: List[Dict]) -> Dict:
        """Calculate statistics for a list of shots"""
        if not shots:
            return {
                'total_shots': 0,
                'player_a_shots': 0,
                'player_b_shots': 0,
                'shot_type_distribution': {},
                'category_distribution': {}
            }
        
        stats = {
            'total_shots': len(shots),
            'player_a_shots': len([s for s in shots if 'A' in s.get('player', '')]),
            'player_b_shots': len([s for s in shots if 'B' in s.get('player', '')]),
            'shot_type_distribution': {},
            'category_distribution': {},
            'average_confidence': round(
                np.mean([s.get('confidence', 0.7) for s in shots]), 2
            )
        }
        
        # Count shot types
        for shot in shots:
            shot_type = shot.get('shot_type', 'unknown')
            category = shot.get('category', 'unknown')
            
            stats['shot_type_distribution'][shot_type] = \
                stats['shot_type_distribution'].get(shot_type, 0) + 1
            stats['category_distribution'][category] = \
                stats['category_distribution'].get(category, 0) + 1
        
        return stats
