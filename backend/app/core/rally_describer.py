"""
Rally Describer Module
Generates detailed natural language descriptions for badminton rallies.
Provides tactical analysis and key moment identification.
"""

import random
from typing import Dict, List, Optional

class RallyDescriber:
    """
    Generates detailed narratives and descriptions for badminton rallies.
    Provides tactical analysis and identifies key moments.
    """
    
    # Templates for rally descriptions
    OPENING_TEMPLATES = [
        "This rally begins with {player}'s {service_type}.",
        "{player} initiates the rally with a {service_type}.",
        "The point starts as {player} serves {service_desc}.",
        "{player} opens with a {service_type}, setting up the rally."
    ]
    
    SHOT_SEQUENCE_TEMPLATES = {
        'smash': [
            "{player} unleashes a powerful smash",
            "{player} attacks with a thunderous smash",
            "{player} goes on the offensive with a smash"
        ],
        'drop': [
            "{player} plays a deceptive drop shot",
            "{player} softens the pace with a drop",
            "{player} catches the opponent off guard with a drop"
        ],
        'clear': [
            "{player} clears to the back court",
            "{player} sends the shuttle deep",
            "{player} pushes the opponent back with a clear"
        ],
        'lob': [
            "{player} lifts the shuttle high",
            "{player} defensively lobs to buy time",
            "{player} sends the shuttle up and back"
        ],
        'net_shot': [
            "{player} plays a delicate net shot",
            "{player} responds with a tight net shot",
            "{player} demonstrates soft hands at the net"
        ],
        'drive': [
            "{player} fires a flat drive",
            "{player} attacks with a quick drive",
            "{player} keeps the pressure with a drive"
        ],
        'push': [
            "{player} pushes to the mid-court",
            "{player} sends a quick push",
            "{player} attacks forward with a push"
        ],
        'rush': [
            "{player} rushes the net aggressively",
            "{player} pounces on the shuttle at the net",
            "{player} attacks with a fast rush"
        ]
    }
    
    ENDING_TEMPLATES = {
        'net': [
            "The rally ends with the shuttle finding the net.",
            "A net error concludes this exchange.",
            "The shuttle clips the net, ending the rally."
        ],
        'out': [
            "The rally concludes with the shuttle going out of bounds.",
            "The shot sails out, ending the point.",
            "An out error brings this rally to a close."
        ],
        'in_court': [
            "A winning shot finds its mark, ending the rally.",
            "The point ends with an unreturnable shot.",
            "A decisive winner concludes the exchange."
        ]
    }
    
    INTENSITY_WORDS = {
        'short': ['brief', 'quick', 'short'],
        'medium': ['competitive', 'engaging', 'tactical'],
        'long': ['intense', 'grueling', 'marathon', 'exhausting']
    }
    
    def __init__(self):
        """Initialize the rally describer."""
        pass
    
    def generate_rally_narrative(self, rally: Dict) -> str:
        """
        Generate a complete narrative description of a rally.
        
        Args:
            rally: Rally data with shots, duration, winner, etc.
            
        Returns:
            A detailed natural language description
        """
        parts = []
        
        # 1. Opening
        shots = rally.get('shots', [])
        duration = rally.get('duration', 0)
        winner = rally.get('winner', 'Player A')
        end_reason = rally.get('end_reason', 'in_court')
        rally_num = rally.get('rally_number', 1)
        
        # Add rally header
        intensity = self._get_intensity(duration, len(shots))
        parts.append(f"**Rally {rally_num}** - A {random.choice(self.INTENSITY_WORDS[intensity])} {duration:.1f}-second exchange with {len(shots)} shots.")
        parts.append("")
        
        # 2. Opening shot
        if shots:
            first_shot = shots[0]
            player = first_shot.get('player', 'Player A')
            shot_type = first_shot.get('shot_type', 'short_service')
            
            service_type = 'short service' if 'short' in shot_type else 'long service'
            service_desc = 'short' if 'short' in shot_type else 'deep to the back court'
            
            opening = random.choice(self.OPENING_TEMPLATES).format(
                player=player,
                service_type=service_type,
                service_desc=service_desc
            )
            parts.append(opening)
        
        # 3. Key moments in the rally
        key_moments = self.identify_key_moments(rally)
        if key_moments:
            parts.append("")
            parts.append("**Key moments:**")
            for moment in key_moments[:3]:  # Top 3 moments
                parts.append(f"- {moment['description']}")
        
        # 4. Shot flow summary
        if len(shots) > 2:
            flow = self._describe_shot_flow(shots)
            parts.append("")
            parts.append(f"**Rally flow:** {flow}")
        
        # 5. Ending
        ending = random.choice(self.ENDING_TEMPLATES.get(end_reason, self.ENDING_TEMPLATES['in_court']))
        parts.append("")
        parts.append(ending)
        parts.append(f"**{winner}** wins this rally.")
        
        return "\n".join(parts)
    
    def describe_shot_sequence(self, shots: List[Dict]) -> str:
        """
        Generate a description of the shot sequence.
        
        Args:
            shots: List of shot dictionaries
            
        Returns:
            A description of the shot flow
        """
        if not shots:
            return "No shots recorded."
        
        descriptions = []
        
        for i, shot in enumerate(shots):
            player = shot.get('player', 'Player')
            shot_type = shot.get('shot_type', 'drive')
            
            # Get template for shot type
            templates = self.SHOT_SEQUENCE_TEMPLATES.get(
                shot_type, 
                [f"{{player}} plays a {shot_type.replace('_', ' ')}"]
            )
            desc = random.choice(templates).format(player=player)
            descriptions.append(desc)
        
        # Join with connectors
        if len(descriptions) <= 3:
            return ". ".join(descriptions) + "."
        else:
            # Summarize longer sequences
            opening = descriptions[0]
            middle = f"After {len(descriptions) - 2} exchanges"
            ending = descriptions[-1]
            return f"{opening}. {middle}, {ending}."
    
    def identify_key_moments(self, rally: Dict) -> List[Dict]:
        """
        Identify key moments in a rally.
        
        Returns:
            List of key moment dictionaries with time and description
        """
        key_moments = []
        shots = rally.get('shots', [])
        mistakes = rally.get('mistakes', [])
        
        # Key moment types
        for i, shot in enumerate(shots):
            shot_type = shot.get('shot_type', '')
            player = shot.get('player', 'Player')
            time = shot.get('time', 0)
            
            # Smashes are key moments
            if 'smash' in shot_type:
                key_moments.append({
                    'time': time,
                    'shot_number': i + 1,
                    'type': 'attack',
                    'description': f"{player} attacks with a powerful smash at {time:.1f}s"
                })
            
            # Defensive saves
            if 'defensive' in shot_type or 'lob' in shot_type:
                if i > 0 and 'smash' in shots[i-1].get('shot_type', ''):
                    key_moments.append({
                        'time': time,
                        'shot_number': i + 1,
                        'type': 'defense',
                        'description': f"{player} makes a crucial defensive save at {time:.1f}s"
                    })
            
            # Net play sequences
            if 'net' in shot_type and i > 0 and 'net' in shots[i-1].get('shot_type', ''):
                key_moments.append({
                    'time': time,
                    'shot_number': i + 1,
                    'type': 'net_battle',
                    'description': f"Intense net battle at {time:.1f}s"
                })
        
        # Add mistakes as key moments
        for mistake in mistakes:
            key_moments.append({
                'time': mistake.get('time', 0),
                'shot_number': mistake.get('shot_number', 0),
                'type': 'mistake',
                'description': f"{mistake.get('player', 'Player')} makes a critical error: {mistake.get('description', 'mistake')}"
            })
        
        # Sort by time and importance
        key_moments.sort(key=lambda x: x['time'])
        
        return key_moments
    
    def generate_tactical_analysis(self, rally: Dict) -> str:
        """
        Generate tactical analysis of a rally.
        
        Returns:
            Tactical insights about the rally
        """
        shots = rally.get('shots', [])
        winner = rally.get('winner', 'Player A')
        end_reason = rally.get('end_reason', 'in_court')
        
        if not shots:
            return "Insufficient data for tactical analysis."
        
        # Count shot types by player
        player_a_shots = [s for s in shots if 'A' in s.get('player', '')]
        player_b_shots = [s for s in shots if 'B' in s.get('player', '')]
        
        a_attack = sum(1 for s in player_a_shots if s.get('shot_type') in ['smash', 'drop', 'rush', 'push'])
        b_attack = sum(1 for s in player_b_shots if s.get('shot_type') in ['smash', 'drop', 'rush', 'push'])
        
        a_defense = sum(1 for s in player_a_shots if 'lob' in s.get('shot_type', '') or 'defensive' in s.get('shot_type', ''))
        b_defense = sum(1 for s in player_b_shots if 'lob' in s.get('shot_type', '') or 'defensive' in s.get('shot_type', ''))
        
        analysis_parts = []
        
        # Attacking patterns
        if a_attack > b_attack:
            analysis_parts.append("Player A was more aggressive, attempting more attacking shots.")
        elif b_attack > a_attack:
            analysis_parts.append("Player B controlled the offensive, showing more aggression.")
        else:
            analysis_parts.append("Both players showed balanced attacking patterns.")
        
        # Defensive comparison
        if a_defense > b_defense:
            analysis_parts.append("Player A was pushed into more defensive positions.")
        elif b_defense > a_defense:
            analysis_parts.append("Player B had to defend more frequently.")
        
        # Rally outcome analysis
        if end_reason == 'net':
            analysis_parts.append("The rally was decided by a net error, suggesting tight play near the net.")
        elif end_reason == 'out':
            analysis_parts.append("The point ended with an out error, possibly from overhitting under pressure.")
        else:
            analysis_parts.append(f"{winner} finished the rally with a well-placed winner.")
        
        return " ".join(analysis_parts)
    
    def _get_intensity(self, duration: float, shot_count: int) -> str:
        """Determine rally intensity based on duration and shots."""
        if duration < 5 or shot_count < 4:
            return 'short'
        elif duration < 15 or shot_count < 12:
            return 'medium'
        else:
            return 'long'
    
    def _describe_shot_flow(self, shots: List[Dict]) -> str:
        """Generate a brief description of shot flow."""
        if len(shots) < 2:
            return "Brief exchange."
        
        # Count shot categories
        attack_shots = sum(1 for s in shots if s.get('shot_type') in ['smash', 'drop', 'rush', 'push'])
        net_shots = sum(1 for s in shots if 'net' in s.get('shot_type', ''))
        clear_shots = sum(1 for s in shots if s.get('shot_type') in ['clear', 'lob'])
        
        total = len(shots)
        
        if attack_shots / total > 0.4:
            return "A fast-paced attacking rally with multiple offensive attempts."
        elif net_shots / total > 0.3:
            return "A tactical rally with plenty of net play."
        elif clear_shots / total > 0.4:
            return "A rally dominated by baseline exchanges and clears."
        else:
            return "A well-balanced rally with varied shot selection."
    
    def generate_rally_summary(self, rally: Dict) -> Dict:
        """
        Generate a complete summary object for a rally.
        
        Returns:
            Dictionary with narrative, key moments, and tactical analysis
        """
        return {
            'rally_number': rally.get('rally_number', 1),
            'duration': rally.get('duration', 0),
            'shot_count': len(rally.get('shots', [])),
            'winner': rally.get('winner', 'Unknown'),
            'narrative': self.generate_rally_narrative(rally),
            'shot_description': self.describe_shot_sequence(rally.get('shots', [])),
            'key_moments': self.identify_key_moments(rally),
            'tactical_analysis': self.generate_tactical_analysis(rally)
        }
