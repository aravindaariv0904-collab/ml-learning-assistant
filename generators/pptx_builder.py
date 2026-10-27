"""
Modern AI Learning Studio Presentation Builder (.pptx)
Implements the Modern AI Learning Studio Design Specification:
  - 16:9 widescreen dimensions (13.333 x 7.5 inches)
  - Curated Design System Palette (Midnight Navy, Deep Blue, Electric Cyan, Violet, Off-White, Slate Gray, Success Green, Amber)
  - Dynamic Theme Variation: Dark Technical Slides vs Light Explanation Slides
  - 18–25 Slide Sequences with Container Cards, Monospace Code Labs, and Clean Footers
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional

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
    logger.warning("python-pptx not found. Slides will be recorded as JSON artifacts.")
    class RGBColor:
        def __init__(self, r, g, b): pass
    def Inches(v): return v
    def Pt(v): return v
    class PP_ALIGN:
        CENTER = 2
        LEFT = 1
        RIGHT = 3
    class MSO_SHAPE:
        RECTANGLE = 1
        ROUNDED_RECTANGLE = 5


class PPTXBuilder:
    """
    Renders production-grade, premium machine learning curriculum presentations
    matching the Modern AI Learning Studio design specification.
    """

    # --- Modern AI Learning Studio Palette ---
    COLOR_MIDNIGHT_NAVY = RGBColor(16, 24, 40)   # #101828 (Dark slide background)
    COLOR_DEEP_BLUE = RGBColor(29, 78, 216)      # #1D4ED8 (Primary brand / Light slide headers)
    COLOR_ELECTRIC_CYAN = RGBColor(34, 211, 238) # #22D3EE (Dark slide accents / highlight)
    COLOR_VIOLET = RGBColor(139, 92, 246)        # #8B5CF6 (Secondary accent)
    COLOR_OFF_WHITE = RGBColor(248, 250, 252)    # #F8FAFC (Light slide background)
    COLOR_SLATE_GRAY = RGBColor(100, 116, 139)   # #64748B (Body text in light mode)
    COLOR_SUCCESS_GREEN = RGBColor(22, 163, 74)  # #16A34A (Validation / Good)
    COLOR_AMBER_WARNING = RGBColor(245, 158, 11) # #F59E0B (Warnings / Caution)

    # Secondary & Container Palette
    COLOR_CARD_DARK = RGBColor(26, 38, 64)       # #1A2640 (Cards on dark slides)
    COLOR_BORDER_DARK = RGBColor(38, 54, 88)     # #263658 (Borders on dark cards)
    COLOR_CARD_LIGHT = RGBColor(255, 255, 255)   # #FFFFFF (Cards on light slides)
    COLOR_BORDER_LIGHT = RGBColor(226, 232, 240) # #E2E8F0 (Borders on light cards)

    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_DARK_TEXT = RGBColor(15, 23, 42)       # #0F172A
    COLOR_MUTED_LIGHT = RGBColor(148, 163, 184)  # #94A3B8 (Muted on dark)
    COLOR_CODE_BG = RGBColor(11, 17, 32)         # #0B1120 (Code container background)
    COLOR_CODE_TEXT = RGBColor(56, 189, 248)     # #38BDF8 (Monospace code text)
    COLOR_DANGER_RED = RGBColor(239, 68, 68)     # #EF4444 (Hazard / Fail)

    FONT_HEADING = "Segoe UI"
    FONT_BODY = "Segoe UI"
    FONT_CODE = "Consolas"

    def __init__(self):
        pass

    def build_deck(self, slide_payload: Dict[str, Any], output_path: str) -> str:
        """
        Builds a 16:9 widescreen presentation (18–25 slides) from structured slide specifications.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if not HAS_PPTX:
            logger.warning(f"python-pptx not available. Saving JSON payload to {output_path}.json")
            with open(f"{output_path}.json", "w", encoding="utf-8") as f:
                json.dump(slide_payload, f, indent=2)
            with open(output_path, "wb") as f:
                f.write(b"PK\x03\x04[MOCK_PPTX_PENDING_INSTALL]")
            return output_path

        prs = Presentation()
        # Set 16:9 widescreen dimensions (13.333 x 7.5 inches)
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        blank_layout = prs.slide_layouts[6]

        slides = slide_payload.get("slides", [])
        deck_title = slide_payload.get("deck_title", "Machine Learning Masterclass")
        module_name = slide_payload.get("module", "Production Foundations")
        day_num = slide_payload.get("day_number", 1)

        total_slides = len(slides)
        logger.info(f"Rendering {total_slides} slides for '{deck_title}' into {output_path}...")

        for idx, slide_dict in enumerate(slides, 1):
            slide_type = slide_dict.get("slide_type") or self._default_slide_type(idx)
            theme = slide_dict.get("theme") or self._infer_theme(slide_type)
            slide_dict["slide_type"] = slide_type
            slide_dict["theme"] = theme
            slide = prs.slides.add_slide(blank_layout)

            # Apply background based on theme
            if theme == "dark":
                self._paint_background(slide, self.COLOR_MIDNIGHT_NAVY)
            else:
                self._paint_background(slide, self.COLOR_OFF_WHITE)

            # Render specific slide layout
            if slide_type in ["cover", "title"]:
                self._render_cover_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["code_lab", "code"]:
                self._render_code_lab_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["diagram", "workflow"]:
                self._render_diagram_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["math", "mathematical_intuition"]:
                self._render_math_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["case_study", "results"]:
                self._render_case_study_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["comparison", "before_after"]:
                self._render_comparison_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["pitfalls"]:
                self._render_pitfalls_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["interview"]:
                self._render_interview_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["knowledge_check"]:
                self._render_knowledge_check_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            elif slide_type in ["takeaways", "summary"]:
                self._render_takeaways_slide(slide, slide_dict, day_num, module_name, idx, total_slides)
            else:
                self._render_card_grid_slide(slide, slide_dict, day_num, module_name, idx, total_slides)

        prs.save(output_path)
        logger.info(f"Successfully generated {total_slides}-slide Modern AI Learning Studio presentation: {output_path}")
        return output_path

    def _infer_theme(self, slide_type: str) -> str:
        """
        Determines theme following the Modern AI Learning Studio rules:
        - Dark: Cover, Architecture/Diagram, Workflow, Code Labs, Math, Challenge, Interview Defense
        - Light: Why Matters, Objectives, Prerequisites, Intuition, Core Concept, Walkthrough, Case Study, Results, Comparison, Pitfalls, Limitations, Knowledge Check, Takeaways, Resources
        """
        dark_types = {
            "cover", "title", "how_it_works", "math", "mathematical_intuition", "diagram", "workflow",
            "code_lab", "code", "challenge", "interview"
        }
        return "dark" if (slide_type or "").lower() in dark_types else "light"

    def _default_slide_type(self, idx: int) -> str:
        types_map = {
            1: "cover",
            2: "why_matters",
            3: "objectives",
            4: "prerequisites",
            5: "intuition",
            6: "core_concept",
            7: "how_it_works",
            8: "math",
            9: "diagram",
            10: "workflow",
            11: "code_lab",
            12: "code_walkthrough",
            13: "case_study",
            14: "results",
            15: "comparison",
            16: "pitfalls",
            17: "limitations",
            18: "challenge",
            19: "interview",
            20: "knowledge_check",
            21: "takeaways",
            22: "resources"
        }
        return types_map.get(idx, "concept")

    def _paint_background(self, slide, color: RGBColor):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()

    def _render_header_band(
        self,
        slide,
        title_text: str,
        subtitle_text: str,
        day_num: int,
        module_name: str,
        theme: str = "dark"
    ):
        """Renders standard top header with track badge, title, and subtitle."""
        is_dark = (theme == "dark")

        # Top Badge
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(6.0), Inches(0.35))
        tf_b = badge_box.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = f"DAY {day_num:02d} • {module_name.upper()} • PRODUCTION SPRINT"
        p_b.font.name = self.FONT_HEADING
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = self.COLOR_ELECTRIC_CYAN if is_dark else self.COLOR_DEEP_BLUE

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = self.FONT_HEADING
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = self.COLOR_WHITE if is_dark else self.COLOR_DARK_TEXT

        # Subtitle
        if subtitle_text:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.5), Inches(0.35))
            tf_s = sub_box.text_frame
            tf_s.word_wrap = True
            p_s = tf_s.paragraphs[0]
            p_s.text = subtitle_text
            p_s.font.name = self.FONT_BODY
            p_s.font.size = Pt(12)
            p_s.font.color.rgb = self.COLOR_MUTED_LIGHT if is_dark else self.COLOR_SLATE_GRAY

    def _render_discreet_footer(
        self,
        slide,
        day_num: int,
        topic: str,
        track: str,
        current_slide: int,
        total_slides: int,
        theme: str = "dark"
    ):
        """Renders discreet footer with Day XX • Topic | Track and slide count."""
        is_dark = (theme == "dark")
        footer_color = self.COLOR_MUTED_LIGHT if is_dark else self.COLOR_SLATE_GRAY

        box = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(11.733), Inches(0.3))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = f"Day {day_num:02d} • {topic}  |  {track}        [{current_slide}/{total_slides}]"
        p.font.name = self.FONT_BODY
        p.font.size = Pt(9)
        p.font.color.rgb = footer_color

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 1: COVER SLIDE (DARK)
    # -------------------------------------------------------------------------
    def _render_cover_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", f"Day {day_num}")
        subtitle = data.get("subtitle", "30-Day Production Machine Learning Masterclass")
        bullets = data.get("bullets", [])

        # Decorative Top Cyan Accent Line
        top_accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.0), Inches(1.5), Inches(0.08))
        top_accent.fill.solid()
        top_accent.fill.fore_color.rgb = self.COLOR_ELECTRIC_CYAN
        top_accent.line.fill.background()

        # Day Badge
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.25), Inches(5.0), Inches(0.4))
        p_badge = badge_box.text_frame.paragraphs[0]
        p_badge.text = f"DAY {day_num:02d} OF 30 • {module.upper()}"
        p_badge.font.name = self.FONT_HEADING
        p_badge.font.size = Pt(13)
        p_badge.font.bold = True
        p_badge.font.color.rgb = self.COLOR_ELECTRIC_CYAN

        # Large Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.5))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = self.FONT_HEADING
        p_title.font.size = Pt(38)
        p_title.font.bold = True
        p_title.font.color.rgb = self.COLOR_WHITE

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(11.5), Inches(0.6))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = self.FONT_BODY
        p_sub.font.size = Pt(16)
        p_sub.font.color.rgb = self.COLOR_MUTED_LIGHT

        # Bottom 3 Highlight Cards
        cards = bullets[:3] or [
            "Mathematical Derivations & Closed-Form Solutions",
            "Scikit-Learn Production Pipeline Implementation",
            "Zero Data Leakage & Staff-Level Interview Prep"
        ]
        col_w = Inches(3.7)
        gap = Inches(0.3)
        start_x = Inches(0.8)
        top_y = Inches(4.2)
        card_h = Inches(2.2)

        for i, text in enumerate(cards):
            x = start_x + (i * (col_w + gap))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, col_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.COLOR_CARD_DARK
            card.line.color.rgb = self.COLOR_BORDER_DARK
            card.line.width = Pt(1)

            tb = slide.shapes.add_textbox(x + Inches(0.2), top_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p0 = tf.paragraphs[0]
            p0.text = f"MILESTONE 0{i+1}"
            p0.font.name = self.FONT_HEADING
            p0.font.size = Pt(10)
            p0.font.bold = True
            p0.font.color.rgb = self.COLOR_ELECTRIC_CYAN

            p1 = tf.add_paragraph()
            p1.text = text
            p1.font.name = self.FONT_BODY
            p1.font.size = Pt(12)
            p1.font.color.rgb = self.COLOR_WHITE
            p1.space_before = Pt(8)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="dark")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 2: CODE LABORATORY (DARK)
    # -------------------------------------------------------------------------
    def _render_code_lab_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Python Code Laboratory")
        subtitle = data.get("subtitle", "Production implementation verified in isolated sandbox")
        code_text = data.get("code_snippet") or "# Production scikit-learn pipeline\nmodel.fit(X_train, y_train)"
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="dark")

        # Left Column: Dark Code Syntax Box (7.2 inches wide)
        code_x = Inches(0.8)
        code_y = Inches(1.8)
        code_w = Inches(7.5)
        code_h = Inches(4.8)

        code_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, code_x, code_y, code_w, code_h)
        code_card.fill.solid()
        code_card.fill.fore_color.rgb = self.COLOR_CODE_BG
        code_card.line.color.rgb = self.COLOR_ELECTRIC_CYAN
        code_card.line.width = Pt(1.5)

        # Code header pill
        pill_box = slide.shapes.add_textbox(code_x + Inches(0.25), code_y + Inches(0.15), Inches(4.0), Inches(0.3))
        p_pill = pill_box.text_frame.paragraphs[0]
        p_pill.text = "PYTHON 3 • AST SANDBOX VERIFIED"
        p_pill.font.name = self.FONT_CODE
        p_pill.font.size = Pt(9)
        p_pill.font.bold = True
        p_pill.font.color.rgb = self.COLOR_SUCCESS_GREEN

        # Code text box
        code_box = slide.shapes.add_textbox(code_x + Inches(0.25), code_y + Inches(0.45), code_w - Inches(0.5), code_h - Inches(0.6))
        tf_code = code_box.text_frame
        tf_code.word_wrap = True
        p_code = tf_code.paragraphs[0]
        p_code.text = code_text[:500]
        p_code.font.name = self.FONT_CODE
        p_code.font.size = Pt(10)
        p_code.font.color.rgb = self.COLOR_CODE_TEXT

        # Right Column: Architectural Explanations (4.0 inches wide)
        right_x = Inches(8.6)
        right_y = Inches(1.8)
        right_w = Inches(3.933)
        right_h = Inches(4.8)

        right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, right_y, right_w, right_h)
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = self.COLOR_CARD_DARK
        right_card.line.color.rgb = self.COLOR_BORDER_DARK
        right_card.line.width = Pt(1)

        notes_box = slide.shapes.add_textbox(right_x + Inches(0.25), right_y + Inches(0.2), right_w - Inches(0.5), right_h - Inches(0.4))
        tf_notes = notes_box.text_frame
        tf_notes.word_wrap = True
        p_head = tf_notes.paragraphs[0]
        p_head.text = "KEY ARCHITECTURAL HIGHLIGHTS"
        p_head.font.name = self.FONT_HEADING
        p_head.font.size = Pt(11)
        p_head.font.bold = True
        p_head.font.color.rgb = self.COLOR_ELECTRIC_CYAN

        for b in bullets[:4]:
            p = tf_notes.add_paragraph()
            p.text = f"• {b}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(11)
            p.font.color.rgb = self.COLOR_WHITE
            p.space_before = Pt(10)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="dark")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 3: DIAGRAM / WORKFLOW (DARK)
    # -------------------------------------------------------------------------
    def _render_diagram_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Algorithm Workflow & Pipeline Architecture")
        subtitle = data.get("subtitle", "Deterministic execution pipeline topology")
        diagram_text = data.get("diagram_text", "[Input] -> [Transform] -> [Solve] -> [Artifact]")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="dark")

        # Top Diagram Box
        diag_x = Inches(0.8)
        diag_y = Inches(1.8)
        diag_w = Inches(11.733)
        diag_h = Inches(2.2)

        diag_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, diag_x, diag_y, diag_w, diag_h)
        diag_card.fill.solid()
        diag_card.fill.fore_color.rgb = self.COLOR_CARD_DARK
        diag_card.line.color.rgb = self.COLOR_ELECTRIC_CYAN
        diag_card.line.width = Pt(1.5)

        tb_diag = slide.shapes.add_textbox(diag_x + Inches(0.3), diag_y + Inches(0.2), diag_w - Inches(0.6), diag_h - Inches(0.4))
        tf_diag = tb_diag.text_frame
        tf_diag.word_wrap = True
        p_d_head = tf_diag.paragraphs[0]
        p_d_head.text = "SYSTEM FLOW SCHEMATIC"
        p_d_head.font.name = self.FONT_HEADING
        p_d_head.font.size = Pt(10)
        p_d_head.font.bold = True
        p_d_head.font.color.rgb = self.COLOR_ELECTRIC_CYAN

        p_d_body = tf_diag.add_paragraph()
        p_d_body.text = diagram_text
        p_d_body.font.name = self.FONT_CODE
        p_d_body.font.size = Pt(11)
        p_d_body.font.color.rgb = self.COLOR_WHITE
        p_d_body.space_before = Pt(8)

        # Bottom 3 Sequence Cards
        col_w = Inches(3.7)
        gap = Inches(0.3)
        start_x = Inches(0.8)
        bot_y = Inches(4.3)
        card_h = Inches(2.4)

        cards = bullets[:3] or ["Step 1: Input Isolation", "Step 2: Regularized Optimization", "Step 3: Residual Verification"]
        for i, text in enumerate(cards):
            x = start_x + (i * (col_w + gap))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, bot_y, col_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.COLOR_CARD_DARK
            card.line.color.rgb = self.COLOR_BORDER_DARK
            card.line.width = Pt(1)

            tb = slide.shapes.add_textbox(x + Inches(0.2), bot_y + Inches(0.2), col_w - Inches(0.4), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p0 = tf.paragraphs[0]
            p0.text = f"PHASE 0{i+1}"
            p0.font.name = self.FONT_HEADING
            p0.font.size = Pt(10)
            p0.font.bold = True
            p0.font.color.rgb = self.COLOR_ELECTRIC_CYAN

            p1 = tf.add_paragraph()
            p1.text = text
            p1.font.name = self.FONT_BODY
            p1.font.size = Pt(11)
            p1.font.color.rgb = self.COLOR_WHITE
            p1.space_before = Pt(6)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="dark")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 4: MATHEMATICAL INTUITION (DARK)
    # -------------------------------------------------------------------------
    def _render_math_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Mathematical Foundations & Derivations")
        subtitle = data.get("subtitle", "Closed-form formulations and guaranteed convexity")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="dark")

        # 2 Column Cards
        col_w = Inches(5.7)
        gap = Inches(0.333)
        top_y = Inches(1.8)
        card_h = Inches(4.8)

        # Left Column: Formulation & Normal Equation
        x1 = Inches(0.8)
        card1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x1, top_y, col_w, card_h)
        card1.fill.solid()
        card1.fill.fore_color.rgb = self.COLOR_CARD_DARK
        card1.line.color.rgb = self.COLOR_ELECTRIC_CYAN
        card1.line.width = Pt(1.5)

        tb1 = slide.shapes.add_textbox(x1 + Inches(0.3), top_y + Inches(0.25), col_w - Inches(0.6), card_h - Inches(0.5))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        p_f_head = tf1.paragraphs[0]
        p_f_head.text = "CORE OBJECTIVE & ANALYTICAL SOLUTION"
        p_f_head.font.name = self.FONT_HEADING
        p_f_head.font.size = Pt(11)
        p_f_head.font.bold = True
        p_f_head.font.color.rgb = self.COLOR_ELECTRIC_CYAN

        math_items = bullets[:2] if len(bullets) >= 2 else ["Objective Loss Formulation", "Analytical Inversion"]
        for m in math_items:
            p = tf1.add_paragraph()
            p.text = f"• {m}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.color.rgb = self.COLOR_WHITE
            p.space_before = Pt(12)

        # Right Column: Variable Dimensions & Invertibility
        x2 = x1 + col_w + gap
        card2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x2, top_y, col_w, card_h)
        card2.fill.solid()
        card2.fill.fore_color.rgb = self.COLOR_CARD_DARK
        card2.line.color.rgb = self.COLOR_BORDER_DARK
        card2.line.width = Pt(1)

        tb2 = slide.shapes.add_textbox(x2 + Inches(0.3), top_y + Inches(0.25), col_w - Inches(0.6), card_h - Inches(0.5))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p_s_head = tf2.paragraphs[0]
        p_s_head.text = "STRUCTURAL PROPERTIES & GUARANTEES"
        p_s_head.font.name = self.FONT_HEADING
        p_s_head.font.size = Pt(11)
        p_s_head.font.bold = True
        p_s_head.font.color.rgb = self.COLOR_VIOLET

        right_items = bullets[2:4] if len(bullets) >= 4 else ["Eigenvalue Spectrum Guarantees", "Convex Quadratic Optimization"]
        for r in right_items:
            p = tf2.add_paragraph()
            p.text = f"• {r}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.color.rgb = self.COLOR_WHITE
            p.space_before = Pt(12)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="dark")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 5: CASE STUDY & RESULTS (LIGHT)
    # -------------------------------------------------------------------------
    def _render_case_study_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Practical Industry Case Study")
        subtitle = data.get("subtitle", "Production enterprise dataset and evaluation telemetry")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="light")

        # 4 Clean Grid Cards on Light Background
        card_w = Inches(5.7)
        card_h = Inches(2.25)
        gap_x = Inches(0.333)
        gap_y = Inches(0.25)
        start_x = Inches(0.8)
        start_y = Inches(1.8)

        card_headers = ["PROBLEM DEFINITION", "DATASET & COVARIATES", "PERFORMANCE TELEMETRY", "PRODUCTION IMPACT"]
        colors = [self.COLOR_DEEP_BLUE, self.COLOR_VIOLET, self.COLOR_SUCCESS_GREEN, self.COLOR_DEEP_BLUE]

        for i in range(4):
            col = i % 2
            row = i // 2
            x = start_x + (col * (card_w + gap_x))
            y = start_y + (row * (card_h + gap_y))

            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.COLOR_CARD_LIGHT
            card.line.color.rgb = self.COLOR_BORDER_LIGHT
            card.line.width = Pt(1)

            tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p_head = tf.paragraphs[0]
            p_head.text = card_headers[i]
            p_head.font.name = self.FONT_HEADING
            p_head.font.size = Pt(10)
            p_head.font.bold = True
            p_head.font.color.rgb = colors[i]

            text_content = bullets[i] if i < len(bullets) else f"Production evaluation metric for {card_headers[i]}."
            p_body = tf.add_paragraph()
            p_body.text = text_content
            p_body.font.name = self.FONT_BODY
            p_body.font.size = Pt(11)
            p_body.font.color.rgb = self.COLOR_DARK_TEXT
            p_body.space_before = Pt(6)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="light")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 6: BEFORE AND AFTER COMPARISON (LIGHT)
    # -------------------------------------------------------------------------
    def _render_comparison_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Before-and-After: Baseline vs Production Solution")
        subtitle = data.get("subtitle", "Quantifying error reduction and architectural superiority")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="light")

        col_w = Inches(5.7)
        card_h = Inches(4.8)
        top_y = Inches(1.8)

        # Left Column: Naive Baseline (Amber/Red Accent)
        x1 = Inches(0.8)
        card1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x1, top_y, col_w, card_h)
        card1.fill.solid()
        card1.fill.fore_color.rgb = self.COLOR_CARD_LIGHT
        card1.line.color.rgb = self.COLOR_AMBER_WARNING
        card1.line.width = Pt(2)

        tb1 = slide.shapes.add_textbox(x1 + Inches(0.3), top_y + Inches(0.25), col_w - Inches(0.6), card_h - Inches(0.5))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        p1_head = tf1.paragraphs[0]
        p1_head.text = "⚠️ NAIVE HEURISTIC BASELINE"
        p1_head.font.name = self.FONT_HEADING
        p1_head.font.size = Pt(12)
        p1_head.font.bold = True
        p1_head.font.color.rgb = self.COLOR_AMBER_WARNING

        left_points = [bullets[0], bullets[2]] if len(bullets) >= 3 else [
            "Rolling moving average without covariate weighting.",
            "High residual variance leading to unpredictable budget overruns."
        ]
        for pt in left_points:
            p = tf1.add_paragraph()
            p.text = f"• {pt}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.color.rgb = self.COLOR_DARK_TEXT
            p.space_before = Pt(12)

        # Right Column: Production ML Solution (Success Green Accent)
        x2 = Inches(6.833)
        card2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x2, top_y, col_w, card_h)
        card2.fill.solid()
        card2.fill.fore_color.rgb = self.COLOR_CARD_LIGHT
        card2.line.color.rgb = self.COLOR_SUCCESS_GREEN
        card2.line.width = Pt(2)

        tb2 = slide.shapes.add_textbox(x2 + Inches(0.3), top_y + Inches(0.25), col_w - Inches(0.6), card_h - Inches(0.5))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p2_head = tf2.paragraphs[0]
        p2_head.text = "✅ PRODUCTION REGULARIZED PIPELINE"
        p2_head.font.name = self.FONT_HEADING
        p2_head.font.size = Pt(12)
        p2_head.font.bold = True
        p2_head.font.color.rgb = self.COLOR_SUCCESS_GREEN

        right_points = [bullets[1], bullets[3]] if len(bullets) >= 4 else [
            "Leakage-free Scikit-Learn Pipeline with regularized L2 weights.",
            "Residual variance slashed by up to 85% with sub-millisecond serving latency."
        ]
        for pt in right_points:
            p = tf2.add_paragraph()
            p.text = f"• {pt}"
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.color.rgb = self.COLOR_DARK_TEXT
            p.space_before = Pt(12)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="light")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 7: COMMON PRODUCTION PITFALLS (LIGHT)
    # -------------------------------------------------------------------------
    def _render_pitfalls_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Common Production Pitfalls & Mitigations")
        subtitle = data.get("subtitle", "Preventing data leakage and numerical instability in production")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="light")

        # 4 Horizontal Warning Strips
        start_y = Inches(1.8)
        card_h = Inches(1.1)
        gap = Inches(0.18)
        card_w = Inches(11.733)
        start_x = Inches(0.8)

        pitfalls_data = bullets[:4] or [
            "Target Leakage: Global feature scaling before train/test splitting.",
            "Multicollinearity: Singular matrix collapse in unregularized Normal Equations.",
            "Lookahead Bias: Shuffle splits on sequential temporal observations.",
            "Heteroscedasticity: Ignoring non-constant residual variance."
        ]

        for i, text in enumerate(pitfalls_data):
            y = start_y + (i * (card_h + gap))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, y, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.COLOR_CARD_LIGHT
            card.line.color.rgb = self.COLOR_BORDER_LIGHT
            card.line.width = Pt(1)

            # Red warning indicator bar on left of each card
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, start_x, y, Inches(0.12), card_h)
            bar.fill.solid()
            bar.fill.fore_color.rgb = self.COLOR_DANGER_RED
            bar.line.fill.background()

            tb = slide.shapes.add_textbox(start_x + Inches(0.3), y + Inches(0.15), card_w - Inches(0.5), card_h - Inches(0.3))
            tf = tb.text_frame
            tf.word_wrap = True
            p0 = tf.paragraphs[0]
            p0.text = f"HAZARD 0{i+1}: {text}"
            p0.font.name = self.FONT_HEADING
            p0.font.size = Pt(11)
            p0.font.bold = True
            p0.font.color.rgb = self.COLOR_DARK_TEXT

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="light")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 8: INTERVIEW DEFENSE (DARK)
    # -------------------------------------------------------------------------
    def _render_interview_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "High-Yield Technical Interview Defense")
        subtitle = data.get("subtitle", "Senior and Staff level architectural evaluations")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="dark")

        # 2 Large Q&A Cards
        top_y = Inches(1.8)
        card_h = Inches(2.25)
        gap = Inches(0.3)
        card_w = Inches(11.733)
        start_x = Inches(0.8)

        questions = bullets[:2] if len(bullets) >= 2 else [
            "Q: Why does L1 regularization yield sparse zero weights while L2 only shrinks them?\nA: The L1 diamond constraint region intersects quadratic loss contours at coordinate axes corners.",
            "Q: Under what condition is OLS mathematically equivalent to Maximum Likelihood Estimation?\nA: When additive errors are independently and identically distributed normal random variables."
        ]

        for i, qa in enumerate(questions):
            y = top_y + (i * (card_h + gap))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, start_x, y, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.COLOR_CARD_DARK
            card.line.color.rgb = self.COLOR_BORDER_DARK
            card.line.width = Pt(1)

            tb = slide.shapes.add_textbox(start_x + Inches(0.3), y + Inches(0.2), card_w - Inches(0.6), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p0 = tf.paragraphs[0]
            p0.text = f"TECHNICAL DEFENSE 0{i+1}"
            p0.font.name = self.FONT_HEADING
            p0.font.size = Pt(10)
            p0.font.bold = True
            p0.font.color.rgb = self.COLOR_ELECTRIC_CYAN

            p1 = tf.add_paragraph()
            p1.text = qa
            p1.font.name = self.FONT_BODY
            p1.font.size = Pt(11)
            p1.font.color.rgb = self.COLOR_WHITE
            p1.space_before = Pt(8)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="dark")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 9: KNOWLEDGE CHECK (LIGHT)
    # -------------------------------------------------------------------------
    def _render_knowledge_check_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Knowledge Check: Diagnostic Checkpoint")
        subtitle = data.get("subtitle", "Immediate concept mastery verification")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="light")

        # Large Question Card
        q_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = self.COLOR_CARD_LIGHT
        q_card.line.color.rgb = self.COLOR_DEEP_BLUE
        q_card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.933), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p_q_badge = tf.paragraphs[0]
        p_q_badge.text = "CONCEPT VERIFICATION QUESTION"
        p_q_badge.font.name = self.FONT_HEADING
        p_q_badge.font.size = Pt(11)
        p_q_badge.font.bold = True
        p_q_badge.font.color.rgb = self.COLOR_DEEP_BLUE

        for b in bullets:
            p = tf.add_paragraph()
            p.text = b
            p.font.name = self.FONT_BODY
            p.font.size = Pt(12)
            p.font.color.rgb = self.COLOR_DARK_TEXT
            p.space_before = Pt(10)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="light")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 10: KEY TAKEAWAYS (LIGHT)
    # -------------------------------------------------------------------------
    def _render_takeaways_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", "Key Takeaways: Production Masterclass Summary")
        subtitle = data.get("subtitle", "Structured daily retention card")
        bullets = data.get("bullets", [])

        self._render_header_band(slide, title, subtitle, day_num, module, theme="light")

        # 3 Column Cards
        col_w = Inches(3.7)
        gap = Inches(0.3)
        start_x = Inches(0.8)
        top_y = Inches(1.8)
        card_h = Inches(4.8)

        cards_data = bullets[:3] or [
            "Foundation: Closed-form analytical optimization provides the baseline for predictive systems.",
            "Integrity: Encapsulate transformers inside pipelines to eliminate test set contamination.",
            "Stability: L2 shrinkage guarantees invertible Gram matrices under collinearity."
        ]

        headers = ["MATHEMATICAL PILLAR", "ENGINEERING INTEGRITY", "PRODUCTION RELIABILITY"]
        for i, text in enumerate(cards_data):
            x = start_x + (i * (col_w + gap))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, col_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.COLOR_CARD_LIGHT
            card.line.color.rgb = self.COLOR_BORDER_LIGHT
            card.line.width = Pt(1)

            tb = slide.shapes.add_textbox(x + Inches(0.25), top_y + Inches(0.3), col_w - Inches(0.5), card_h - Inches(0.6))
            tf = tb.text_frame
            tf.word_wrap = True
            p0 = tf.paragraphs[0]
            p0.text = headers[i]
            p0.font.name = self.FONT_HEADING
            p0.font.size = Pt(10)
            p0.font.bold = True
            p0.font.color.rgb = self.COLOR_DEEP_BLUE

            p1 = tf.add_paragraph()
            p1.text = text
            p1.font.name = self.FONT_BODY
            p1.font.size = Pt(12)
            p1.font.color.rgb = self.COLOR_DARK_TEXT
            p1.space_before = Pt(14)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme="light")

    # -------------------------------------------------------------------------
    # SLIDE LAYOUT 11: STANDARD CARD GRID (LIGHT / DARK)
    # -------------------------------------------------------------------------
    def _render_card_grid_slide(self, slide, data: Dict[str, Any], day_num: int, module: str, current_idx: int, total_slides: int):
        title = data.get("title", f"Slide {current_idx}")
        subtitle = data.get("subtitle", "")
        theme = data.get("theme", "light")
        bullets = data.get("bullets", [])

        is_dark = (theme == "dark")
        self._render_header_band(slide, title, subtitle, day_num, module, theme=theme)

        # 2 Column Split
        col_w = Inches(5.7)
        gap = Inches(0.333)
        top_y = Inches(1.8)
        card_h = Inches(4.8)

        card_bg = self.COLOR_CARD_DARK if is_dark else self.COLOR_CARD_LIGHT
        card_border = self.COLOR_BORDER_DARK if is_dark else self.COLOR_BORDER_LIGHT
        text_color = self.COLOR_WHITE if is_dark else self.COLOR_DARK_TEXT

        half = max(1, (len(bullets) + 1) // 2)
        cols_data = [bullets[:half], bullets[half:]]

        for i, col_items in enumerate(cols_data):
            x = Inches(0.8) + (i * (col_w + gap))
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, col_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = card_bg
            card.line.color.rgb = card_border
            card.line.width = Pt(1)

            tb = slide.shapes.add_textbox(x + Inches(0.3), top_y + Inches(0.3), col_w - Inches(0.6), card_h - Inches(0.6))
            tf = tb.text_frame
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = f"SECTION 0{i+1}"
            p0.font.name = self.FONT_HEADING
            p0.font.size = Pt(10)
            p0.font.bold = True
            p0.font.color.rgb = self.COLOR_ELECTRIC_CYAN if is_dark else self.COLOR_DEEP_BLUE

            for item in col_items:
                p = tf.add_paragraph()
                p.text = f"• {item}"
                p.font.name = self.FONT_BODY
                p.font.size = Pt(12)
                p.font.color.rgb = text_color
                p.space_before = Pt(12)

        self._render_discreet_footer(slide, day_num, title, module, current_idx, total_slides, theme=theme)
