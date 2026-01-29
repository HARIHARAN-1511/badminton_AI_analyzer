"""
Training Data Loader Module
Loads and processes ShuttleSet data for improved analysis accuracy.
The ShuttleSet dataset contains 36,492 annotated strokes from professional matches.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import glob
import random

class TrainingDataLoader:
    """
    Loads ShuttleSet training data to improve analysis accuracy.
    Provides statistics for shot types, rally patterns, and player behaviors.
    """
    
    # Shot type mapping (English -> ID)
    SHOT_TYPES = {
        'net shot': 0,
        'return net': 1,
        'smash': 2,
        'wrist smash': 3,
        'lob': 4,
        'defensive return lob': 5,
        'clear': 6,
        'drive': 7,
        'driven flight': 8,
        'back-court drive': 9,
        'drop': 10,
        'passive drop': 11,
        'push': 12,
        'rush': 13,
        'defensive return drive': 14,
        'cross-court net shot': 15,
        'short service': 16,
        'long service': 17
    }
    
    # Reverse mapping
    ID_TO_SHOT = {v: k for k, v in SHOT_TYPES.items()}
    
    # Shot type to internal name mapping
    SHOT_TYPE_INTERNAL = {
        'net shot': 'net_shot',
        'return net': 'return_net',
        'smash': 'smash',
        'wrist smash': 'wrist_smash',
        'lob': 'lob',
        'defensive return lob': 'defensive_lob',
        'clear': 'clear',
        'drive': 'drive',
        'driven flight': 'driven_flight',
        'back-court drive': 'back_court_drive',
        'drop': 'drop',
        'passive drop': 'passive_drop',
        'push': 'push',
        'rush': 'rush',
        'defensive return drive': 'defensive_drive',
        'cross-court net shot': 'cross_court_net',
        'short service': 'short_service',
        'long service': 'long_service'
    }
    
    def __init__(self, data_dir: str = None):
        """Initialize with path to ShuttleSet data directory."""
        if data_dir is None:
            # Default path relative to backend
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(base_dir, "data", "training", "shuttleset")
        
        self.data_dir = data_dir
        self.matches_df = None
        self.all_strokes_df = None
        self._loaded = False
        
        # Statistics computed from data
        self.shot_type_distribution = {}
        self.shot_transitions = {}
        self.rally_length_distribution = {}
        self.landing_patterns = {}
        self.lose_reasons = {}
        
    def load_data(self) -> bool:
        """Load all ShuttleSet data files."""
        if self._loaded:
            return True
            
        try:
            # Load match.csv
            match_path = os.path.join(self.data_dir, "match.csv")
            if os.path.exists(match_path):
                self.matches_df = pd.read_csv(match_path)
            
            # Load all set CSV files
            all_strokes = []
            set_files = glob.glob(os.path.join(self.data_dir, "**/set*.csv"), recursive=True)
            
            for set_file in set_files:
                try:
                    df = pd.read_csv(set_file)
                    # Add match info from folder name
                    folder_name = os.path.basename(os.path.dirname(set_file))
                    df['match_folder'] = folder_name
                    df['set_file'] = os.path.basename(set_file)
                    all_strokes.append(df)
                except Exception as e:
                    print(f"Error loading {set_file}: {e}")
            
            if all_strokes:
                self.all_strokes_df = pd.concat(all_strokes, ignore_index=True)
                self._compute_statistics()
                self._loaded = True
                return True
            
            return False
            
        except Exception as e:
            print(f"Error loading training data: {e}")
            return False
    
    def _compute_statistics(self):
        """Compute various statistics from the loaded data."""
        if self.all_strokes_df is None:
            return
        
        df = self.all_strokes_df
        
        # 1. Shot type distribution
        if 'type' in df.columns:
            type_counts = df['type'].value_counts()
            total = type_counts.sum()
            self.shot_type_distribution = {
                str(shot): count / total 
                for shot, count in type_counts.items()
            }
        
        # 2. Shot transitions (what shot follows what)
        if 'type' in df.columns and 'rally' in df.columns:
            self._compute_transitions(df)
        
        # 3. Rally length distribution
        if 'rally' in df.columns and 'ball_round' in df.columns:
            rally_lengths = df.groupby(['match_folder', 'set_file', 'rally'])['ball_round'].max()
            self.rally_length_distribution = {
                'mean': float(rally_lengths.mean()),
                'std': float(rally_lengths.std()),
                'median': float(rally_lengths.median()),
                'min': int(rally_lengths.min()),
                'max': int(rally_lengths.max())
            }
        
        # 4. Lose reasons
        if 'lose_reason' in df.columns:
            # Get unique rallies with their lose reasons
            rally_ends = df[df['ball_round'] == df.groupby(['match_folder', 'set_file', 'rally'])['ball_round'].transform('max')]
            reason_counts = rally_ends['lose_reason'].value_counts()
            total = reason_counts.sum()
            self.lose_reasons = {
                str(reason): count / total
                for reason, count in reason_counts.items()
            }
    
    def _compute_transitions(self, df: pd.DataFrame):
        """Compute shot type transition probabilities."""
        transitions = {}
        
        # Group by match and rally
        for (match, set_file, rally), group in df.groupby(['match_folder', 'set_file', 'rally']):
            group = group.sort_values('ball_round')
            types = group['type'].tolist()
            
            for i in range(len(types) - 1):
                current = str(types[i])
                next_shot = str(types[i + 1])
                
                if current not in transitions:
                    transitions[current] = {}
                if next_shot not in transitions[current]:
                    transitions[current][next_shot] = 0
                transitions[current][next_shot] += 1
        
        # Normalize to probabilities
        for current, nexts in transitions.items():
            total = sum(nexts.values())
            transitions[current] = {
                shot: count / total 
                for shot, count in nexts.items()
            }
        
        self.shot_transitions = transitions
    
    def get_shot_type_probability(self, shot_type: str) -> float:
        """Get probability of a shot type from training data."""
        self.load_data()
        return self.shot_type_distribution.get(shot_type, 0.05)
    
    def get_next_shot_probability(self, current_shot: str, next_shot: str) -> float:
        """Get probability of next_shot given current_shot."""
        self.load_data()
        if current_shot in self.shot_transitions:
            return self.shot_transitions[current_shot].get(next_shot, 0.05)
        return 0.05
    
    def get_likely_next_shots(self, current_shot: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get most likely next shots after a given shot."""
        self.load_data()
        if current_shot in self.shot_transitions:
            sorted_shots = sorted(
                self.shot_transitions[current_shot].items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_shots[:top_n]
        return []
    
    def sample_rally_length(self) -> int:
        """Sample a realistic rally length based on training data."""
        self.load_data()
        if self.rally_length_distribution:
            mean = self.rally_length_distribution['mean']
            std = self.rally_length_distribution['std']
            length = int(np.random.normal(mean, std))
            return max(2, min(50, length))  # Clamp between 2 and 50
        return random.randint(4, 15)
    
    def sample_lose_reason(self) -> str:
        """Sample a rally end reason based on training data."""
        self.load_data()
        if self.lose_reasons:
            reasons = list(self.lose_reasons.keys())
            probs = list(self.lose_reasons.values())
            return np.random.choice(reasons, p=probs)
        return random.choice(['net', 'out', 'winner'])
    
    def get_shot_type_name(self, shot_id: int) -> str:
        """Convert shot ID to internal name."""
        if shot_id in self.ID_TO_SHOT:
            external = self.ID_TO_SHOT[shot_id]
            return self.SHOT_TYPE_INTERNAL.get(external, 'drive')
        return 'drive'
    
    def sample_shot_sequence(self, length: int) -> List[str]:
        """Generate a realistic shot sequence of given length."""
        self.load_data()
        
        sequence = []
        
        # Start with a service
        if random.random() < 0.7:
            sequence.append('short service')
        else:
            sequence.append('long service')
        
        # Generate subsequent shots using transitions
        for _ in range(length - 1):
            prev_shot = sequence[-1]
            next_shots = self.get_likely_next_shots(prev_shot, top_n=5)
            
            if next_shots:
                shots, probs = zip(*next_shots)
                probs = np.array(probs)
                probs = probs / probs.sum()  # Normalize
                next_shot = np.random.choice(list(shots), p=probs)
            else:
                # Fallback to random common shots
                next_shot = random.choice([
                    'clear', 'drop', 'smash', 'lob', 'drive', 'net shot'
                ])
            
            sequence.append(next_shot)
        
        # Convert to internal names
        return [self.SHOT_TYPE_INTERNAL.get(s, s.replace(' ', '_')) for s in sequence]
    
    def get_statistics_summary(self) -> Dict:
        """Get summary of loaded training data statistics."""
        self.load_data()
        
        return {
            'total_strokes': len(self.all_strokes_df) if self.all_strokes_df is not None else 0,
            'total_matches': len(self.matches_df) if self.matches_df is not None else 0,
            'shot_type_distribution': self.shot_type_distribution,
            'rally_length_stats': self.rally_length_distribution,
            'lose_reasons': self.lose_reasons,
            'data_loaded': self._loaded
        }


# Global instance for easy access
_training_data = None

def get_training_data() -> TrainingDataLoader:
    """Get the global training data loader instance."""
    global _training_data
    if _training_data is None:
        _training_data = TrainingDataLoader()
    return _training_data
