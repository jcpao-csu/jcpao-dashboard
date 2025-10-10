# Establish session state in JCPAO Dashboard Streamlit app

import streamlit as st
from pathlib import Path
from datetime import datetime
from datetime import date
import pandas as pd

from read_data import RCVD, FLD, NTFLD, DISP

# --- Initialize datetime objects ---

today = datetime.now()
last_year = today.year - 1
next_year = today.year + 1

def initialize_year(select_year: int):
    jan_1 = datetime.date(select_year, 1, 1)
    dec_31 = datetime.date(select_year, 12, 31)

    q_dict = {
        1: (datetime.date(select_year, 1, 1), datetime.date(select_year, 3, 31)),
        2: (datetime.date(select_year, 4, 1), datetime.date(select_year, 6, 30)),
        3: (datetime.date(select_year, 7, 1), datetime.date(select_year, 9, 30)),
        4: (datetime.date(select_year, 10, 1), datetime.date(select_year, 12, 31))
    }

    return jan_1, dec_31, q_dict

# --- Import MSHP Codebook ---

def import_codebook(file_path: str = "assets/data/MSHP_2025_08_19.csv") -> pd.DataFrame:
    col_order = [
        "Charge Code",
        "Statute",
        "Severity",
        "Classification",
        "Offense Description (abridged)",
        "NCIC Category Code",
        "NCIC Category",
        "JCPAO Category Code",
        "JCPAO Category",
        "Legacy Code",
    ]
    df = pd.read_csv(
        Path(file_path),
        header=0,
        names=[
            "Charge Code",
            "Severity",
            "Classification",
            "Offense Description (abridged)",
            "MSHP Code",
            "NCIC Category Code",
            "Statute",
            "Offense Description (unabridged)",
            "OSCA Category",
            "Severity-Class Rank",
            "NCIC Category",
            "Legacy Code",
            "JCPAO Category",
            "JCPAO Category Code",
            "DV"
        ],
        usecols=col_order,
        encoding="utf-8"
    )

    return df# [[col_order]]

MSHP_CODEBOOK = import_codebook()

# --- Initialize st.session_state --- 

# st.session_state for main page
def initial_session_state():
    # if ("" not in st.session_state) or (True):
    #     st.session_state[""] = ""

    if "data" not in st.session_state:
        st.session_state["data"] = []

    # if "charge_category_filter" not in st.session_state:
    #     st.session_state["charge_category_filter"] = []

    if "police_agency_filter" not in st.session_state:
        st.session_state["police_agency_filter"] = []

    if "date_range_filter" not in st.session_state:
        st.session_state["date_range_filter"] = (date(last_year, date.today().month, date.today().day), date.today())

    if "def_race_filter" not in st.session_state:
        st.session_state["def_race_filter"] = "All"

    if "def_sex_filter" not in st.session_state:
        st.session_state["def_sex_filter"] = "All"

    # if "rcvd" not in st.session_state:
    #     st.session_state["rcvd"] = RCVD

    # if "fld" not in st.session_state:
    #     st.session_state["fld"] = FLD

    # if "ntfld" not in st.session_state:
    #     st.session_state["ntfld"] = NTFLD

    # if "disp" not in st.session_state:
    #     st.session_state["disp"] = DISP

# st.session_state for dashboard pages
def pages_session_state():

    if "data" not in st.session_state:
        st.session_state["data"] = []

    # if "charge_category_filter" not in st.session_state:
    #     st.session_state["charge_category_filter"] = []

    if "police_agency_filter" not in st.session_state:
        st.session_state["police_agency_filter"] = []

    if "date_range_filter" not in st.session_state:
        st.session_state["date_range_filter"] = (date(last_year, date.today().month, date.today().day), date.today())

    if "def_race_filter" not in st.session_state:
        st.session_state["def_race_filter"] = "All"

    if "def_sex_filter" not in st.session_state:
        st.session_state["def_sex_filter"] = "All"

# --- Define callback functions --- 

