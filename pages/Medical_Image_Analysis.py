import os
import io
import streamlit as st
import pydicom
import numpy as np
from agno.media import Image as AgnoImage
from agents.medical_agent import agent
from PIL import Image as PILImage
from config import config
import datetime


# Set page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Medical Image Analysis",
    page_icon="🩺",
    layout="wide",
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH,
    size="large",
    icon_image=config.LOGO_ICON_PATH
)

def main():
    with st.sidebar:
        st.info(
            "This tool provides AI-powered analysis of medical imaging data using "
            "advanced computer vision and radiological expertise."
        )
        st.warning(
            "DISCLAIMER: This tool is for show cases and informational purposes only. "
            "All analyses should be reviewed by qualified healthcare professionals. "
            "Do not make medical decisions based solely on this analysis."
        )

    # Page title
    one_cola = st.columns([1])[0]
    with one_cola:
        col1a, col2a = st.columns([1, 5])

        with col1a:
            team_image = config.ASSETS_DIR / "godsinwhite_radiologist.png" 
            st.image(team_image, width=100)
        with col2a:
            st.markdown("""
            # Medical Imaging Diagnosis Agent  
            Upload a medical image for professional analysis
            """, unsafe_allow_html=True)

    # Create containers for better organization
    upload_container = st.container()
    image_container = st.container()
    analysis_container = st.container()

    with upload_container:
        uploaded_file = st.file_uploader(
            "Upload Medical Image",
            type=["jpg", "jpeg", "png", "dicom", "dcm"],
            help="Supported formats: JPG, JPEG, PNG, DICOM, DCM",
        )

    if uploaded_file is not None:
        with image_container:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Check if file is DICOM or regular image
                file_extension = uploaded_file.name.split('.')[-1].lower()

                if file_extension in ['dicom', 'dcm'] or uploaded_file.type == 'application/dicom':
                    # Handle DICOM files
                    try:
                        # Reset file pointer to beginning
                        uploaded_file.seek(0)
                        # Read the DICOM file
                        dicom_data = pydicom.dcmread(uploaded_file)
                        
                        # Convert DICOM to array that PIL can handle
                        img_array = dicom_data.pixel_array
                        
                        # Normalize the image for display
                        img_array = img_array / img_array.max() * 255
                        img_array = img_array.astype(np.uint8)
                        
                        # Convert numpy array to PIL Image
                        pil_image = PILImage.fromarray(img_array)

                        # If grayscale, convert to RGB for better display
                        if len(img_array.shape) == 2:
                            pil_image = pil_image.convert('RGB')

                    except Exception as e:
                        st.error(f"Error processing DICOM file: {str(e)}")
                        st.stop()
                else:
                    # Handle regular image files with PIL
                    pil_image = PILImage.open(uploaded_file)
                
                # Resize the image for display
                width, height = pil_image.size
                aspect_ratio = width / height
                new_width = 500
                new_height = int(new_width / aspect_ratio)
                resized_image = pil_image.resize((new_width, new_height))

                st.image(
                    resized_image,
                    caption="Uploaded Medical Image",
                    width="stretch",
                )

                analyze_button = st.button(
                    ":material/search: Analyze Image", type="primary", width="stretch"
                )

                additional_info = st.text_area(
                    "Provide additional context about the image (e.g., patient history, symptoms)",
                    placeholder="Enter any relevant information here...",
                )

        with analysis_container:
            if analyze_button:
                image_path = "temp_medical_image.png"
                # Save the resized image
                resized_image.save(image_path, format="PNG")
                
                # Add DICOM metadata to additional info if available
                if file_extension == 'dicom' or uploaded_file.type == 'application/dicom':
                    try:
                        uploaded_file.seek(0)
                        dicom_data = pydicom.dcmread(uploaded_file)
                        dicom_info = f"\n\nDICOM Metadata:\n"
                        for tag in ['PatientID', 'PatientName', 'PatientAge', 'PatientSex', 'Modality', 'StudyDescription']:
                            if hasattr(dicom_data, tag) and getattr(dicom_data, tag) != '':
                                dicom_info += f"- {tag}: {getattr(dicom_data, tag)}\n"
                        
                        if additional_info:
                            additional_info += dicom_info
                        else:
                            additional_info = dicom_info
                    except Exception as e:
                        st.warning(f"Could not extract DICOM metadata: {str(e)}")

                with st.spinner(":material/cycle: Analyzing image... Please wait."):
                    try:
                        # Read the image file as binary
                        with open(image_path, "rb") as f:
                            image_bytes = f.read()
                        # creating an instance of Image
                        agno_image = AgnoImage(content=image_bytes, format="png")

                        prompt = (
                            f"Analyze this medical image considering the following context: {additional_info}"
                            if additional_info
                            else "Analyze this medical image and provide detailed findings."
                            + "\n\n"
                            + "If you are not sure about the diagnosis, please provide a possible diagnosis."
                            + "\n\n"
                            + "Answer in the language of the user. If it is not given, answer English."
                        )
                        model = "gpt-5"
                        response = agent.run(prompt, images=[agno_image], model=model)
                        st.markdown("### :material/diagnosis: Analysis Results")
                        st.markdown("---")
                        if hasattr(response, "content"):
                            st.markdown(response.content)
                        elif isinstance(response, str):
                            st.markdown(response)
                        elif isinstance(response, dict) and "content" in response:
                            st.markdown(response["content"])
                        else:
                            st.markdown(str(response))
                        st.markdown("---")
                        st.caption(
                            "Note: This analysis is generated by AI and should be reviewed by "
                            "a qualified healthcare professional."
                        )

                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
                        st.info(
                            "Please try again or contact support if the issue persists."
                        )
                        print(f"Detailed error: {e}")
                    finally:
                        if os.path.exists(image_path):
                            os.remove(image_path)

    else:
        st.info(":material/upload: Please upload a medical image to begin analysis")


if __name__ == "__main__":
    main()
