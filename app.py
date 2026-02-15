import streamlit as st
import datetime
from config import config
from dotenv import load_dotenv

# from langfuse import get_client

load_dotenv(override=True)

# langfuse = get_client()

# Verify connection
# if langfuse.auth_check():
#    print("Langfuse client is authenticated and ready!")
# else:
#    print("Authentication failed. Please check your credentials and host.")


if "init" not in st.session_state:
    st.session_state.init = True

pages = [
    st.Page("pages/Home.py", title="Home", icon=":material/home:"),
    st.Page(
        "pages/Medical_Image_Analysis.py",
        title="Medical Image Analysis",
        icon=":material/diagnosis:",
    ),
    # st.Page(
    #    "pages/Experts_Chat.py",
    #    title="Experts Chat",
    #    icon=":material/chat:"
    # ),
    st.Page(
        "pages/Generated_Images.py",
        title="Generated Images",
        icon=":material/photo_library:",
    ),
    st.Page(
        "pages/Configuration.py", title="Configuration", icon=":material/settings:"
    ),
    st.Page(
        "pages/About.py",
        title="About",
        # icon=":material/widgets:"
        icon=":material/info:",
    ),
]

page = st.navigation(pages)
page.run()


# with st.sidebar.container(height=310):
#    if page.title == "Home":
#        pass
#    elif page.title == "About":
#        pass
#    else:
#        pass

st.sidebar.markdown(" ")
st.sidebar.caption(
    f"©  {datetime.date.today().year} | Made with :material/favorite: by [{config.COMPANY}]({config.COMPANY_URL})"
)
