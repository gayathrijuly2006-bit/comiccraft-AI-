import os
import json
import textwrap
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

load_dotenv()

APP_TITLE = "ComicCraft AI"
OUTPUT_DIR = Path("streamlit_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="ComicCraft AI",
    page_icon="🎨",
    layout="wide",
)


# ---------------------------------------------------------
# CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }

    .comic-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .comic-subtitle {
        text-align: center;
        color: #aaaaaa;
        margin-bottom: 30px;
    }

    .panel-card {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #444;
        background-color: #171b22;
        margin-bottom: 15px;
    }

    .dialogue {
        padding: 10px;
        border-radius: 8px;
        background-color: #252a34;
        margin-top: 8px;
    }

    .narration {
        color: #cccccc;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------

def generate_with_gemini(prompt: str):
    """
    Generate structured comic content using Google Gemini.
    Returns None if Gemini is unavailable.
    """

    if not GEMINI_API_KEY:
        return None

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        instruction = f"""
Create a 5-panel comic story.

User story:
{prompt}

Return ONLY valid JSON in this format:

{{
  "title": "Comic title",
  "panels": [
    {{
      "panel": 1,
      "scene": "Short visual description",
      "narration": "Narrator text",
      "dialogue": [
        {{
          "character": "Character name",
          "text": "Dialogue"
        }}
      ]
    }}
  ]
}}

Requirements:
- Exactly 5 panels.
- Make the story coherent.
- Include narration.
- Include character dialogue.
- Make each scene visually understandable.
- Do not use markdown.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=instruction,
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        return json.loads(text)

    except Exception as e:
        st.warning(f"Gemini unavailable. Demo mode used. ({e})")
        return None


# ---------------------------------------------------------
# Demo story generator
# ---------------------------------------------------------

def generate_demo_story(
    story_prompt,
    character,
    setting,
    tone,
    art_style,
):
    return {
        "title": f"{character}'s Adventure",
        "panels": [
            {
                "panel": 1,
                "scene": f"{character} arrives at the {setting}.",
                "narration": f"It was an unusual day at the {setting}.",
                "dialogue": [
                    {
                        "character": character,
                        "text": "Something strange is happening here..."
                    }
                ],
            },
            {
                "panel": 2,
                "scene": f"{character} discovers something mysterious.",
                "narration": "A mysterious object suddenly appears.",
                "dialogue": [
                    {
                        "character": character,
                        "text": "What is that?"
                    }
                ],
            },
            {
                "panel": 3,
                "scene": f"The mysterious object reacts to {character}.",
                "narration": "The object begins to glow.",
                "dialogue": [
                    {
                        "character": character,
                        "text": "Whoa! It is responding to me!"
                    }
                ],
            },
            {
                "panel": 4,
                "scene": f"{character} decides to investigate.",
                "narration": "Instead of running away, our hero chooses courage.",
                "dialogue": [
                    {
                        "character": character,
                        "text": "I need to find out what this means."
                    }
                ],
            },
            {
                "panel": 5,
                "scene": f"{character} discovers the truth and smiles.",
                "narration": "The mystery finally makes sense.",
                "dialogue": [
                    {
                        "character": character,
                        "text": "What an incredible adventure!"
                    }
                ],
            },
        ],
    }


# ---------------------------------------------------------
# Image generator
# ---------------------------------------------------------

def create_panel_image(panel_number, scene, art_style):
    """
    Creates a lightweight local comic illustration.
    This avoids requiring a GPU or Stable Diffusion server.
    """

    width = 900
    height = 600

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        [10, 10, width - 10, height - 10],
        outline="black",
        width=8,
    )

    # Header
    draw.rectangle(
        [30, 30, width - 30, 90],
        fill="#222222",
    )

    draw.text(
        (50, 48),
        f"PANEL {panel_number}",
        fill="white",
    )

    # Simple comic illustration
    cx = width // 2
    cy = height // 2 + 20

    # Head
    draw.ellipse(
        [cx - 70, cy - 110, cx + 70, cy + 30],
        outline="black",
        width=5,
    )

    # Eyes
    draw.ellipse(
        [cx - 40, cy - 60, cx - 20, cy - 40],
        fill="black",
    )

    draw.ellipse(
        [cx + 20, cy - 60, cx + 40, cy - 40],
        fill="black",
    )

    # Body
    draw.rectangle(
        [cx - 55, cy + 30, cx + 55, cy + 170],
        outline="black",
        width=5,
    )

    # Arms
    draw.line(
        [cx - 55, cy + 55, cx - 150, cy + 110],
        fill="black",
        width=6,
    )

    draw.line(
        [cx + 55, cy + 55, cx + 150, cy + 110],
        fill="black",
        width=6,
    )

    # Speech bubble
    bubble_x = 120
    bubble_y = 120

    draw.rounded_rectangle(
        [
            bubble_x,
            bubble_y,
            bubble_x + 500,
            bubble_y + 120,
        ],
        radius=25,
        outline="black",
        width=4,
        fill="white",
    )

    wrapped = textwrap.fill(scene, width=45)

    draw.text(
        (bubble_x + 20, bubble_y + 20),
        wrapped,
        fill="black",
    )

    # Art style label
    draw.text(
        (40, height - 55),
        f"Style: {art_style}",
        fill="black",
    )

    path = OUTPUT_DIR / f"panel_{panel_number}.png"
    image.save(path)

    return path


# ---------------------------------------------------------
# PDF generator
# ---------------------------------------------------------

def sanitize_pdf_text(value):
    """
    Make AI-generated text safer for FPDF's built-in Arial font.
    Also break very long words/tokens so FPDF never gets a word
    wider than the available page width.
    """
    value = str(value or "")

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
        "\u2192": "->",
        "\u2190": "<-",
    }

    for old_char, new_char in replacements.items():
        value = value.replace(old_char, new_char)

    # Remove other characters that the built-in Arial font may not support.
    value = value.encode("latin-1", errors="replace").decode("latin-1")

    # Character-level wrapping prevents FPDFException when Gemini returns
    # a very long word, URL, identifier, or punctuation sequence.
    return textwrap.fill(
        value,
        width=70,
        break_long_words=True,
        break_on_hyphens=True,
    )


def create_pdf(story, image_paths):
    pdf_path = OUTPUT_DIR / "comiccraft_comic.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 22)
    pdf.cell(
        0,
        15,
        sanitize_pdf_text(story.get("title", "ComicCraft Comic")),
        ln=True,
        align="C",
    )

    pdf.ln(5)

    for i, panel in enumerate(story["panels"]):

        pdf.set_font("Arial", "B", 15)
        pdf.cell(
            0,
            10,
            sanitize_pdf_text(f"Panel {panel.get('panel', i + 1)}"),
            ln=True,
        )

        image_path = str(image_paths[i])

        pdf.image(
            image_path,
            x=15,
            w=180,
        )

        pdf.ln(3)

        # Narration
        pdf.set_font("Arial", "I", 11)
        narration = sanitize_pdf_text(panel.get("narration", ""))

        if narration:
            pdf.multi_cell(
                0,
                7,
                narration,
            )

        # Dialogue
        pdf.set_font("Arial", "", 11)

        for dialogue in panel.get("dialogue", []):
            character = sanitize_pdf_text(
                dialogue.get("character", "Character")
            )
            dialogue_text = sanitize_pdf_text(
                dialogue.get("text", "")
            )

            pdf.multi_cell(
                0,
                7,
                f"{character}: {dialogue_text}",
            )

        pdf.ln(8)

    pdf.output(str(pdf_path))

    return pdf_path


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Comic Settings")

    st.write(
        "Create a 5-panel comic from your story idea."
    )

    if GEMINI_API_KEY:
        st.success("Gemini API key detected.")
    else:
        st.info(
            "Gemini API key not found.\n\n"
            "Demo mode will be used."
        )

    st.divider()

    st.caption("ComicCraft AI Demo")


# ---------------------------------------------------------
# Main UI
# ---------------------------------------------------------

st.markdown(
    '<div class="comic-title">🎨 ComicCraft AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="comic-subtitle">'
    "AI-powered personalized comic generator"
    "</div>",
    unsafe_allow_html=True,
)


st.subheader("✍️ Create Your Comic")

story_prompt = st.text_area(
    "Story Prompt",
    placeholder=(
        "Example: A young student discovers a "
        "mysterious robot in an abandoned laboratory."
    ),
    height=130,
)

col1, col2 = st.columns(2)

with col1:

    character = st.text_input(
        "Main Character",
        placeholder="Example: Arjun",
    )

    setting = st.selectbox(
        "Setting",
        [
            "School",
            "College",
            "Future City",
            "Space Station",
            "Forest",
            "Laboratory",
            "Village",
            "Office",
        ],
    )


with col2:

    tone = st.selectbox(
        "Story Tone",
        [
            "Funny",
            "Adventure",
            "Mystery",
            "Emotional",
            "Inspirational",
            "Sci-Fi",
        ],
    )

    art_style = st.selectbox(
        "Art Style",
        [
            "Comic Book",
            "Cartoon",
            "Manga",
            "Anime",
            "Minimal",
        ],
    )


generate = st.button(
    "🚀 Generate Comic",
    type="primary",
)


# ---------------------------------------------------------
# Generation
# ---------------------------------------------------------

if generate:

    if not story_prompt.strip():

        st.error("Please enter a story prompt.")

    elif not character.strip():

        st.error("Please enter the main character name.")

    else:

        with st.spinner("Creating your comic..."):

            full_prompt = f"""
Story idea:
{story_prompt}

Main character:
{character}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}
"""

            story = generate_with_gemini(full_prompt)

            if story is None:

                story = generate_demo_story(
                    story_prompt,
                    character,
                    setting,
                    tone,
                    art_style,
                )

            image_paths = []

            for panel in story["panels"]:

                image_path = create_panel_image(
                    panel["panel"],
                    panel["scene"],
                    art_style,
                )

                image_paths.append(image_path)

            pdf_path = create_pdf(
                story,
                image_paths,
            )

        st.success("🎉 Comic generated successfully!")

        st.divider()

        st.header(
            f"📖 {story.get('title', 'ComicCraft Comic')}"
        )

        # -------------------------------------------------
        # Panels
        # -------------------------------------------------

        for index, panel in enumerate(story["panels"]):

            st.markdown(
                f'<div class="panel-card">'
                f"<h3>Panel {panel['panel']}</h3>"
                f"</div>",
                unsafe_allow_html=True,
            )

            col_img, col_text = st.columns(
                [1, 1]
            )

            with col_img:

                st.image(
                    str(image_paths[index]),
                    use_container_width=True,
                )

            with col_text:

                st.markdown(
                    "**Scene**"
                )

                st.write(
                    panel.get("scene", "")
                )

                st.markdown(
                    "**Narration**"
                )

                st.markdown(
                    f'<div class="narration">'
                    f"{panel.get('narration', '')}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "**Dialogue**"
                )

                for dialogue in panel.get(
                    "dialogue", []
                ):

                    st.markdown(
                        f'<div class="dialogue">'
                        f"<b>{dialogue.get('character', '')}:</b> "
                        f"{dialogue.get('text', '')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            st.divider()

        # -------------------------------------------------
        # PDF download
        # -------------------------------------------------

        st.header("📄 Export")

        with open(pdf_path, "rb") as pdf_file:

            st.download_button(
                label="⬇️ Download Comic PDF",
                data=pdf_file,
                file_name="ComicCraft_Comic.pdf",
                mime="application/pdf",
            )

        # -------------------------------------------------
        # JSON
        # -------------------------------------------------

        st.download_button(
            label="⬇️ Download Story JSON",
            data=json.dumps(
                story,
                indent=2,
            ),
            file_name="comic_story.json",
            mime="application/json",
        )

        st.success(
            "Your ComicCraft comic is ready!"
        )