# Define update_df() function
def update_df():

    # Initialize DFs
    dfs = [RCVD, FLD, NTFLD, DISP] # Perform filtering on all four DFs 
    st.session_state["data"] = []
    df_counter = 0

    # Iterate over each DF one by one
    for df in dfs:
        
        # Filter by selected MSHP Charge Code Category
        if st.session_state["charge_category_filter"]:
            col_names = [col_name.upper() if col_name.upper()=="ESCAPE" else col_name.lower().replace(" ", "_") for col_name in st.session_state["charge_category_filter"]]
            df = df.loc[df[col_names].any(axis=1)].copy().reset_index(drop=True)

        # Filter by selected Referring Police Agency
        if st.session_state["police_agency_filter"]:
            df = df.loc[df["agency_name"].isin(st.session_state["police_agency_filter"])].copy().reset_index(drop=True)

        # Filter by selected Date Range
        if isinstance(st.session_state["date_range_filter"], tuple):

            # Filter if a date range has been established 2-len tuple
            if len(st.session_state["date_range_filter"])==2:

                # RCVD
                if df_counter == 0:
                    df = df.loc[
                        (df["ref_date"].dt.date >= st.session_state["date_range_filter"][0]) & 
                        (df["ref_date"].dt.date <= st.session_state["date_range_filter"][1])
                    ].copy().reset_index(drop=True)

                # FLD
                elif df_counter == 1:
                    df = df.loc[
                        (df["earliest_fld_date"].dt.date >= st.session_state["date_range_filter"][0]) & 
                        (df["earliest_fld_date"].dt.date <= st.session_state["date_range_filter"][1])
                    ].copy().reset_index(drop=True)

                # NTFLD 
                elif df_counter == 2:
                    df = df.loc[
                        (df["earliest_ntfld_date"].dt.date >= st.session_state["date_range_filter"][0]) & 
                        (df["earliest_ntfld_date"].dt.date <= st.session_state["date_range_filter"][1])
                    ].copy().reset_index(drop=True)

                # DISP
                elif df_counter == 3:
                    df = df.loc[
                        (df["earliest_disp_date"].dt.date >= st.session_state["date_range_filter"][0]) & 
                        (df["earliest_disp_date"].dt.date <= st.session_state["date_range_filter"][1])
                    ].copy().reset_index(drop=True)

            # Else warning
            elif len(st.session_state["date_range_filter"])==1:
                # st.warning("Please select a **start** and **end** date to filter the data accordingly.", icon="⚠️", width="stretch")
                # st.stop()
                continue

        # Filter by selected Def / Sus Race
        if st.session_state["def_race_filter"] != "All": 
            df = df.loc[df["def_race"]==st.session_state["def_race_filter"]].copy().reset_index(drop=True)

        # Filter by selected Def / Sus Gender 
        if st.session_state["def_sex_filter"] != "All":
            df = df.loc[df["def_sex"]==st.session_state["def_sex_filter"]].copy().reset_index(drop=True)

        # +1 counter
        df_counter += 1

        # Append to DFs list 
        st.session_state["data"].append(df)

# Reset filters button
def reset_filters():
    st.session_state["charge_category_filter"] = [] # MSHP Charge Code Categories
    st.session_state["police_agency_filter"] = [] # Referring Police Agencies
    st.session_state["date_range_filter"] = (date(last_year, date.today().month, date.today().day), date.today()) # Date Range
    st.session_state["def_race_filter"] = "All" # Def/Sus race
    st.session_state["def_sex_filter"] = "All" # Def/Sus gender
    
    # Run update_df callback to reset data
    update_df()


# --- Initiate interactive dashboard widgets ---

# Possible colors: red, orange, yellow, blue, green, violet, gray/grey, or "primary" (config.toml set 'theme.primaryColor')

