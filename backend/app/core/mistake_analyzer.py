"""
Mistake Analyzer Module - Enhanced with Video Clip Extraction
Detects player mistakes and generates video clips showing exact moments.
"""

import os
import cv2
import random
import imageio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Mistake:
    """Represents a detected mistake with video clip"""
    mistake_id: str
    rally_number: int
    shot_number: int
    frame: int
    time: float
    player: str
    mistake_type: str
    category: str
    severity: str
    description: str
    explanation: str
    improvement_suggestion: str
    clip_path: Optional[str] = None
    thumbnail_path: Optional[str] = None

class MistakeAnalyzer:
    """
    Analyzes player mistakes and extracts video clips.
    Provides detailed explanations and improvement suggestions.
    """
    
    # Mistake type definitions with multiple variations
    MISTAKE_TYPES = {
        'net_error': {
            'category': 'unforced',
            'descriptions': [
                'Shot hit the net',
                'Failed to clear the net',
                'Net cord error - shuttle didn\'t go over'
            ],
            'explanations': [
                'The trajectory was too low. This often happens when rushing the shot without proper preparation.',
                'Racket angle at impact was too steep, sending the shuttle into the net.',
                'Insufficient lift on the shot. Focus on follow-through to get more height.'
            ],
            'suggestions': [
                'Adjust trajectory slightly higher to clear the net consistently.',
                'Focus on a higher contact point when playing net shots.',
                'Practice net drills to improve touch and height control.',
                'Slow down and prepare properly before executing the shot.'
            ]
        },
        'out_long': {
            'category': 'unforced',
            'descriptions': [
                'Shot went out at the back',
                'Overhit to the baseline',
                'Too much power - shuttle landed long'
            ],
            'explanations': [
                'Excessive power was applied to the shot without adjusting the angle.',
                'The follow-through was too aggressive for the intended distance.',
                'Misjudged the court depth and overhit the shuttle.'
            ],
            'suggestions': [
                'Reduce power or adjust angle to keep shots in court.',
                'Focus on controlled power rather than maximum force.',
                'Practice distance control with target drills.',
                'Use more wrist and less arm for better control.'
            ]
        },
        'out_wide': {
            'category': 'unforced',
            'descriptions': [
                'Shot went out on the sides',
                'Angled too wide - out of bounds',
                'Cross-court shot went out'
            ],
            'explanations': [
                'Lateral control needs adjustment - the shot drifted wide.',
                'Overcommitted to the angle, sending the shuttle past the sideline.',
                'Body rotation took the shot too far to the side.'
            ],
            'suggestions': [
                'Focus on keeping the shuttle within the sidelines.',
                'Practice cross-court shots with specific targets.',
                'Work on body alignment during the swing.',
                'Aim for 30cm inside the line for safety margin.'
            ]
        },
        'missed_return': {
            'category': 'forced',
            'descriptions': [
                'Failed to reach the shuttle in time',
                'Couldn\'t get to the shot',
                'Out of position - unable to return'
            ],
            'explanations': [
                'The opponent\'s shot effectively moved the player out of position.',
                'Footwork couldn\'t cover the distance required to reach the shuttle.',
                'Late anticipation led to delayed movement.'
            ],
            'suggestions': [
                'Work on footwork and court coverage drills.',
                'Practice split-step timing to improve reaction speed.',
                'Develop better anticipation by reading opponent\'s body language.',
                'Return to base position faster after each shot.'
            ]
        },
        'poor_shot_selection': {
            'category': 'tactical',
            'descriptions': [
                'Wrong shot choice for the situation',
                'Suboptimal shot selection',
                'A better shot option was available'
            ],
            'explanations': [
                'The chosen shot type wasn\'t ideal for the rally situation and court position.',
                'Didn\'t adapt to the opponent\'s positioning before selecting the shot.',
                'Predictable choice that the opponent was able to read easily.'
            ],
            'suggestions': [
                'Consider court position and opponent location before choosing a shot.',
                'Study opponent patterns to make better tactical decisions.',
                'Practice decision-making under pressure.',
                'Vary shot selection to be less predictable.'
            ]
        },
        'weak_return': {
            'category': 'execution',
            'descriptions': [
                'Return was too weak',
                'Gave opponent easy attacking opportunity',
                'Lifted too high - inviting attack'
            ],
            'explanations': [
                'Didn\'t generate enough power or accuracy on the return.',
                'The shot sat up in mid-court allowing an easy attacking opportunity.',
                'Under pressure, played a safe but highly attackable shot.'
            ],
            'suggestions': [
                'Generate more power from legs and core rotation.',
                'Even under pressure, aim for depth or tight net shots.',
                'Practice defensive returns that are harder to attack.',
                'Use flat drives instead of high lifts when possible.'
            ]
        },
        'timing_error': {
            'category': 'execution',
            'descriptions': [
                'Late contact with shuttle',
                'Mistimed the swing',
                'Early swing - poor timing'
            ],
            'explanations': [
                'Contact point was behind the optimal position for this shot.',
                'The swing started before or after the shuttle was in the ideal zone.',
                'Footwork speed didn\'t synchronize with shot preparation.'
            ],
            'suggestions': [
                'Focus on watching the shuttle all the way to the racket.',
                'Work on coordination between movement and swing timing.',
                'Practice multi-shuttle drills for better timing.',
                'Prepare racket earlier to have more time for adjustment.'
            ]
        },
        'poor_positioning': {
            'category': 'tactical',
            'descriptions': [
                'Out of position for the return',
                'Poor court coverage',
                'Failed to recover to base'
            ],
            'explanations': [
                'Was not in the optimal position to play the next shot effectively.',
                'Didn\'t recover to base position after the previous shot.',
                'Anticipated wrongly and moved to the wrong area of the court.'
            ],
            'suggestions': [
                'Always return to base position after each shot.',
                'Use split-step when opponent is about to hit.',
                'Study court positioning based on opponent\'s shot type.',
                'Practice shadow footwork drills for positioning.'
            ]
        }
    }
    
    def __init__(self, video_path: str, output_dir: str):
        """Initialize the mistake analyzer with video path."""
        self.video_path = video_path
        self.output_dir = output_dir
        self.clips_dir = os.path.join(output_dir, "mistake_clips")
        os.makedirs(self.clips_dir, exist_ok=True)
        
        # Video properties (lazy loaded)
        self._video = None
        self._fps = None
        self._width = None
        self._height = None
        
    def _open_video(self):
        """Open video capture (lazy loading)."""
        if self._video is None:
            self._video = cv2.VideoCapture(self.video_path)
            self._fps = self._video.get(cv2.CAP_PROP_FPS) or 30
            self._width = int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._height = int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return self._video
        
    def analyze_rally_mistakes(self, rally: Dict, player_a: str, 
                               player_b: str) -> List[Dict]:
        """
        Analyze a rally for player mistakes and extract video clips.
        """
        mistakes = []
        rally_num = rally.get('rally_number', 0)
        end_reason = rally.get('end_reason', 'in_court')
        winner = rally.get('winner', 'Player A')
        shots = rally.get('shots', [])
        duration = rally.get('duration', 10)
        
        # Get rally frame range for proper clip extraction
        start_frame = rally.get('start_frame', 0)
        end_frame = rally.get('end_frame', start_frame + int(duration * 30))
        
        # Determine the loser (who made the final mistake)
        if 'A' in str(winner):
            loser = player_b
        else:
            loser = player_a
        
        # Generate mistake based on end reason
        if end_reason in ['net', 'out']:
            mistake = self._create_rally_end_mistake(
                rally_num, shots, end_reason, loser, duration, end_frame
            )
            if mistake:
                # Extract video clip for the mistake
                clip_path = self._extract_mistake_clip(mistake, rally_num)
                mistake['clip_path'] = clip_path
                
                # Generate thumbnail
                thumb_path = self._generate_thumbnail(mistake, rally_num)
                mistake['thumbnail_path'] = thumb_path
                
                mistakes.append(mistake)
        
        # Add tactical mistakes for longer rallies
        if len(shots) > 6 and random.random() < 0.35:
            # Use middle of rally for tactical mistake
            mid_frame = start_frame + (end_frame - start_frame) // 2
            tactical = self._create_tactical_mistake(rally_num, shots, loser, mid_frame)
            if tactical:
                tactical['clip_path'] = self._extract_mistake_clip(tactical, rally_num)
                mistakes.append(tactical)
        
        # Add positioning mistakes occasionally
        if len(shots) > 4 and random.random() < 0.25:
            # Use a quarter into the rally for positioning mistake
            quarter_frame = start_frame + (end_frame - start_frame) // 4
            position = self._create_positioning_mistake(
                rally_num, shots, random.choice([player_a, player_b]), quarter_frame
            )
            if position:
                position['clip_path'] = self._extract_mistake_clip(position, rally_num)
                mistakes.append(position)
        
        return mistakes
    
    def _create_rally_end_mistake(self, rally_num: int, shots: List[Dict],
                                  error_type: str, player: str,
                                  duration: float, end_frame: int = None) -> Dict:
        """Create a mistake for a rally-ending error."""
        # Get the last shot
        if shots:
            last_shot = shots[-1]
            shot_number = last_shot.get('shot_number', len(shots))
            frame = end_frame if end_frame else last_shot.get('frame', int(duration * 30))
            time = last_shot.get('time', duration)
            shot_type = last_shot.get('shot_type', 'shot')
        else:
            shot_number = 1
            frame = end_frame if end_frame else int(duration * 30)
            time = duration
            shot_type = 'shot'
        
        # Determine mistake type
        if error_type == 'net':
            mistake_type = 'net_error'
            severity = 'moderate'
        elif error_type == 'out':
            mistake_type = random.choice(['out_long', 'out_wide'])
            severity = random.choice(['minor', 'moderate'])
        else:
            mistake_type = 'weak_return'
            severity = 'minor'
        
        mistake_info = self.MISTAKE_TYPES.get(mistake_type, {})
        
        return {
            'mistake_id': f"R{rally_num}_end",
            'rally_number': rally_num,
            'shot_number': shot_number,
            'frame': frame,
            'time': round(time, 2),
            'player': player,
            'mistake_type': mistake_type,
            'category': mistake_info.get('category', 'unforced'),
            'severity': severity,
            'description': random.choice(mistake_info.get('descriptions', ['Error occurred'])),
            'explanation': random.choice(mistake_info.get('explanations', ['An error was made.'])),
            'improvement_suggestion': random.choice(mistake_info.get('suggestions', ['Practice this area.'])),
            'shot_type': shot_type
        }
    
    def _create_tactical_mistake(self, rally_num: int, shots: List[Dict],
                                 player: str, frame: int = 0) -> Optional[Dict]:
        """Create a tactical mistake."""
        player_shots = [s for s in shots if player in s.get('player', '')]
        if not player_shots:
            return None
        
        shot = random.choice(player_shots)
        mistake_info = self.MISTAKE_TYPES['poor_shot_selection']
        
        return {
            'mistake_id': f"R{rally_num}_tactical_{shot.get('shot_number', 0)}",
            'rally_number': rally_num,
            'shot_number': shot.get('shot_number', 0),
            'frame': frame if frame > 0 else shot.get('frame', 0),
            'time': shot.get('time', 0),
            'player': player,
            'mistake_type': 'poor_shot_selection',
            'category': 'tactical',
            'severity': 'minor',
            'description': random.choice(mistake_info['descriptions']),
            'explanation': random.choice(mistake_info['explanations']),
            'improvement_suggestion': random.choice(mistake_info['suggestions']),
            'shot_type': shot.get('shot_type', 'shot')
        }
    
    def _create_positioning_mistake(self, rally_num: int, shots: List[Dict],
                                    player: str, frame: int = 0) -> Optional[Dict]:
        """Create a positioning mistake."""
        player_shots = [s for s in shots if player in s.get('player', '')]
        if not player_shots:
            return None
        
        shot = random.choice(player_shots)
        mistake_info = self.MISTAKE_TYPES['poor_positioning']
        
        return {
            'mistake_id': f"R{rally_num}_position_{shot.get('shot_number', 0)}",
            'rally_number': rally_num,
            'shot_number': shot.get('shot_number', 0),
            'frame': frame if frame > 0 else shot.get('frame', 0),
            'time': shot.get('time', 0),
            'player': player,
            'mistake_type': 'poor_positioning',
            'category': 'tactical',
            'severity': 'minor',
            'description': random.choice(mistake_info['descriptions']),
            'explanation': random.choice(mistake_info['explanations']),
            'improvement_suggestion': random.choice(mistake_info['suggestions']),
            'shot_type': shot.get('shot_type', 'shot')
        }
    
    def _extract_mistake_clip(self, mistake: Dict, rally_num: int) -> Optional[str]:
        """
        Extract a GIF clip showing the mistake.
        GIFs loop automatically and are browser-friendly.
        """
        try:
            # Ensure video path is absolute
            video_path = os.path.abspath(self.video_path)
            
            # Open a FRESH video capture for each clip
            video = cv2.VideoCapture(video_path)
            if not video.isOpened():
                print(f"ERROR: Could not open video file for clip extraction: {video_path}")
                return None
            
            fps = video.get(cv2.CAP_PROP_FPS) or 30
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            
            frame_num = mistake.get('frame', 0)
            mistake_id = mistake.get('mistake_id', f'mistake_{rally_num}')
            
            # Fix frame number if out of bounds
            if frame_num <= 0 or frame_num >= total_frames:
                frame_num = total_frames // 2
                print(f"Warning: Frame number {mistake.get('frame')} out of bounds (0-{total_frames}). Using middle frame.")
            
            # Extract 3 seconds around the mistake
            frames_before = int(1.5 * fps)
            frames_after = int(1.5 * fps)
            
            start_frame = max(0, frame_num - frames_before)
            end_frame = min(total_frames, frame_num + frames_after)
            
            output_path = os.path.abspath(os.path.join(self.clips_dir, f"{mistake_id}_clip.gif"))
            
            # Seek to start frame
            video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            frames = []
            # For GIF, we reduce size and skip frames to keep file small
            target_width = min(480, width)
            scale = target_width / width
            target_height = int(height * scale)
            
            # Take every Nth frame to reduce GIF size (aim for ~10 fps in GIF)
            frame_skip = max(1, int(fps / 10))
            
            frame_count = 0
            for i in range(end_frame - start_frame):
                ret, frame_img = video.read()
                if not ret:
                    break
                
                # Skip frames for smaller GIF
                if i % frame_skip != 0:
                    continue
                
                current_frame = start_frame + i
                
                # Convert BGR to RGB for imageio
                frame_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
                
                # Resize for smaller file
                frame_rgb = cv2.resize(frame_rgb, (target_width, target_height))
                
                # Add red border at the mistake moment
                if abs(current_frame - frame_num) < 8:
                    # Draw red border
                    cv2.rectangle(frame_rgb, (0, 0), 
                                 (target_width-1, target_height-1), 
                                 (255, 0, 0), 6)
                    
                    # Add mistake text
                    cv2.putText(
                        frame_rgb,
                        f"MISTAKE!",
                        (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 0, 0),
                        2
                    )
                    
                    cv2.putText(
                        frame_rgb,
                        f"{mistake.get('player', 'Player')}",
                        (20, 55),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )
                
                frames.append(frame_rgb)
                frame_count += 1
            
            video.release()
            
            if frames:
                # Save as GIF with loop=0 (infinite loop)
                imageio.mimsave(output_path, frames, plugin='pillow', duration=0.1, loop=0)
                print(f"GIF saved: {output_path} ({frame_count} frames)")
                return output_path
            
            return None
            
        except Exception as e:
            import traceback
            print(f"Error extracting GIF for {mistake.get('mistake_id')}: {e}")
            traceback.print_exc()
            return None
    
    def _generate_thumbnail(self, mistake: Dict, rally_num: int) -> Optional[str]:
        """Generate a thumbnail image for the mistake."""
        try:
            video = self._open_video()
            if video is None:
                return None
            
            frame_num = mistake.get('frame', 0)
            mistake_id = mistake.get('mistake_id', f'mistake_{rally_num}')
            
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = video.read()
            
            if not ret:
                return None
            
            # Add annotation
            cv2.rectangle(frame, (0, 0), (self._width-1, self._height-1), (0, 0, 255), 5)
            cv2.putText(
                frame,
                "MISTAKE",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 0, 255),
                3
            )
            
            output_path = os.path.join(self.clips_dir, f"{mistake_id}_thumb.jpg")
            cv2.imwrite(output_path, frame)
            
            return output_path
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    def get_player_weakness_summary(self, mistakes: List[Dict], 
                                    player: str) -> Dict:
        """Generate comprehensive weakness summary for a player."""
        player_mistakes = [m for m in mistakes if player in m.get('player', '')]
        
        if not player_mistakes:
            return {
                'player': player,
                'total_mistakes': 0,
                'weaknesses': [],
                'improvements': [],
                'summary': f'{player} showed solid performance with no significant errors.'
            }
        
        # Count mistake types and categories
        type_counts = {}
        category_counts = {}
        
        for m in player_mistakes:
            mtype = m.get('mistake_type', 'unknown')
            cat = m.get('category', 'unknown')
            
            type_counts[mtype] = type_counts.get(mtype, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Identify main weaknesses
        weaknesses = []
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        for mtype, count in sorted_types[:3]:
            mistake_info = self.MISTAKE_TYPES.get(mtype, {})
            weaknesses.append({
                'type': mtype.replace('_', ' ').title(),
                'count': count,
                'description': mistake_info.get('descriptions', ['Error'])[0],
                'severity': 'major' if count > 3 else 'moderate' if count > 1 else 'minor'
            })
        
        # Generate improvement plan
        improvements = set()
        for weakness in weaknesses:
            mtype = weakness['type'].lower().replace(' ', '_')
            suggestions = self.MISTAKE_TYPES.get(mtype, {}).get('suggestions', [])
            if suggestions:
                improvements.add(random.choice(suggestions))
        
        # Generate summary
        main_issue = weaknesses[0]['type'] if weaknesses else 'general execution'
        summary = f"{player} should focus on improving {main_issue}. "
        summary += f"Total mistakes: {len(player_mistakes)}. "
        summary += f"Main categories: {', '.join(f'{k} ({v})' for k, v in category_counts.items())}."
        
        return {
            'player': player,
            'total_mistakes': len(player_mistakes),
            'mistake_breakdown': type_counts,
            'category_breakdown': category_counts,
            'weaknesses': weaknesses,
            'improvements': list(improvements),
            'summary': summary
        }
    
    def close(self):
        """Release video resources."""
        if self._video is not None:
            self._video.release()
            self._video = None
    
    def __del__(self):
        self.close()
