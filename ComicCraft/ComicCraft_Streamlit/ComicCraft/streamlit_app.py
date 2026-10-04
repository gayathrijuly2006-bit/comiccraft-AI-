import json
import os
import textwrap
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw
from fpdf import FPDF

# ============================================================
# ENVIRONMENT
# ============================================================

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="ComicCraft AI",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0e1117;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background-color: #171b22;
        border: 1px solid #343b47;
        margin-bottom: 25px;
    }

    .hero h1 {
        margin: 0;
        font-size: 42px;
        font-weight: 800;
    }

    .hero p {
        color: #aeb7c4;
        font-size: 17px;
    }

    .panel {
        padding: 18px;
        border: 1px solid #343b47;
        border-radius: 14px;
        background-color: #171b22;
        margin-bottom: 18px;
    }

    .dialogue {
        padding: 10px 14px;
        border-radius: 10px;
        background-color: #252c37;
        margin: 6px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DEMO STORY
# ============================================================

def create_demo_story(
    prompt,
    character,
    setting,
    tone
):

    return {
        "title": f"{character}: {tone} at the {setting}",

        "panels": [

            {
                "panel": 1,

                "scene": (
                    f"{character} arrives at the {setting} "
                    "after receiving a mysterious message."
                ),

                "narration": (
                    "A normal day suddenly becomes an "
                    "unexpected adventure."
                ),

                "dialogue": [
                    {
                        "character": character,
                        "text": (
                            "I wonder who sent this message..."
                        )
                    }
                ]
            },

            {
                "panel": 2,

                "scene": (
                    f"{character} discovers a glowing object "
                    f"hidden near the {setting}."
                ),

                "narration": (
                    "The strange object begins to glow."
                ),

                "dialogue": [
                    {
                        "character": character,
                        "text": (
                            "This definitely wasn't here before!"
                        )
                    }
                ]
            },

            {
                "panel": 3,

                "scene": (
                    f"The object reveals a clue connected "
                    f"to the story: {prompt}"
                ),

                "narration": (
                    "The mystery is connected to something "
                    "much bigger."
                ),

                "dialogue": [
                    {
                        "character": character,
                        "text": (
                            "Now everything is starting to "
                            "make sense."
                        )
                    }
                ]
            },

            {
                "panel": 4,

                "scene": (
                    f"{character} follows the clue and "
                    "faces the main challenge."
                ),

                "narration": (
                    "Courage becomes more important than fear."
                ),

                "dialogue": [
                    {
                        "character": character,
                        "text": (
                            "I have to keep going!"
                        )
                    }
                ]
            },

            {
                "panel": 5,

                "scene": (
                    f"{character} solves the mystery "
                    "and returns safely."
                ),

                "narration": (
                    "The adventure ends, but a new story "
                    "is just beginning."
                ),

                "dialogue": [
                    {
                        "character": character,
                        "text": (
                            "What an incredible adventure!"
                        )
                    }
                ]
            }

        ]
    }


# ============================================================
# GEMINI STORY GENERATOR
# ============================================================

def generate_gemini_story(
    prompt,
    character,
    setting,
    tone,
    art_style
):

    if not GEMINI_API_KEY:
        return None, "Gemini API key not configured."

    try:

        from google import genai

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        instruction = f"""
Create a coherent five-panel comic.

Story idea:
{prompt}

Main character:
{character}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "title": "Comic title",

    "panels": [
        {{
            "panel": 1,
            "scene": "Visual scene description",
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

Rules:

1. Exactly 5 panels.
2. Every panel must advance the story.
3. Include narration.
4. Include character dialogue.
5. Dialogue should be concise.
6. Scenes should be visually understandable.
7. No markdown.
8. No code fences.
9. Return valid JSON only.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=instruction
        )

        raw_text = (
            response.text or ""
        ).strip()

        raw_text = raw_text.replace(
            "```json",
            ""
        )

        raw_text = raw_text.replace(
            "```",
            ""
        )

        raw_text = raw_text.strip()

        story = json.loads(raw_text)

        if (
            not isinstance(
                story.get("panels"),
                list
            )
            or len(story["panels"]) != 5
        ):

            raise ValueError(
                "Gemini did not return exactly 5 panels."
            )

        return story, None

    except Exception as error:

        return None, str(error)


# ============================================================
# COMIC PANEL IMAGE
# ============================================================

def create_panel_image(
    panel_number,
    scene,
    art_style
):

    width = 1000
    height = 650

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    # Outer border

    draw.rectangle(
        (
            8,
            8,
            width - 8,
            height - 8
        ),
        outline="black",
        width=8
    )

    # Header

    draw.rectangle(
        (
            30,
            30,
            width - 30,
            90
        ),
        fill="black"
    )

    draw.text(
        (55, 49),
        f"PANEL {panel_number}",
        fill="white"
    )

    # Character

    center_x = width // 2
    center_y = 390

    # Head

    draw.ellipse(
        (
            center_x - 75,
            center_y - 150,
            center_x + 75,
            center_y
        ),
        outline="black",
        width=6
    )

    # Eyes

    draw.ellipse(
        (
            center_x - 42,
            center_y - 90,
            center_x - 22,
            center_y - 70
        ),
        fill="black"
    )

    draw.ellipse(
        (
            center_x + 22,
            center_y - 90,
            center_x + 42,
            center_y - 70
        ),
        fill="black"
    )

    # Smile

    draw.arc(
        (
            center_x - 35,
            center_y - 55,
            center_x + 35,
            center_y - 15
        ),
        0,
        180,
        fill="black",
        width=4
    )

    # Body

    draw.rectangle(
        (
            center_x - 65,
            center_y,
            center_x + 65,
            center_y + 150
        ),
        outline="black",
        width=6
    )

    # Arms

    draw.line(
        (
            center_x - 65,
            center_y + 25,
            center_x - 180,
            center_y + 95
        ),
        fill="black",
        width=7
    )

    draw.line(
        (
            center_x + 65,
            center_y + 25,
            center_x + 180,
            center_y + 95
        ),
        fill="black",
        width=7
    )

    # Speech bubble

    bubble_x = 120
    bubble_y = 125

    draw.rounded_rectangle(
        (
            bubble_x,
            bubble_y,
            800,
            280
        ),
        radius=28,
        fill="white",
        outline="black",
        width=4
    )

    wrapped_scene = textwrap.fill(
        str(scene),
        width=65
    )

    draw.text(
        (
            bubble_x + 22,
            bubble_y + 22
        ),
        wrapped_scene,
        fill="black"
    )

    # Art style

    draw.text(
        (
            40,
            height - 48
        ),
        f"Style: {art_style}",
        fill="black"
    )

    image_path = (
        OUTPUT_DIR /
        f"panel_{panel_number}.png"
    )

    image.save(image_path)

    return image_path


# ============================================================
# PDF GENERATOR - FIXED
# ============================================================

def create_pdf(
    story,
    image_paths
):

    pdf_path = (
        OUTPUT_DIR /
        "ComicCraft_Comic.pdf"
    )

    pdf = FPDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()

    # Title

    pdf.set_font(
        "Helvetica",
        "B",
        20
    )

    pdf.multi_cell(
        180,
        12,
        str(
            story.get(
                "title",
                "ComicCraft Comic"
            )
        ),
        align="C"
    )

    pdf.ln(5)

    # Panels

    for index, panel in enumerate(
        story["panels"]
    ):

        # Panel heading

        pdf.set_font(
            "Helvetica",
            "B",
            14
        )

        pdf.multi_cell(
            180,
            8,
            f"Panel {panel.get('panel', index + 1)}"
        )

        # Image

        pdf.image(
            str(image_paths[index]),
            x=15,
            w=180
        )

        pdf.ln(4)

        # Narration

        narration = str(
            panel.get(
                "narration",
                ""
            )
        )

        if narration.strip():

            pdf.set_font(
                "Helvetica",
                "I",
                10
            )

            pdf.multi_cell(
                180,
                6,
                narration,
                wrapmode="CHAR"
            )

        pdf.ln(2)

        # Dialogue

        pdf.set_font(
            "Helvetica",
            "",
            10
        )

        for dialogue in panel.get(
            "dialogue",
            []
        ):

            character = str(
                dialogue.get(
                    "character",
                    "Character"
                )
            )

            message = str(
                dialogue.get(
                    "text",
                    ""
                )
            )

            dialogue_line = (
                f"{character}: {message}"
            )

            # IMPORTANT:
            # Explicit width prevents the
            # FPDF horizontal-space error.

            pdf.multi_cell(
                180,
                6,
                dialogue_line,
                wrapmode="CHAR"
            )

            pdf.ln(1)

        pdf.ln(6)

    pdf.output(
        str(pdf_path)
    )

    return pdf_path


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>🎨 ComicCraft AI</h1>

        <p>
        Turn a story idea into a five-panel comic
        with AI narration, dialogue, illustrations
        and PDF export.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Configuration"
    )

    if GEMINI_API_KEY:

        st.success(
            f"Gemini: {GEMINI_MODEL}"
        )

    else:

        st.warning(
            "Gemini API key not configured — "
            "demo mode available."
        )

    st.caption(
        "Never put API keys directly "
        "inside source code."
    )


# ============================================================
# INPUT SECTION
# ============================================================

st.subheader(
    "✍️ Create Your Comic"
)

story_prompt = st.text_area(
    "Story Prompt",
    placeholder=(
        "Example: A student discovers "
        "a robot that can predict the future."
    ),
    height=130
)


column1, column2 = st.columns(2)


with column1:

    character = st.text_input(
        "Main Character",
        "Arjun"
    )

    setting = st.selectbox(
        "Setting",
        [
            "College",
            "Future City",
            "Laboratory",
            "Forest",
            "Space Station",
            "Village",
            "Office"
        ]
    )


with column2:

    tone = st.selectbox(
        "Tone",
        [
            "Adventure",
            "Funny",
            "Mystery",
            "Emotional",
            "Inspirational",
            "Sci-Fi"
        ]
    )

    art_style = st.selectbox(
        "Art Style",
        [
            "Comic Book",
            "Cartoon",
            "Manga",
            "Anime",
            "Minimal"
        ]
    )


# ============================================================
# GENERATE BUTTON
# ============================================================

generate_button = st.button(
    "🚀 Generate Comic",
    type="primary",
    use_container_width=True
)


# ============================================================
# GENERATE COMIC
# ============================================================

if generate_button:

    if not story_prompt.strip():

        st.error(
            "Please enter a story prompt."
        )

        st.stop()


    with st.spinner(
        "Creating your comic..."
    ):

        story, error = generate_gemini_story(
            story_prompt,
            character,
            setting,
            tone,
            art_style
        )


        # Fallback

        if story is None:

            story = create_demo_story(
                story_prompt,
                character,
                setting,
                tone
            )

            if GEMINI_API_KEY:

                st.warning(
                    "Gemini generation failed. "
                    "Demo mode was used instead."
                )

                with st.expander(
                    "Show Gemini error"
                ):

                    st.code(
                        error
                    )

            else:

                st.info(
                    "Demo mode used. "
                    "Configure Gemini to enable "
                    "AI story generation."
                )


        # Generate images

        image_paths = []

        for panel in story["panels"]:

            image_path = create_panel_image(
                panel["panel"],
                panel["scene"],
                art_style
            )

            image_paths.append(
                image_path
            )


        # Generate PDF

        pdf_path = create_pdf(
            story,
            image_paths
        )


    # ========================================================
    # RESULTS
    # ========================================================

    st.success(
        "🎉 Comic generated successfully!"
    )

    st.header(
        "📖 " +
        story.get(
            "title",
            "ComicCraft Comic"
        )
    )


    # ========================================================
    # PANELS
    # ========================================================

    for index, panel in enumerate(
        story["panels"]
    ):

        st.markdown(
            f"""
            <div class="panel">
                <h3>
                    Panel {panel["panel"]}
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )


        image_column, text_column = st.columns(
            [1.15, 1]
        )


        with image_column:

            st.image(
                str(
                    image_paths[index]
                ),
                use_container_width=True
            )


        with text_column:

            st.markdown(
                "**Scene**"
            )

            st.write(
                panel.get(
                    "scene",
                    ""
                )
            )


            st.markdown(
                "**Narration**"
            )

            st.write(
                panel.get(
                    "narration",
                    ""
                )
            )


            st.markdown(
                "**Dialogue**"
            )


            for dialogue in panel.get(
                "dialogue",
                []
            ):

                st.markdown(
                    f"""
                    <div class="dialogue">

                    <b>
                    {dialogue.get(
                        "character",
                        ""
                    )}:
                    </b>

                    {dialogue.get(
                        "text",
                        ""
                    )}

                    </div>
                    """,
                    unsafe_allow_html=True
                )


        st.divider()


    # ========================================================
    # EXPORT
    # ========================================================

    st.subheader(
        "📥 Export"
    )


    with open(
        pdf_path,
        "rb"
    ) as pdf_file:

        st.download_button(
            "⬇️ Download Comic PDF",
            pdf_file,
            file_name="ComicCraft_Comic.pdf",
            mime="application/pdf"
        )


    st.download_button(
        "⬇️ Download Story JSON",

        json.dumps(
            story,
            indent=2
        ),

        file_name="comic_story.json",

        mime="application/json"
    )