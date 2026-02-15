"""
About Page
This page provides information about the GodsinWhite Agent Interface.
"""

import os
import streamlit as st
import sys

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Set page config
st.set_page_config(
    page_title="GodsinWhite About",
    page_icon=config.LOGO_ICON_PATH,
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH, size="large", icon_image=config.LOGO_ICON_PATH)

# Page title
one_cola = st.columns([1])[0]
with one_cola:
    col1a, col2a = st.columns([2, 6])

    with col1a:
        # team_image = config.LOGO_TEAM_PATH
        st.image(config.LOGO_TEAM_PATH, width=400)
        # st.image(team_image, width=400)
    with col2a:
        st.markdown(
            """
        # Gods in White  
         *A Corpus Analytica Innovation*
        """,
            unsafe_allow_html=True,
        )

height = 50
st.markdown(f'<div style="height: {height}px;"></div>', unsafe_allow_html=True)

# --- Content ---
st.markdown("""
# Corpus Analytica - Your Trusted Partner in Healthcare

At [Corpus Analytica](https://www.corpusanalytica.com), we redefine how medical professionals and patients connect—through a platform built for simplicity, security, and global reach.

#### What We Offer:
- Seamless Connections: We unite doctors, specialists, and patients through our cutting-edge digital platform.

- Expert Second Opinions: Gain easy access to a network of certified physicians and specialists for reliable second opinions.

- Effortless Booking: Our intuitive interface makes requesting and scheduling consultations fast and frustration-free.

- Global Access: Wherever you are, our online consultations bring expert medical advice right to your screen.

- Data You Can Trust: We uphold the highest standards in data protection and patient privacy—because your health deserves nothing less.

#### Experience Healthcare in a New Dimension
Your health is invaluable. With Corpus Analytica, discover a smarter, safer, and more connected way to care.

> *"Healthcare should be accessible, transparent, and empowering. At Corpus Analytica, we're building more than just a platform—we're building trust, one consultation at a time."* — Bernhard Z., Founder of [Corpus Analytica](https://www.corpusanalytica.com)

""")

height = 50
st.markdown(f'<div style="height: {height}px;"></div>', unsafe_allow_html=True)
