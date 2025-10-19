import streamlit as st
import os
import tempfile
from Emotion_in_video import detect_emotions_in_video
from Scene_detect import get_scene_boundaries_from_video
from Script_analysis import parse_screenplay_pdf
import json

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="🎬 Media Intelligence Suite",
    layout="wide",
    page_icon="🎥"
)

# -------------------------------
# CUSTOM CSS for professional look
# -------------------------------
st.markdown("""
    <style>
    /* Global Styling */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
        padding: 2rem;
    }

    h1, h2, h3, h4 {
        color: #F5F5F5;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161A23;
        color: #FFFFFF;
        padding-top: 2rem;
    }
    [data-testid="stSidebar"] h2 {
        color: #FAFAFA;
        text-align: center;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #0066FF, #00CC99);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #00CC99, #0066FF);
        transform: scale(1.03);
    }

    /* Info Boxes */
    .stAlert {
        border-radius: 10px;
    }

    /* Footer */
    footer {
        visibility: hidden;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: #0E1117;
        text-align: center;
        color: #BBBBBB;
        padding: 10px;
        font-size: 0.9em;
    }

    /* Card Container */
    .card {
        background-color: #161A23;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER SECTION
# -------------------------------
st.markdown("<h1 style='text-align:center;'>🎬 Media Intelligence Suite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#BBBBBB;'>A unified platform for Emotion Detection, Scene Segmentation & Script Analysis</p>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2203/2203183.png", width=80)
st.sidebar.title("Navigation")

option = st.sidebar.radio(
    "Select a Module:",
    ["Emotion Detection in Video", "Scene Detection", "Script Analysis"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip:** Upload a file to begin processing.")
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 **Media Intelligence Suite**")
st.sidebar.markdown("<small>Built with ❤️ using Streamlit</small>", unsafe_allow_html=True)

# -------------------------------
# MODEL PATH
# -------------------------------
MODEL_PATH = os.path.join(os.getcwd(), "best.pt")

if not os.path.exists(MODEL_PATH):
    st.warning("⚠️ 'best.pt' model not found in this directory. Please ensure it's present.")

# -------------------------------
# MODULE 1: EMOTION DETECTION
# -------------------------------
if option == "Emotion Detection in Video":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("😊 Emotion Detection in Video")
    uploaded_video = st.file_uploader("🎥 Upload a video file", type=["mp4", "avi", "mov"])

    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_vid:
            temp_vid.write(uploaded_video.read())
            st.info("Running emotion detection... (Press 'q' in the pop-up window to stop)")
            try:
                detect_emotions_in_video(temp_vid.name, MODEL_PATH)
                st.success("✅ Emotion detection completed successfully.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# MODULE 2: SCENE DETECTION
# -------------------------------
elif option == "Scene Detection":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🎞 Scene Detection from Video")
    uploaded_video = st.file_uploader("🎬 Upload a video file", type=["mp4", "avi", "mov"])

    if uploaded_video:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_vid:
            temp_vid.write(uploaded_video.read())
            st.info("Analyzing scenes...")
            try:
                scenes = get_scene_boundaries_from_video(temp_vid.name)
                st.success("✅ Scenes detected successfully!")
                st.write("### 📍 Scene Boundaries:")
                for scene in scenes:
                    st.markdown(f"- {scene}")
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# MODULE 3: SCRIPT ANALYSIS
# -------------------------------
elif option == "Script Analysis":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📜 Screenplay Script Analysis")
    uploaded_pdf = st.file_uploader("📂 Upload a screenplay PDF", type=["pdf"])

    if uploaded_pdf:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(uploaded_pdf.read())
            st.info("Parsing screenplay...")
            try:
                parsed_data = parse_screenplay_pdf(temp_pdf.name)
                st.success(f"✅ Parsed {len(parsed_data)} pages successfully!")

                selected_page = st.slider("Select page to view", 1, len(parsed_data), 1)
                page_data = next((p for p in parsed_data if p["page"] == selected_page), None)
                if page_data:
                    st.json(page_data)
                else:
                    st.warning("No data found for this page.")
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("<div class='footer'>Media Intelligence Suite © 2025 | Built with ❤️ by Bhavya Gaur</div>", unsafe_allow_html=True)