def initiate_widgets(disabled: bool = False, color: str = "violet"):
    """
    Creates input widgets that help end user explore and interact with the data.
    Filters are inspired by Measures for Justice Commons dashboards ([see here](https://commons.measuresforjustice.org/prosecutor/jackson-county-mo))
    """

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

    # filter by referring police agency
    agency_dict = { 
        "Blue Springs PD": "Blue Springs PD", 
        "Buckner PD": "Buckner PD",
        "Grain Valley PD": "Grain Valley PD",
        "Grandview PD": "Grandview PD",
        "Greenwood PD": "Greenwood PD",
        "Independence PD": "Independence PD",
        "Jackson County Sheriff": "Jackson County Sheriff", 
        "JCDTF": "Jackson County Drug Task Force", # (JCDTF)
        "KCPD": "KCPD", 
        "Lake Lotawana PD": "Lake Lotawana PD",
        "Lake Tapawingo PD": "Lake Tapawingo PD",
        "Lee's Summit PD": "Lee's Summit PD",
        "Lone Jack PD": "Lone Jack PD",
        "Missouri State Highway Patrol": "Missouri State Highway Patrol", # MSHP
        "Oak Grove PD": "Oak Grove PD",
        "Raytown PD": "Raytown PD",
        "Sugar Creek PD": "Sugar Creek PD",
        "Other In-County": "Other In-County Agencies",
        "Other In-State": "Other In-State Agencies",
        "Out-of-State": "Out-of-State Agencies",
        "State Agencies": "State Agencies",
        "Federal Agencies": "Federal Agencies",
        "Other": "Other Agencies"
    }

    filter_police = st.multiselect(
        f":{color}-background[:{color}[**Referring Police Agency**] 🚔]",
        options=agency_dict.keys(),
        default=[],
        format_func=lambda x: agency_dict[x],
        key="police_agency_filter",
        help="Select the police agencies' referred case data you would like to examine through the dashboard.",
        on_change=update_df,
        max_selections=5,
        placeholder="All",
        disabled=disabled,
        label_visibility="visible",
        accept_new_options=False,
        width="stretch"
    )

    # Date range filter: (a) last 12 months; (b) year / current year ytd (default); (c) month; (d) quarterly (q1: jan-mar / q2: apr-jun / q3: jul-sept / q4: oct-dec); (e) date
    filter_date_range = st.date_input( # start_date, end_date
        f":{color}-background[:{color}[**Date Range**] 📆]",
        value=(date(last_year, date.today().month, date.today().day), date.today()), # last 12 months
        min_value=date(2016, 1, 1),
        max_value=date.today(),
        key="date_range_filter",
        help="Select the date range of the data you would like to examine through the dashboard.",
        on_change=update_df,
        format="MM/DD/YYYY",
        disabled=disabled,
        label_visibility="visible",
        width="stretch"
    )

    # def race
    def_race_dict = {
        "All": "All",
        "A": "Asian",
        "B": "Black / African American",
        "H": "Hispanic",
        "I": "American Indian / Alaska Native",
        "M": "Multiple",
        "P": "Pacific Islander",
        "W": "White (Non-Latino) / Caucasian",
        "U": "Unknown"
    }

    filter_def_race = st.selectbox(
        label=f":{color}-background[:{color}[**Race**] 👤]",
        options=def_race_dict.keys(),
        index=0,
        format_func=lambda x: def_race_dict[x],
        key="def_race_filter",
        help="Select the suspect/defendant race of the data you would like to examine through the dashboard.",
        on_change=update_df,
        placeholder="Select race to filter",
        disabled=disabled,
        label_visibility="visible",
        accept_new_options=False,
        width="stretch"
    )

    # def sex
    def_sex_dict = {
        "All" : "All",
        "F": "Female",
        "M": "Male",
        "O": "Other",
        "U": "Unknown"
    }

    filter_def_sex = st.selectbox(
        label=f":{color}-background[:{color}[**Gender**] 🚻]", 
        options=def_sex_dict.keys(),
        index=0,
        format_func=lambda x: def_sex_dict[x],
        key="def_sex_filter",
        help="Select the suspect/defendant gender of the data you would like to examine through the dashboard.",
        on_change=update_df,
        placeholder="Select gender to filter",
        disabled=disabled,
        label_visibility="visible",
        accept_new_options=False,
        width="stretch"
    )

    # def age 

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
    return filter_category, filter_police, filter_date_range, filter_def_race, filter_def_sex


# filter_category, filter_police, filter_date_range, filter_def_race, filter_def_sex = initiate_widgets()

# st.write(start_date, end_date)

# st.write("Charge Code Category:")
# st.write(filter_category)

# st.write("Police Agency:")
# st.write(filter_police)

# st.write("Date Range:")
# st.write(filter_date_range)

# st.write("Defendant Race:")
# st.write(filter_def_race)

# st.write("Defendant Gender:")
# st.write(filter_def_sex)
