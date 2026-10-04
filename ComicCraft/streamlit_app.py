import os
import io
import json
import base64
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

APP_NAME = "ComicCraft"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)

OUTPUT_DIR = Path("streamlit_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ComicCraft AI",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #777;
        margin-bottom: 2rem;
    }

    .panel-card {
        padding: 1.2rem;
        border-radius: 15px;
        border: 1px solid #ddd;
        margin-bottom: 1.5rem;
        background: #ffffff;
    }

    .panel-title {
        font-size: 1.4rem;
        font-weight: 700;
    }

    .caption {
        font-style: italic;
        color: #555;
    }

    .dialogue {
        padding: 0.8rem;
        border-radius: 10px;
        background: #f4f4f4;
        margin-top: 0.5rem;
    }

    .stButton > button {
        width: 100%;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🎨 ComicCraft AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Turn your story idea into a 5-panel AI comic"
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# HELPER: GEMINI CLIENT
# ============================================================

def get_gemini_client():
    if not GEMINI_API_KEY or genai is None:
        return None

    return genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# MOCK COMIC GENERATOR
# ============================================================

def create_mock_comic(
    story_prompt,
    character,
    setting,
    tone,
    art_style
):
    """
    Creates a demo comic without requiring an API key.
    """

    return [
        {
            "panel": 1,
            "title": "The Beginning",
            "scene_description": (
                f"{character} begins an unexpected adventure "
                f"in {setting}."
            ),
            "caption": "A new adventure begins...",
            "narration": (
                f"{character} never expected that a simple day "
                f"in {setting} would change everything."
            ),
            "dialogue": (
                f"{character}: Something feels different today."
            ),
            "image_prompt": (
                f"{art_style} comic illustration of {character} "
                f"in {setting}, beginning an adventure"
            )
        },
        {
            "panel": 2,
            "title": "The Challenge",
            "scene_description": (
                f"A mysterious event appears in {setting}."
            ),
            "caption": "Suddenly, everything changes!",
            "narration": (
                f"A strange mystery appears before {character}. "
                f"The situation becomes more difficult."
            ),
            "dialogue": (
                f"{character}: What is happening?"
            ),
            "image_prompt": (
                f"{art_style} comic scene showing {character} "
                f"facing a mysterious challenge in {setting}"
            )
        },
        {
            "panel": 3,
            "title": "The Turning Point",
            "scene_description": (
                f"{character} discovers an important clue."
            ),
            "caption": "The truth is closer than expected.",
            "narration": (
                f"After thinking carefully, {character} discovers "
                f"a clue that could solve the mystery."
            ),
            "dialogue": (
                f"{character}: Now I understand!"
            ),
            "image_prompt": (
                f"{art_style} dramatic comic illustration of "
                f"{character} discovering a clue in {setting}"
            )
        },
        {
            "panel": 4,
            "title": "The Decision",
            "scene_description": (
                f"{character} must make an important decision."
            ),
            "caption": "There is no turning back.",
            "narration": (
                f"{character} gathers courage and decides to "
                f"face the problem directly."
            ),
            "dialogue": (
                f"{character}: I have to do this."
            ),
            "image_prompt": (
                f"{art_style} heroic comic scene of {character} "
                f"making a brave decision in {setting}"
            )
        },
        {
            "panel": 5,
            "title": "The Ending",
            "scene_description": (
                f"The adventure reaches a satisfying conclusion."
            ),
            "caption": "And so the adventure ends...",
            "narration": (
                f"{character} successfully completes the adventure. "
                f"The experience changes how they see the world."
            ),
            "dialogue": (
                f"{character}: I will never forget this adventure."
            ),
            "image_prompt": (
                f"{art_style} cinematic comic ending showing "
                f"{character} standing proudly in {setting}"
            )
        }
    ]


# ============================================================
# GEMINI GENERATOR
# ============================================================

def generate_with_gemini(
    story_prompt,
    character,
    setting,
    tone,
    art_style
):
    client = get_gemini_client()

    if client is None:
        return None

    prompt = f"""
You are ComicCraft, an expert comic writer.

Create a complete 5-panel comic.

USER INPUT
Story idea: {story_prompt}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON.

Required structure:

{{
  "panels": [
    {{
      "panel": 1,
      "title": "...",
      "scene_description": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "...",
      "image_prompt": "..."
    }}
  ]
}}

Requirements:
- Exactly 5 panels.
- Create a coherent beginning, middle and ending.
- Keep the same main character throughout.
- Make the dialogue natural.
- Make each image_prompt visually detailed.
- Follow the requested tone and art style.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        data = json.loads(response.text)

        panels = data.get("panels", [])

        if len(panels) != 5:
            return None

        return panels

    except Exception as e:
        st.warning(
            f"Gemini generation failed. Using demo mode instead. "
            f"Error: {e}"
        )
        return None


# ============================================================
# DEMO IMAGE GENERATOR
# ============================================================

def create_demo_image(
    panel,
    character,
    setting,
    art_style
):
    """
    Generates a simple illustrated placeholder image.
    """

    width = 1200
    height = 700

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    # Background
    draw.rectangle(
        [0, 0, width, height],
        outline="black",
        width=8
    )

    # Panel number
    draw.text(
        (40, 30),
        f"PANEL {panel['panel']}",
        fill="black"
    )

    # Main title
    draw.text(
        (40, 90),
        panel["title"],
        fill="black"
    )

    # Character representation
    cx = width // 2
    cy = 330

    # Head
    draw.ellipse(
        [cx - 70, cy - 100, cx + 70, cy + 40],
        outline="black",
        width=6
    )

    # Body
    draw.rectangle(
        [cx - 80, cy + 40, cx + 80, cy + 230],
        outline="black",
        width=6
    )

    # Arms
    draw.line(
        [cx - 80, cy + 80, cx - 190, cy + 160],
        fill="black",
        width=6
    )

    draw.line(
        [cx + 80, cy + 80, cx + 190, cy + 160],
        fill="black",
        width=6
    )

    # Legs
    draw.line(
        [cx - 40, cy + 230, cx - 100, cy + 350],
        fill="black",
        width=6
    )

    draw.line(
        [cx + 40, cy + 230, cx + 100, cy + 350],
        fill="black",
        width=6
    )

    # Environment
    draw.text(
        (40, 600),
        f"Character: {character}",
        fill="black"
    )

    draw.text(
        (40, 635),
        f"Setting: {setting}",
        fill="black"
    )

    return image


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf(panels, images):
    pdf = FPDF()

    for panel, image in zip(panels, images):

        pdf.add_page()

        pdf.set_font("Helvetica", "B", 18)

        pdf.cell(
            0,
            12,
            f"Panel {panel['panel']}: {panel['title']}",
            ln=True
        )

        pdf.ln(5)

        # Save image temporarily
        image_path = (
            OUTPUT_DIR /
            f"panel_{panel['panel']}.png"
        )

        image.save(image_path)

        pdf.image(
            str(image_path),
            x=10,
            y=35,
            w=190
        )

        pdf.set_y(150)

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            7,
            f"Scene: {panel['scene_description']}"
        )

        pdf.ln(2)

        pdf.multi_cell(
            0,
            7,
            f"Caption: {panel['caption']}"
        )

        pdf.ln(2)

        pdf.multi_cell(
            0,
            7,
            f"Narration: {panel['narration']}"
        )

        pdf.ln(2)

        pdf.multi_cell(
            0,
            7,
            f"Dialogue: {panel['dialogue']}"
        )

    pdf_bytes = bytes(pdf.output())

    return pdf_bytes


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Comic Settings")

    st.write(
        "Create a 5-panel comic from your story idea."
    )

    if GEMINI_API_KEY:
        st.success("Gemini API configured")
    else:
        st.info(
            "Gemini API key not found.\n\n"
            "Demo mode will be used."
        )

    st.divider()

    st.caption(
        "ComicCraft AI Demo"
    )


# ============================================================
# INPUT FORM
# ============================================================

with st.form("comic_form"):

    st.subheader("✍️ Create Your Comic")

    story_prompt = st.text_area(
        "Story Prompt",
        placeholder=(
            "Example: A young student discovers "
            "a mysterious robot in an abandoned laboratory."
        ),
        height=120
    )

    col1, col2 = st.columns(2)

    with col1:

        character = st.text_input(
            "Main Character",
            placeholder="Example: Arjun"
        )

        setting = st.selectbox(
            "Setting",
            [
                "School",
                "Forest",
                "City",
                "Space",
                "Futuristic City",
                "Village",
                "Laboratory",
                "Custom"
            ]
        )

    with col2:

        tone = st.selectbox(
            "Story Tone",
            [
                "Funny",
                "Dramatic",
                "Adventurous",
                "Emotional",
                "Mysterious",
                "Light-hearted"
            ]
        )

        art_style = st.selectbox(
            "Art Style",
            [
                "Comic Book",
                "Anime",
                "Pixel Art",
                "Realistic",
                "Cartoon",
                "Manga"
            ]
        )

    generate = st.form_submit_button(
        "🚀 Generate Comic"
    )


# ============================================================
# GENERATION
# ============================================================

if generate:

    if not story_prompt.strip():
        st.error("Please enter a story prompt.")

    elif not character.strip():
        st.error("Please enter a character name.")

    else:

        with st.spinner(
            "Creating your comic..."
        ):

            # Try Gemini first
            panels = generate_with_gemini(
                story_prompt,
                character,
                setting,
                tone,
                art_style
            )

            # Fallback
            if panels is None:

                panels = create_mock_comic(
                    story_prompt,
                    character,
                    setting,
                    tone,
                    art_style
                )

                st.info(
                    "Demo mode: using built-in comic generation."
                )

            # Generate images
            images = []

            for panel in panels:

                image = create_demo_image(
                    panel,
                    character,
                    setting,
                    art_style
                )

                images.append(image)

        st.session_state["panels"] = panels
        st.session_state["images"] = images


# ============================================================
# DISPLAY COMIC
# ============================================================

if "panels" in st.session_state:

    panels = st.session_state["panels"]
    images = st.session_state["images"]

    st.divider()

    st.header("📖 Your Comic")

    for panel, image in zip(panels, images):

        st.markdown(
            f"""
            <div class="panel-card">

            <div class="panel-title">
            Panel {panel['panel']}: {panel['title']}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.image(
            image,
            use_container_width=True
        )

        st.markdown(
            f"**Scene:** {panel['scene_description']}"
        )

        st.markdown(
            f"*Caption: {panel['caption']}*"
        )

        st.markdown(
            f"**Narration:** {panel['narration']}"
        )

        st.markdown(
            f"""
            <div class="dialogue">
            💬 <b>{panel['dialogue']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander(
            "🔍 Image Prompt"
        ):
            st.write(
                panel["image_prompt"]
            )

        st.divider()

    # ========================================================
    # PDF
    # ========================================================

    st.header("📥 Export")

    pdf_data = create_pdf(
        panels,
        images
    )

    st.download_button(
        label="📄 Download Comic as PDF",
        data=pdf_data,
        file_name="ComicCraft_Comic.pdf",
        mime="application/pdf"
    )

    st.success(
        "Your comic is ready!"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "ComicCraft AI — Generative AI Comic Creator"
)
