"""
Production PowerPoint (.pptx) Presentation Builder
Generates 16:9 widescreen, visually styled slides using python-pptx.
Implements modern dark-mode aesthetics, custom card layouts, and monospace code containers.
"""

import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("PPTXBuilder")

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False
    logger.warning("python-pptx library not found in local environment. Run 'pip install -r requirements.txt'. Presentation creation will generate mock artifact.")
    # Safe class-level mock stubs when pptx is not installed
    class RGBColor:
        def __init__(self, r, g, b): pass
    def Inches(val): return val
    def Pt(val): return val
    class PP_ALIGN:
        CENTER = 2
    class MSO_SHAPE:
        RECTANGLE = 1
        ROUNDED_RECTANGLE = 5




class PPTXBuilder:
    """
    Renders professional 16:9 widescreen presentation decks from structured slide JSON.
    """

    # Modern Dark Theme Color Palette
    COLOR_BG = RGBColor(15, 23, 42)          # Deep Slate #0F172A
    COLOR_CARD = RGBColor(30, 41, 59)        # Slate Card #1E293B
    COLOR_BORDER = RGBColor(51, 65, 85)      # Slate Border #334155
    COLOR_TEXT_PRIMARY = RGBColor(248, 250, 252) # Snow White #F8FAFC
    COLOR_TEXT_MUTED = RGBColor(148, 163, 184)   # Slate Muted #94A3B8
    COLOR_ACCENT = RGBColor(16, 185, 129)    # Emerald #10B981
    COLOR_CYAN = RGBColor(6, 182, 212)       # Electric Cyan #06B6D4
    COLOR_AMBER = RGBColor(245, 158, 11)     # Amber Alert #F59E0B
    COLOR_RED = RGBColor(239, 68, 68)        # Red Danger #EF4444
    COLOR_CODE_BG = RGBColor(2, 6, 23)       # Dark Obsidian #020617
    COLOR_CODE_TEXT = RGBColor(56, 189, 248) # Sky Blue Monospace #38BDF8

    FONT_HEADING = "Segoe UI"
    FONT_BODY = "Segoe UI"
    FONT_CODE = "Consolas"

    def __init__(self):
        pass

    def build_deck(self, slide_data: Dict[str, Any], output_path: str) -> str:
        """
        Creates a 16:9 widescreen presentation and saves it to output_path.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if not HAS_PPTX:
            logger.warning(f"python-pptx is not installed. Writing slide payload to {output_path}.json for inspection.")
            with open(f"{output_path}.json", "w", encoding="utf-8") as f:
                json.dump(slide_data, f, indent=2)
            with open(output_path, "wb") as f:
                f.write(b"PK\x03\x04[MOCK_PPTX_FILE_PENDING_PIP_INSTALL]")
            return output_path

        prs = Presentation()
        # Set 16:9 widescreen dimensions (13.333 x 7.5 inches)
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        blank_layout = prs.slide_layouts[6] # completely blank layout

        slides = slide_data.get("slides", [])
        deck_title = slide_data.get("deck_title", "Machine Learning Masterclass")
        module_name = slide_data.get("module", "Machine Learning Foundations")
        day_num = slide_data.get("day_number", 1)

        for slide_dict in slides:
            slide_type = slide_dict.get("slide_type", "concept")
            slide = prs.slides.add_slide(blank_layout)
            self._set_dark_background(slide)

            if slide_type == "title":
                self._render_title_slide(slide, slide_dict, day_num, module_name)
            elif slide_type == "code":
                self._render_code_slide(slide, slide_dict, day_num)
            elif slide_type == "diagram":
                self._render_diagram_slide(slide, slide_dict, day_num)
            elif slide_type == "pitfalls":
                self._render_pitfalls_slide(slide, slide_dict, day_num)
            elif slide_type == "interview":
                self._render_interview_slide(slide, slide_dict, day_num)
            else:
                self._render_standard_slide(slide, slide_dict, day_num)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        prs.save(output_path)
        logger.info(f"Presentation successfully generated at: {output_path}")
        return output_path

    def _set_dark_background(self, slide):
        """Adds a full-bleed dark rectangle background."""
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5)
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = self.COLOR_BG
        bg.line.fill.background()

    def _render_header(self, slide, title_text: str, subtitle_text: str, day_num: int):
        """Renders standard top header with day badge and title."""
        # Top banner badge
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(3.0), Inches(0.4))
        tf_badge = badge_box.text_frame
        tf_badge.word_wrap = True
        p_badge = tf_badge.paragraphs[0]
        p_badge.text = f"DAY {day_num:02d} • ML PRODUCTION SPRINT"
        p_badge.font.name = self.FONT_HEADING
        p_badge.font.size = Pt(11)
        p_badge.font.bold = True
        p_badge.font.color.rgb = self.COLOR_ACCENT

        # Slide Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = self.FONT_HEADING
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = self.COLOR_TEXT_PRIMARY

        # Optional Subtitle
        if subtitle_text:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.5), Inches(0.4))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle_text
            p_sub.font.name = self.FONT_BODY
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = self.COLOR_TEXT_MUTED

        # Thin Accent Divider Line
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.95), Inches(11.733), Inches(0.02)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = self.COLOR_BORDER
        line.line.fill.background()

    def _render_title_slide(self, slide, data: Dict[str, Any], day_num: int, module_name: str):
        """Renders the hero cover title slide."""
        # Decorative card glow
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = self.COLOR_CARD
        card.line.color.rgb = self.COLOR_BORDER
        card.line.width = Pt(1.5)

        # Module Tag
        tag_box = slide.shapes.add_textbox(Inches(1.6), Inches(1.7), Inches(9.0), Inches(0.5))
        tf_tag = tag_box.text_frame
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = f"MODULE: {module_name.upper()}  |  DAY {day_num:02d} OF 30"
        p_tag.font.name = self.FONT_HEADING
        p_tag.font.size = Pt(13)
        p_tag.font.bold = True
        p_tag.font.color.rgb = self.COLOR_ACCENT

        # Master Title
        title_box = slide.shapes.add_textbox(Inches(1.6), Inches(2.3), Inches(10.0), Inches(1.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = data.get("title", f"Day {day_num}")
        p_title.font.name = self.FONT_HEADING
        p_title.font.size = Pt(36)
        p_title.font.bold = True
        p_title.font.color.rgb = self.COLOR_TEXT_PRIMARY

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(1.6), Inches(4.1), Inches(9.5), Inches(1.0))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = data.get("subtitle", "Autonomous Cloud Learning Pipeline • Zero-Cost Production Stack")
        p_sub.font.name = self.FONT_BODY
        p_sub.font.size = Pt(16)
        p_sub.font.color.rgb = self.COLOR_TEXT_MUTED

        # Footer badge
        foot_box = slide.shapes.add_textbox(Inches(1.6), Inches(5.3), Inches(9.5), Inches(0.5))
        tf_foot = foot_box.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = "⚡ Cloud Orchestrated • Verified Sandbox Execution • Mathematical Rigor"
        p_foot.font.name = self.FONT_BODY
        p_foot.font.size = Pt(12)
        p_foot.font.color.rgb = self.COLOR_CYAN

    def _render_standard_slide(self, slide, data: Dict[str, Any], day_num: int):
        """Renders standard content slide with structured bullet points inside cards."""
        self._render_header(slide, data.get("title", ""), data.get("subtitle", ""), day_num)

        bullets = data.get("bullets", [])
        if not bullets:
            return

        # Render content inside a styled container card
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), Inches(11.733), Inches(4.7)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = self.COLOR_CARD
        card.line.color.rgb = self.COLOR_BORDER
        card.line.width = Pt(1)

        # Bullets text frame
        tb = slide.shapes.add_textbox(Inches(1.2), Inches(2.4), Inches(10.9), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"▸  {bullet}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(15)
            p.font.color.rgb = self.COLOR_TEXT_PRIMARY
            p.space_after = Pt(16)

    def _render_code_slide(self, slide, data: Dict[str, Any], day_num: int):
        """Renders slide with side-by-side or stacked code container."""
        self._render_header(slide, data.get("title", ""), data.get("subtitle", ""), day_num)

        # Left Column: Key Principles (Width: 4.8 inches)
        left_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), Inches(4.6), Inches(4.7)
        )
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = self.COLOR_CARD
        left_card.line.color.rgb = self.COLOR_BORDER

        tb_left = slide.shapes.add_textbox(Inches(1.0), Inches(2.4), Inches(4.2), Inches(4.3))
        tf_left = tb_left.text_frame
        tf_left.word_wrap = True

        bullets = data.get("bullets", ["Production-ready Python implementation", "Strict pipeline encapsulation"])
        for i, bullet in enumerate(bullets):
            p = tf_left.paragraphs[0] if i == 0 else tf_left.add_paragraph()
            p.text = f"• {bullet}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(13)
            p.font.color.rgb = self.COLOR_TEXT_PRIMARY
            p.space_after = Pt(12)

        # Right Column: Monospace Code Container (Width: 6.8 inches)
        code_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(2.2), Inches(6.9), Inches(4.7)
        )
        code_card.fill.solid()
        code_card.fill.fore_color.rgb = self.COLOR_CODE_BG
        code_card.line.color.rgb = self.COLOR_BORDER
        code_card.line.width = Pt(1.5)

        # Code header pill
        tb_pill = slide.shapes.add_textbox(Inches(5.8), Inches(2.3), Inches(4.0), Inches(0.3))
        tf_pill = tb_pill.text_frame
        p_pill = tf_pill.paragraphs[0]
        p_pill.text = "PYTHON SANDBOX • VERIFIED"
        p_pill.font.name = self.FONT_CODE
        p_pill.font.size = Pt(9)
        p_pill.font.bold = True
        p_pill.font.color.rgb = self.COLOR_ACCENT

        # Code snippet text
        tb_code = slide.shapes.add_textbox(Inches(5.8), Inches(2.6), Inches(6.5), Inches(4.1))
        tf_code = tb_code.text_frame
        tf_code.word_wrap = True

        snippet = data.get("code_snippet", "# Production pipeline code snippet\nimport numpy as np\nimport sklearn")
        lines = snippet.split("\n")
        for i, line in enumerate(lines[:14]): # fit up to 14 lines cleanly
            p = tf_code.paragraphs[0] if i == 0 else tf_code.add_paragraph()
            p.text = line
            p.font.name = self.FONT_CODE
            p.font.size = Pt(11)
            p.font.color.rgb = self.COLOR_CODE_TEXT
            p.space_after = Pt(2)

    def _render_diagram_slide(self, slide, data: Dict[str, Any], day_num: int):
        """Renders an architectural diagram flow slide."""
        self._render_header(slide, data.get("title", ""), data.get("subtitle", ""), day_num)

        # Top area: Diagram flow card
        diagram_text = data.get("diagram_text", "[Stage 1] ──> [Stage 2] ──> [Stage 3] ──> [Output]")
        diag_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), Inches(11.733), Inches(1.8)
        )
        diag_card.fill.solid()
        diag_card.fill.fore_color.rgb = self.COLOR_CODE_BG
        diag_card.line.color.rgb = self.COLOR_CYAN
        diag_card.line.width = Pt(1.5)

        tb_diag = slide.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(11.1), Inches(1.2))
        tf_diag = tb_diag.text_frame
        tf_diag.word_wrap = True
        p_diag = tf_diag.paragraphs[0]
        p_diag.alignment = PP_ALIGN.CENTER
        p_diag.text = diagram_text
        p_diag.font.name = self.FONT_CODE
        p_diag.font.size = Pt(14)
        p_diag.font.bold = True
        p_diag.font.color.rgb = self.COLOR_CYAN

        # Bottom area: Architectural bullet points
        bot_card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.2), Inches(11.733), Inches(2.7)
        )
        bot_card.fill.solid()
        bot_card.fill.fore_color.rgb = self.COLOR_CARD
        bot_card.line.color.rgb = self.COLOR_BORDER

        tb_bot = slide.shapes.add_textbox(Inches(1.1), Inches(4.35), Inches(11.1), Inches(2.4))
        tf_bot = tb_bot.text_frame
        tf_bot.word_wrap = True

        bullets = data.get("bullets", [])
        for i, bullet in enumerate(bullets):
            p = tf_bot.paragraphs[0] if i == 0 else tf_bot.add_paragraph()
            p.text = f"⚡ {bullet}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.color.rgb = self.COLOR_TEXT_PRIMARY
            p.space_after = Pt(10)

    def _render_pitfalls_slide(self, slide, data: Dict[str, Any], day_num: int):
        """Renders a high-visibility data leakage & production hazards slide."""
        self._render_header(slide, data.get("title", "Common Pitfalls & Data Leakage Warnings"), data.get("subtitle", "Production Hazard Analysis"), day_num)

        bullets = data.get("bullets", [])
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), Inches(11.733), Inches(4.7)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = self.COLOR_CARD
        card.line.color.rgb = self.COLOR_RED
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(1.2), Inches(2.4), Inches(10.9), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"⚠️  {bullet}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.color.rgb = self.COLOR_TEXT_PRIMARY
            p.space_after = Pt(14)

    def _render_interview_slide(self, slide, data: Dict[str, Any], day_num: int):
        """Renders technical interview defense questions."""
        self._render_header(slide, data.get("title", "Senior Technical Interview Edge Cases"), data.get("subtitle", "Engineering Trade-offs & Deep Questions"), day_num)

        bullets = data.get("bullets", [])
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.2), Inches(11.733), Inches(4.7)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = self.COLOR_CARD
        card.line.color.rgb = self.COLOR_AMBER
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(1.2), Inches(2.4), Inches(10.9), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"🎯  {bullet}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(14)
            p.font.color.rgb = self.COLOR_TEXT_PRIMARY
            p.space_after = Pt(12)
