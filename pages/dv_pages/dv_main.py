import streamlit as st
from pathlib import Path

# from cloudinary_assets import load_asset

st.markdown("<h1 style='text-align: center;'>Prosecuting Domestic Violence in Jackson County</h1>", unsafe_allow_html=True)
st.write(" ")

cols = st.columns(2)

with cols[0]:
    intro_text = Path("assets/text/dv_pages/dv_intro.txt").read_text(encoding="utf-8")
    st.markdown(intro_text)

with cols[1]:
    with st.expander("Read Prosecutor Johnson's January 2025 Letter", expanded=False, icon="📄"):
        # pdf_url = load_asset("2025_01_14_dv_letter") # "2025_01_14_dv_letter"
        # st.pdf(pdf_url, height="stretch")

        pdf_path = Path("dv_letter_2025_01_14.pdf") # assets/pdfs/
        st.pdf(pdf_path, height="stretch")




