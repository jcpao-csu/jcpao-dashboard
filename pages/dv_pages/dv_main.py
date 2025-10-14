import streamlit as st
from pathlib import Path

# from cloudinary_assets import load_asset

st.markdown("<h1 style='text-align: center;'>:violet[Prosecuting Domestic Violence in Jackson County]</h1>", unsafe_allow_html=True)
st.write(" ")

cols = st.columns(2, vertical_alignment="top")

with cols[0]:

    intro_text = Path("assets/text/dv_pages/dv_intro.txt").read_text(encoding="utf-8")
    st.markdown(intro_text)

with cols[1]:

    press_conf_still = Path("assets/images/dv_pc/dv_pc_still4.png")
    st.image(
        press_conf_still,
        caption="Prosecuting Attorney Melesa Johnson giving remarks at the October 14, 2025 DV Press Conference",
        width="stretch"
    )

    with st.expander("Read Letter", expanded=False, icon="📄"):

        letter_image = Path("assets/images/dv_letter_2025_01_14.png")
        st.image(
            letter_image,
            caption="Prosecuting Attorney Melesa Johnson's Letter from January 14, 2025",
            width="stretch"
        )

    with st.expander("View Press Conference", expanded=False, icon="▶️"):
        youtube_url = "https://youtu.be/6ajaqyQ0k1c"
        st.video(
            youtube_url,
            autoplay=False,
            muted=False,
            width="stretch"
        )

    # st.pdf not working?
    # with st.expander("Read Prosecutor Johnson's January 2025 Letter [here](https://www.jacksoncountyprosecutor.com/DocumentCenter/View/2741/DV-Letter)", expanded=False, icon="📄"):
    #     letter_url = "https://www.jacksoncountyprosecutor.com/DocumentCenter/View/2741/DV-Letter"
    #     st.pdf(letter_url, height="stretch")




