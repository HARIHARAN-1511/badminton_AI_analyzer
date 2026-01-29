"""
PDF Report Generator
Generates comprehensive PDF reports for badminton match analysis.
Includes all analysis sections with embedded graphs and statistics.

Report Sections:
1. Cover Page & Match Summary
2. Rally-by-Rally Analysis
3. Player A Performance
4. Player B Performance
5. Shot Distribution Analysis
6. Mistake Analysis
7. Statistical Graphs
8. Improvement Recommendations
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Line
from typing import Dict, List, Any, Optional
import os
from datetime import datetime

class PDFReportGenerator:
    """
    Generates comprehensive PDF reports for badminton match analysis.
    Includes all visual elements and detailed analysis.
    """
    
    def __init__(self, analysis_results: Dict, output_dir: str):
        """
        Initialize PDF generator.
        
        Args:
            analysis_results: Complete analysis data from the analysis pipeline
            output_dir: Directory containing graphs and output files
        """
        self.results = analysis_results
        self.output_dir = output_dir
        self.graphs_dir = os.path.join(output_dir, "graphs")
        
        # Page settings
        self.page_size = A4
        self.margins = {
            'left': 1.5 * cm,
            'right': 1.5 * cm,
            'top': 2 * cm,
            'bottom': 2 * cm
        }
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Document elements
        self.elements = []
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='Title_Custom',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=30,
            textColor=colors.HexColor('#1a5276'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#566573'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2874a6'),
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a5276'),
            spaceBefore=15,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText_Custom',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='RallyTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2e86de'),
            spaceBefore=10,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='MistakeText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#c0392b'),
            leftIndent=20,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='SuggestionText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#27ae60'),
            leftIndent=20,
            spaceAfter=5
        ))
    
    def generate_report(self, output_path: str):
        """
        Generate the complete PDF report.
        
        Args:
            output_path: Path to save the PDF file
        """
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=self.page_size,
            leftMargin=self.margins['left'],
            rightMargin=self.margins['right'],
            topMargin=self.margins['top'],
            bottomMargin=self.margins['bottom']
        )
        
        # Build report sections
        self._add_cover_page()
        self._add_match_summary()
        self._add_rally_analysis()
        self._add_player_performance_a()
        self._add_player_performance_b()
        self._add_shot_analysis()
        self._add_mistake_analysis()
        self._add_statistical_graphs()
        self._add_recommendations()
        
        # Build PDF
        doc.build(self.elements)
    
    def _add_cover_page(self):
        """Add cover page to report"""
        self.elements.append(Spacer(1, 2 * inch))
        
        # Title
        self.elements.append(Paragraph(
            "Badminton Match Analysis Report",
            self.styles['Title_Custom']
        ))
        
        # Player names
        player_a = self.results.get('player_a', 'Player A')
        player_b = self.results.get('player_b', 'Player B')
        
        self.elements.append(Paragraph(
            f"{player_a} vs {player_b}",
            self.styles['Subtitle']
        ))
        
        self.elements.append(Spacer(1, 1 * inch))
        
        # Match info
        video_info = self.results.get('video_info', {})
        match_info = f"""
        <b>Match Duration:</b> {video_info.get('duration_formatted', 'N/A')}<br/>
        <b>Total Rallies:</b> {self.results.get('total_rallies', 0)}<br/>
        <b>Analysis Date:</b> {datetime.now().strftime('%B %d, %Y')}
        """
        self.elements.append(Paragraph(match_info, self.styles['BodyText']))
        
        self.elements.append(Spacer(1, 2 * inch))
        
        # Footer note
        self.elements.append(Paragraph(
            "Generated by Badminton Analysis Platform",
            self.styles['Subtitle']
        ))
        
        self.elements.append(PageBreak())
    
    def _add_match_summary(self):
        """Add match summary section"""
        self.elements.append(Paragraph("Match Summary", self.styles['SectionTitle']))
        
        stats = self.results.get('statistics', {})
        summary = stats.get('match_summary', {})
        
        # Summary table
        table_data = [
            ['Statistic', 'Value'],
            ['Total Rallies', str(summary.get('total_rallies', 0))],
            ['Player A Wins', str(summary.get('player_a_wins', 0))],
            ['Player B Wins', str(summary.get('player_b_wins', 0))],
            ['Average Rally Duration', f"{summary.get('average_rally_duration', 0)}s"],
            ['Total Shots', str(summary.get('total_shots', 0))],
            ['Average Shots/Rally', str(summary.get('average_shots_per_rally', 0))],
            ['Total Mistakes Detected', str(self.results.get('total_mistakes', 0))]
        ]
        
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eaf2f8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aab7b8')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.5 * inch))
        
        # Win/Loss breakdown graph if exists
        win_loss_path = os.path.join(self.graphs_dir, 'win_loss_breakdown.png')
        if os.path.exists(win_loss_path):
            img = Image(win_loss_path, width=6*inch, height=3*inch)
            self.elements.append(img)
        
        self.elements.append(PageBreak())
    
    def _add_rally_analysis(self):
        """Add rally-by-rally analysis section"""
        self.elements.append(Paragraph("Rally-by-Rally Analysis", self.styles['SectionTitle']))
        
        rallies = self.results.get('rallies', [])
        
        if not rallies:
            self.elements.append(Paragraph(
                "No rallies detected in the analysis.",
                self.styles['BodyText']
            ))
            return
        
        # Rally duration graph
        duration_path = os.path.join(self.graphs_dir, 'rally_duration.png')
        if os.path.exists(duration_path):
            img = Image(duration_path, width=6*inch, height=2.5*inch)
            self.elements.append(img)
            self.elements.append(Spacer(1, 0.3*inch))
        
        # Rally details table
        for i, rally in enumerate(rallies[:20]):  # Limit to first 20 rallies
            rally_num = rally.get('rally_number', i + 1)
            
            self.elements.append(Paragraph(
                f"Rally {rally_num}",
                self.styles['RallyTitle']
            ))
            
            # Rally info
            info = f"""
            <b>Duration:</b> {rally.get('duration', 0):.1f}s | 
            <b>Shots:</b> {len(rally.get('shots', []))} | 
            <b>Winner:</b> {rally.get('winner', 'Unknown')} | 
            <b>End Reason:</b> {rally.get('end_reason', 'Unknown')}
            """
            self.elements.append(Paragraph(info, self.styles['BodyText']))
            
            # Description
            if rally.get('description'):
                self.elements.append(Paragraph(
                    rally['description'],
                    self.styles['BodyText']
                ))
            
            # Shot sequence
            shots = rally.get('shots', [])
            if shots:
                shot_text = "Shot sequence: "
                shot_types = [f"{s.get('player', '?')}-{s.get('shot_type', '?')}" 
                              for s in shots[:10]]
                shot_text += " → ".join(shot_types)
                if len(shots) > 10:
                    shot_text += f" ... (+{len(shots) - 10} more)"
                self.elements.append(Paragraph(shot_text, self.styles['BodyText']))
            
            # Mistakes in this rally
            mistakes = rally.get('mistakes', [])
            if mistakes:
                for mistake in mistakes:
                    self.elements.append(Paragraph(
                        f"⚠ {mistake.get('player', 'Unknown')}: {mistake.get('description', '')}",
                        self.styles['MistakeText']
                    ))
            
            self.elements.append(Spacer(1, 0.2*inch))
        
        if len(rallies) > 20:
            self.elements.append(Paragraph(
                f"... and {len(rallies) - 20} more rallies",
                self.styles['BodyText']
            ))
        
        self.elements.append(PageBreak())
    
    def _add_player_performance_a(self):
        """Add Player A performance section"""
        self._add_player_section('A', self.results.get('player_a', 'Player A'))
    
    def _add_player_performance_b(self):
        """Add Player B performance section"""
        self._add_player_section('B', self.results.get('player_b', 'Player B'))
    
    def _add_player_section(self, player_key: str, player_name: str):
        """Add performance section for a player"""
        self.elements.append(Paragraph(
            f"{player_name} Performance Analysis",
            self.styles['SectionTitle']
        ))
        
        stats = self.results.get('statistics', {})
        
        # Player stats
        shot_dist = stats.get('shot_distribution_by_player', {})
        player_shots = shot_dist.get(f'player_{player_key.lower()}', {})
        
        if player_shots:
            self.elements.append(Paragraph("Shot Distribution", self.styles['SubsectionTitle']))
            
            # Create shot table
            sorted_shots = sorted(player_shots.items(), key=lambda x: x[1], reverse=True)
            table_data = [['Shot Type', 'Count', 'Percentage']]
            total = sum(player_shots.values())
            
            for shot_type, count in sorted_shots[:10]:
                pct = f"{(count/total*100):.1f}%" if total > 0 else "0%"
                table_data.append([shot_type, str(count), pct])
            
            table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aab7b8')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            self.elements.append(table)
            self.elements.append(Spacer(1, 0.3*inch))
        
        # Error analysis
        error_stats = stats.get('error_analysis', {})
        player_errors = error_stats.get(f'player_{player_key.lower()}', {})
        
        if player_errors:
            self.elements.append(Paragraph("Error Analysis", self.styles['SubsectionTitle']))
            
            error_text = f"""
            <b>Net Errors:</b> {player_errors.get('net', 0)}<br/>
            <b>Out Errors:</b> {player_errors.get('out', 0)}<br/>
            <b>Tactical Errors:</b> {player_errors.get('tactical', 0)}
            """
            self.elements.append(Paragraph(error_text, self.styles['BodyText']))
        
        # Player comparison metrics
        comparison = stats.get('player_comparison', {})
        player_metrics = comparison.get(f'player_{player_key.lower()}', {})
        
        if player_metrics:
            self.elements.append(Paragraph("Performance Metrics", self.styles['SubsectionTitle']))
            
            metrics_text = f"""
            <b>Attack Rating:</b> {player_metrics.get('attack', 0)}/100<br/>
            <b>Defense Rating:</b> {player_metrics.get('defense', 0)}/100<br/>
            <b>Net Play Rating:</b> {player_metrics.get('net_play', 0)}/100<br/>
            <b>Power Rating:</b> {player_metrics.get('power', 0)}/100<br/>
            <b>Consistency Rating:</b> {player_metrics.get('consistency', 0)}/100
            """
            self.elements.append(Paragraph(metrics_text, self.styles['BodyText']))
        
        self.elements.append(PageBreak())
    
    def _add_shot_analysis(self):
        """Add shot distribution analysis section"""
        self.elements.append(Paragraph("Shot Distribution Analysis", self.styles['SectionTitle']))
        
        # Overall distribution graph
        shot_dist_path = os.path.join(self.graphs_dir, 'shot_distribution.png')
        if os.path.exists(shot_dist_path):
            img = Image(shot_dist_path, width=6*inch, height=3*inch)
            self.elements.append(img)
            self.elements.append(Spacer(1, 0.3*inch))
        
        # Player comparison graph
        comparison_path = os.path.join(self.graphs_dir, 'player_shot_comparison.png')
        if os.path.exists(comparison_path):
            img = Image(comparison_path, width=6*inch, height=3*inch)
            self.elements.append(img)
        
        self.elements.append(PageBreak())
    
    def _add_mistake_analysis(self):
        """Add comprehensive mistake analysis section"""
        self.elements.append(Paragraph("Mistake Analysis", self.styles['SectionTitle']))
        
        # Error chart
        error_path = os.path.join(self.graphs_dir, 'error_analysis.png')
        if os.path.exists(error_path):
            img = Image(error_path, width=5*inch, height=3*inch)
            self.elements.append(img)
            self.elements.append(Spacer(1, 0.3*inch))
        
        # List all mistakes
        rallies = self.results.get('rallies', [])
        all_mistakes = []
        
        for rally in rallies:
            for mistake in rally.get('mistakes', []):
                mistake['rally_number'] = rally.get('rally_number', 0)
                all_mistakes.append(mistake)
        
        if all_mistakes:
            self.elements.append(Paragraph(
                f"Total Mistakes Detected: {len(all_mistakes)}",
                self.styles['SubsectionTitle']
            ))
            
            # Group by player
            player_a_mistakes = [m for m in all_mistakes if 'A' in m.get('player', '')]
            player_b_mistakes = [m for m in all_mistakes if 'B' in m.get('player', '')]
            
            # Player A mistakes
            if player_a_mistakes:
                player_a = self.results.get('player_a', 'Player A')
                self.elements.append(Paragraph(
                    f"{player_a} Mistakes ({len(player_a_mistakes)})",
                    self.styles['SubsectionTitle']
                ))
                
                for m in player_a_mistakes[:5]:
                    self.elements.append(Paragraph(
                        f"Rally {m.get('rally_number', 0)}: {m.get('description', '')}",
                        self.styles['MistakeText']
                    ))
                    self.elements.append(Paragraph(
                        f"→ {m.get('improvement_suggestion', '')}",
                        self.styles['SuggestionText']
                    ))
                
                if len(player_a_mistakes) > 5:
                    self.elements.append(Paragraph(
                        f"... and {len(player_a_mistakes) - 5} more mistakes",
                        self.styles['BodyText']
                    ))
            
            # Player B mistakes
            if player_b_mistakes:
                player_b = self.results.get('player_b', 'Player B')
                self.elements.append(Paragraph(
                    f"{player_b} Mistakes ({len(player_b_mistakes)})",
                    self.styles['SubsectionTitle']
                ))
                
                for m in player_b_mistakes[:5]:
                    self.elements.append(Paragraph(
                        f"Rally {m.get('rally_number', 0)}: {m.get('description', '')}",
                        self.styles['MistakeText']
                    ))
                    self.elements.append(Paragraph(
                        f"→ {m.get('improvement_suggestion', '')}",
                        self.styles['SuggestionText']
                    ))
                
                if len(player_b_mistakes) > 5:
                    self.elements.append(Paragraph(
                        f"... and {len(player_b_mistakes) - 5} more mistakes",
                        self.styles['BodyText']
                    ))
        
        self.elements.append(PageBreak())
    
    def _add_statistical_graphs(self):
        """Add all statistical graphs section"""
        self.elements.append(Paragraph("Statistical Visualizations", self.styles['SectionTitle']))
        
        # Player comparison radar
        radar_path = os.path.join(self.graphs_dir, 'player_comparison_radar.png')
        if os.path.exists(radar_path):
            self.elements.append(Paragraph("Player Comparison", self.styles['SubsectionTitle']))
            img = Image(radar_path, width=4.5*inch, height=4.5*inch)
            self.elements.append(img)
            self.elements.append(Spacer(1, 0.3*inch))
        
        # Rally length histogram
        histogram_path = os.path.join(self.graphs_dir, 'rally_length_histogram.png')
        if os.path.exists(histogram_path):
            self.elements.append(Paragraph("Rally Length Distribution", self.styles['SubsectionTitle']))
            img = Image(histogram_path, width=5*inch, height=3*inch)
            self.elements.append(img)
            self.elements.append(Spacer(1, 0.3*inch))
        
        # Momentum graph
        momentum_path = os.path.join(self.graphs_dir, 'momentum_graph.png')
        if os.path.exists(momentum_path):
            self.elements.append(Paragraph("Match Momentum", self.styles['SubsectionTitle']))
            img = Image(momentum_path, width=6*inch, height=2.5*inch)
            self.elements.append(img)
        
        # Landing heatmaps
        heatmap_a = os.path.join(self.graphs_dir, 'landing_heatmap_a.png')
        heatmap_b = os.path.join(self.graphs_dir, 'landing_heatmap_b.png')
        
        if os.path.exists(heatmap_a) or os.path.exists(heatmap_b):
            self.elements.append(PageBreak())
            self.elements.append(Paragraph("Landing Position Heatmaps", self.styles['SubsectionTitle']))
            
            if os.path.exists(heatmap_a):
                img = Image(heatmap_a, width=3*inch, height=4.5*inch)
                self.elements.append(img)
            
            if os.path.exists(heatmap_b):
                img = Image(heatmap_b, width=3*inch, height=4.5*inch)
                self.elements.append(img)
        
        self.elements.append(PageBreak())
    
    def _add_recommendations(self):
        """Add improvement recommendations section"""
        self.elements.append(Paragraph("Improvement Recommendations", self.styles['SectionTitle']))
        
        # Generate recommendations based on analysis
        player_a = self.results.get('player_a', 'Player A')
        player_b = self.results.get('player_b', 'Player B')
        
        stats = self.results.get('statistics', {})
        error_stats = stats.get('error_analysis', {})
        
        # Player A recommendations
        self.elements.append(Paragraph(
            f"Recommendations for {player_a}",
            self.styles['SubsectionTitle']
        ))
        
        a_errors = error_stats.get('player_a', {})
        a_recommendations = self._generate_recommendations(a_errors, 'A')
        
        for rec in a_recommendations:
            self.elements.append(Paragraph(f"• {rec}", self.styles['BodyText']))
        
        self.elements.append(Spacer(1, 0.3*inch))
        
        # Player B recommendations
        self.elements.append(Paragraph(
            f"Recommendations for {player_b}",
            self.styles['SubsectionTitle']
        ))
        
        b_errors = error_stats.get('player_b', {})
        b_recommendations = self._generate_recommendations(b_errors, 'B')
        
        for rec in b_recommendations:
            self.elements.append(Paragraph(f"• {rec}", self.styles['BodyText']))
        
        # General tips
        self.elements.append(Spacer(1, 0.5*inch))
        self.elements.append(Paragraph("General Training Tips", self.styles['SubsectionTitle']))
        
        general_tips = [
            "Focus on footwork drills to improve court coverage.",
            "Practice shot placement accuracy with target training.",
            "Work on consistency under pressure situations.",
            "Develop tactical awareness by studying opponent patterns.",
            "Improve physical conditioning for longer rallies."
        ]
        
        for tip in general_tips:
            self.elements.append(Paragraph(f"• {tip}", self.styles['BodyText']))
        
        # Report footer
        self.elements.append(Spacer(1, 1*inch))
        self.elements.append(Paragraph(
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            self.styles['Subtitle']
        ))
        self.elements.append(Paragraph(
            "Badminton Analysis Platform - AI-Powered Match Analysis",
            self.styles['Subtitle']
        ))
    
    def _generate_recommendations(self, errors: Dict, player: str) -> List[str]:
        """Generate specific recommendations based on error patterns"""
        recommendations = []
        
        net_errors = errors.get('net', 0)
        out_errors = errors.get('out', 0)
        tactical_errors = errors.get('tactical', 0)
        
        if net_errors > 3:
            recommendations.append(
                "Focus on lifting shots higher to clear the net consistently. "
                "Practice net clearance drills with graduated heights."
            )
        elif net_errors > 0:
            recommendations.append(
                "Minor net errors detected. Pay attention to racket angle during net shots."
            )
        
        if out_errors > 3:
            recommendations.append(
                "Work on shot control and court awareness. Practice hitting to specific "
                "targets within the court boundaries."
            )
        elif out_errors > 0:
            recommendations.append(
                "A few out-of-bounds errors occurred. Focus on controlling power shots."
            )
        
        if tactical_errors > 2:
            recommendations.append(
                "Develop better shot selection skills. Study opponent patterns and "
                "choose shots based on the situation rather than habit."
            )
        
        if not recommendations:
            recommendations.append(
                "Good overall performance! Continue refining techniques and "
                "maintaining consistency."
            )
        
        return recommendations
