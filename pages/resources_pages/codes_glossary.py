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

    # st.session_state["codes_glossary"] = MSHP_CODEBOOK
    df = MSHP_CODEBOOK

    # Filter by selected MSHP Charge Code Category
    if st.session_state["charge_category_filter"]:
        # col_names = [col_name.upper() if col_name.upper()=="ESCAPE" else col_name.lower().replace(" ", "_") for col_name in st.session_state["charge_category_filter"]]
    
        # df = st.session_state["codes_glossary"]
        df = df.loc[df["JCPAO Category"].isin(st.session_state["charge_category_filter"])].copy().reset_index(drop=True)

    # Filter by legacy charge code 
    # if st.session_state["legacy_code_filter"]:
    df = df.loc[df["Legacy Code"]].copy().reset_index(drop=True)

    # Filter by charge severity
    if st.session_state["severity_filter"] != "All":
        if st.session_state["severity_filter"] == "O": # Other
            df = df[df["Severity"].isin(["A", "U"])].copy().reset_index(drop=True)
        else:
            df = df[df["Severity"]==st.session_state["severity_filter"]].reset_index(drop=True)
    
        # Reassign to session state
        st.session_state["codes_glossary"] = df

# Reset filters button
def reset_filters():
    st.session_state["charge_category_filter"] = [] # MSHP Charge Code Categories
    st.session_state["codes_glossary"] = MSHP_CODEBOOK
    st.session_state["legacy_code_filter"] = False
    st.session_state["severity_filter"] = "All"

# Create widget filter
def initiate_widgets(disabled: bool = False, color: str = "violet"):

    # filter by active charge code 
    filter_legacy = st.toggle(
        f":{color}-background[:{color}[**Active Charge Codes Only**] 🚔]",
        value=False,
        key="legacy_code_filter",
        help="Filter charge codes to only view ones that are currently active.",
        on_change=update_df,
        disabled=disabled,
        width="stretch"
    )

    # filter by charge category / offense type
    filter_category = st.multiselect(
        f":{color}-background[:{color}[**Charge Code Category ^**] 📖]",
        sorted(MSHP_CODEBOOK["JCPAO Category"].unique().tolist()),
        default=[],
        # format_func=None,
        key="charge_category_filter",
        help="Select (up to five) charge code categories.",
        on_change=update_df,
        max_selections=5,
        placeholder="All",
        disabled=disabled,
        label_visibility="visible",
        accept_new_options=False,
        width="stretch"
    )

    # filter by charge code severity
    sev_dict = {
        "All": "All Charge Codes",
        "F": "Felony",
        "M": "Misdemeanor",
        "I": "Infraction",
        "L": "Ordinance",
        "O": "Other" # A or U
    }
    filter_sev = st.selectbox(
        f":{color}-background[:{color}[**Charge Code Severity**] ⚖️]",
        options=sev_dict.keys(),
        index=0,
        format_func=lambda x: sev_dict[x],
        key="severity_filter",
        help="Filter charge codes by severity.",
        on_change=update_df,
        placeholder="Select charge severity to filter",
        disabled=disabled,
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
    return filter_category, filter_legacy, filter_sev


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