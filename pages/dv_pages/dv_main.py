import streamlit as st
from pathlib import Path

# from cloudinary_assets import load_asset

st.markdown("<h1 style='text-align: center;'>Prosecuting Domestic Violence in Jackson County</h1>", unsafe_allow_html=True)
st.write(" ")
# st.write("This page is still under construction. Please come back later! 🚧")

cols = st.columns(2)

with cols[0]:
    intro_text = Path("assets/text/dv_pages/dv_intro.txt").read_text(encoding="utf-8")
    st.markdown(intro_text)

with cols[1]:
    with st.expander("Read Prosecutor Johnson's January 2025 Letter", expanded=False, icon="📄"):
        # load_asset("2025_01_14_dv_letter") 
        # pages/dv_pages/dv_letter_2025_01_14.pdf 
        # assets/pdfs/dv_letter_2025_01_14.pdf
        pdf_path = Path("assets/pdfs/dv_letter_2025_01_14.pdf") 
        st.pdf(pdf_path, height="stretch")

