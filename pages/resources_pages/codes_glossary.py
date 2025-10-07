import streamlit as st

from session_state import MSHP_CODEBOOK

# --- Initialize session state ---
if "codes_glossary" not in st.session_state:
    st.session_state["codes_glossary"] = MSHP_CODEBOOK

# --- Streamlit page title ---

st.markdown("<h1 style='text-align: center;'>MSHP Charge Codes Glossary</h1>", unsafe_allow_html=True)
st.divider()

# --- Define callback functions --- 

# Define update_df() function
def update_df():

    st.session_state["codes_glossary"] = MSHP_CODEBOOK

    # Filter by selected MSHP Charge Code Category
    if st.session_state["charge_category_filter"]:
        # col_names = [col_name.upper() if col_name.upper()=="ESCAPE" else col_name.lower().replace(" ", "_") for col_name in st.session_state["charge_category_filter"]]
    
        df = st.session_state["codes_glossary"]
        df = df.loc[df["JCPAO Category"].isin(st.session_state["charge_category_filter"])].copy().reset_index(drop=True)

        # Reassign to session state
        st.session_state["codes_glossary"] = df

# Reset filters button
def reset_filters():
    st.session_state["charge_category_filter"] = [] # MSHP Charge Code Categories
    st.session_state["codes_glossary"] = MSHP_CODEBOOK

# Create widget filter
def initiate_widgets(disabled: bool = False, color: str = "violet"):

    # filter by charge category / offense type
    filter_category = st.multiselect(
        f":{color}-background[:{color}[**Charge Code Category ^**] 📖]",
        sorted(MSHP_CODEBOOK["JCPAO Category"].unique().tolist()),
        default=[],
        # format_func=None,
        key="charge_category_filter",
        help="Select the charge code categories of the data you would like to examine through the dashboard.",
        on_change=update_df,
        max_selections=5,
        placeholder="All",
        disabled=disabled,
        label_visibility="visible",
        accept_new_options=False,
        width="stretch"
    )

    # Reset filters 
    st.write(" ")
    refresh = st.button(
        label="Reset Filters",
        key="reset_filter",
        help="Resets filters above and returns dashboard to original display.",
        on_click=reset_filters,
        type="secondary",
        icon="🔄",
        disabled=disabled,
        width="stretch"
    )

    st.divider()

    st.caption(
        """
        ^ Charge codes are manually grouped into unique categories established by the JCPAO. 
        The categories are in part taken from the National Crime Information Center (NCIC), 
        a database maintained by the FBI that provides law enforcement agencies across the 
        US with access to crime data. The NCIC has established a uniform classification sytem, 
        which has also been adopted by the Missouri State Highway Patrol in the maintenance 
        of the state criminal charge code.
        """
    ) # https://www.mshp.dps.missouri.gov/CJ08Client/Home/ChargeCode

    # Produce variables
    return filter_category


# --- st.sidebar ---
with st.sidebar:
    st.title("Jackson County Prosecuting Attorney's Office")
    st.write("**Missouri Criminal Charge Codes Glossary**")
    st.write("Learn more about the unique criminal charge codes in the state of Missouri.")
    st.divider()
    filter_category = initiate_widgets(False, "blue")


# --- Display DF ---

df = st.dataframe(
    data=st.session_state["codes_glossary"],
    width="stretch",
    height=1000,
    hide_index=True,
)