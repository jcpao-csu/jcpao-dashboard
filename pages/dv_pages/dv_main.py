import streamlit as st
from pathlib import Path

# from cloudinary_assets import load_asset

st.markdown("<h1 style='text-align: center;'>Prosecuting Domestic Violence in Jackson County</h1>", unsafe_allow_html=True)
st.write(" ")

cols = st.columns(2, vertical_alignment="top")

with cols[0]:
    intro_text = Path("assets/text/dv_pages/dv_intro.txt").read_text(encoding="utf-8")
    st.markdown(intro_text)

with cols[1]:

    with st.expander("Read Letter", expanded=False, icon="📄"):

        letter_image = Path("assets/images/dv_letter_2025_01_14.png")
        st.image(
            letter_image,
            caption="Prosecuting Attorney Melesa Johnson's Letter from January 14, 2025",
            width="stretch"
        )
    # st.pdf not working?
    # with st.expander("Read Prosecutor Johnson's January 2025 Letter [here](https://www.jacksoncountyprosecutor.com/DocumentCenter/View/2741/DV-Letter)", expanded=False, icon="📄"):
    #     letter_url = "https://www.jacksoncountyprosecutor.com/DocumentCenter/View/2741/DV-Letter"
    #     st.pdf(letter_url, height="stretch")




