import streamlit as st
import requests
import base64
from pathlib import Path


st.set_page_config(
    page_title="Swizio AI Diagram Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []


def image_to_base64(path):
    """Convert image to base64."""
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


st.markdown("""
<style>
    /* --- General Styles --- */
    body {
        color: #ffffff;
    }
    .stApp {
        background-color: #1e1e2e;
    }
    .stButton>button {
        border: 2px solid #00d4ff;
        border-radius: 12px;
        padding: 10px 24px;
        background-color: transparent;
        color: #00d4ff;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #1e1e2e;
        border-color: #00d4ff;
    }
    .stButton>button:focus {
        box-shadow: 0 0 0 2px #8b5cf6;
    }
    .stTextArea>div>div>textarea, .stTextInput>div>div>input {
        background-color: #2a2a3e;
        border-radius: 8px;
        border: 1px solid #8b5cf6;
        color: #ffffff;
    }
    .stSpinner > div > div {
        border-top-color: #00d4ff;
        border-right-color: #00d4ff;
    }

    /* --- Card & Container Styles --- */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #2a2a3e;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #8b5cf6;
    }

    /* --- Title Styles --- */
    .title-gradient {
        background: -webkit-linear-gradient(45deg, #00d4ff, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h1 class='title-gradient'>Swizio AI</h1>", unsafe_allow_html=True)
    st.markdown("Your intelligent architecture diagramming assistant.")
    st.markdown("---")
    st.markdown("### Quick Prompts")

    templates = {
        "Web App": "A standard web application with a user, a load balancer, two web servers, and a database.",
        "API Gateway": "An API Gateway with three microservices behind it, each connected to its own database.",
        "Data Pipeline": "A data pipeline with a Kafka source, a Spark processing cluster, and writing to an S3 bucket."
    }

    for name, prompt_text in templates.items():
        if st.button(name):
            st.session_state.prompt_text = prompt_text

    st.markdown("---")
    st.markdown("### Generation History")
    if not st.session_state.prompt_history:
        st.info("Your generated prompts will appear here.")
    else:
        for i, p in enumerate(st.session_state.prompt_history[-5:]):
            if st.button(f"🔄 {p[:30]}...", key=f"history_{i}"):
                st.session_state.prompt_text = p

st.markdown("<h1 class='title-gradient' style='text-align: center;'>AI Diagram Generator</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #a1a1aa;'>Transform your imagination into stunning architecture visuals</p>",
    unsafe_allow_html=True)

main_cols = st.columns((6, 5), gap="large")

with main_cols[0]:
    with st.container():
        st.markdown("### 1. Describe Your Vision")
        prompt = st.text_area(
            "**Enter your description here:**",
            placeholder="e.g., A web application with a load balancer, two web servers, and a database.",
            height=150,
            key="prompt_text"
        )

        if st.button("✨ Generate Diagram", use_container_width=True):
            if prompt:
                with st.spinner("Generating diagram... This may take a moment."):
                    try:
                        response = requests.post("http://localhost:8000/diagrams/generate", json={"prompt": prompt})

                        if response.status_code == 200:
                            st.toast("Diagram generated successfully!", icon="🎉")
                            st.session_state.generated_images.append(response.content)
                            st.session_state.prompt_history.append(prompt)
                        else:
                            st.error(f"Error: Backend returned status {response.status_code}. Check logs for details.")

                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection Error: Could not connect to the backend. Please ensure it's running.")
            else:
                st.warning("Please enter a description for the diagram.")

with main_cols[1]:
    with st.container():
        st.markdown("### 2. Your Generated Diagram")
        if not st.session_state.generated_images:
            st.info("Your generated diagram will appear here.")
        else:
            latest_image = st.session_state.generated_images[-1]
            st.image(latest_image, caption="Latest Diagram", use_container_width=True)
            st.download_button(
                label="📥 Download Diagram",
                data=latest_image,
                file_name="generated_diagram.png",
                mime="image/png",
                use_container_width=True
            )

st.markdown("---")
st.markdown("<h2 class='title-gradient' style='text-align: center;'>Your Gallery</h2>", unsafe_allow_html=True)

if not st.session_state.generated_images:
    st.info("Previously generated images will be shown here.")
else:
    gallery_cols = st.columns(4)
    for i, img_bytes in enumerate(reversed(st.session_state.generated_images)):
        col_index = i % 4
        with gallery_cols[col_index]:
            st.image(img_bytes, use_container_width=True, caption=f"Gen #{len(st.session_state.generated_images) - i}")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #a1a1aa;'>Made with ❤️ by Swizio</p>",
    unsafe_allow_html=True
)
