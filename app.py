import streamlit as st
import cv2
import database
from alpr_engine import AFACSEngine
from PIL import Image
import numpy as np

# Page configuration
st.set_page_config(page_title="NextGen ALPR: AFACS", page_icon="🚘", layout="wide")

@st.cache_resource
def get_engine():
    return AFACSEngine()

# Initialize Database
database.init_db()

st.title("🚘 Autonomous Fleet Access & Compliance System (AFACS)")
st.markdown("""
**Welcome to the future of smart-city traffic management.** 
Upload an image of a vehicle to simulate the edge-node AI processing. The system will detect the vehicle, extract its license plate, and check the decentralized ledger for zone compliance.
""")

col1, col2 = st.columns([1, 1])

engine = get_engine()

with col1:
    st.header("1. Edge Node Camera Feed")
    uploaded_file = st.file_uploader("Upload Vehicle Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="Raw Camera Feed", use_column_width=True)
        
        with st.spinner("Processing through AFACS Deep Learning Pipeline..."):
            out_img, plates_found = engine.process_image(image_bytes)
            
        with col2:
            st.header("2. AI Analysis & Ledger Result")
            if out_img is not None and plates_found:
                # Convert BGR to RGB for Streamlit
                out_img_rgb = cv2.cvtColor(out_img, cv2.COLOR_BGR2RGB)
                st.image(out_img_rgb, caption="YOLOv8 Detection & EasyOCR Reading", use_column_width=True)
                
                best_plate = plates_found[0]['text']
                conf = plates_found[0]['confidence']
                
                st.subheader(f"Extracted Plate: `{best_plate}`")
                st.write(f"OCR Confidence: {conf*100:.1f}%")
                
                # Check ledger
                st.markdown("### Ledger Verification")
                compliance = database.check_compliance(best_plate)
                
                if compliance['status'] == "AUTHORIZED":
                    st.success("✅ VEHICLE AUTHORIZED FOR ZONE ENTRY")
                else:
                    st.error("❌ VEHICLE RESTRICTED: ENTRY DENIED")
                    
                st.json(compliance)
                
                # Hidden registration feature for demo purposes
                with st.expander("Admin: Register Plate"):
                    new_company = st.text_input("Fleet Company", "Test Fleet Ltd.")
                    new_emission = st.selectbox("Emission Class", ["Zero Emission", "Hybrid", "Diesel"])
                    if st.button("Register & Authorize"):
                        database.register_plate(best_plate, new_company, new_emission, "AUTHORIZED")
                        st.success("Plate registered! Upload image again to see updated ledger.")

            else:
                st.warning("No vehicles or readable license plates found in the image. Ensure the image is clear.")
