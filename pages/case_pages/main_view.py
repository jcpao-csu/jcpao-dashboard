import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

from read_data import query_table
from read_data import RCVD, FLD, NTFLD, DISP

# --- Streamlit page title ---

st.markdown("<h1 style='text-align: center;'>JCPAO Dashboard Overview</h1>", unsafe_allow_html=True)
st.divider()

# --- Initialize session state --- 

if "rcvd" not in st.session_state:
    st.session_state["rcvd"] = RCVD

if "fld" not in st.session_state:
    st.session_state["fld"] = FLD

if "ntfld" not in st.session_state:
    st.session_state["ntfld"] = NTFLD

if "disp" not in st.session_state:
    st.session_state["disp"] = DISP

# --- Define callback functions --- 

# # Define update_df() function
# def update_df():

#     filtered_df = concat_df.copy()

#     if st.session_state["dir_selected_position"] != 'All':
#         filtered_df = filtered_df[filtered_df['Position']==st.session_state["dir_selected_position"]].reset_index(drop=True)
#     if st.session_state["dir_selected_unit"] != 'All':
#         filtered_df = filtered_df[filtered_df['Assigned Unit'].apply(lambda x: st.session_state["dir_selected_unit"] in x)].reset_index(drop=True)
#     if st.session_state["dir_selected_location"] != 'All': 
#         filtered_df = filtered_df[filtered_df['Office Location']==st.session_state["dir_selected_location"]].reset_index(drop=True)
#     if st.session_state["dir_selected_month"] != 'All':
#         filtered_df = filtered_df[filtered_df['DOB Month']==int(st.session_state["dir_selected_month"])].reset_index(drop=True)
#     if st.session_state["dir_searched_text"]: # Added searched_text to main clickback action 
#         searched_text = st.session_state["dir_searched_text"].strip().lower()
#         search_cols = ["Full Name", "First Name", "Middle Name", "Last Name", "Suffix", "Preferred Name"]
#         filtered_df = filtered_df[
#             filtered_df[search_cols].apply(lambda row: any(searched_text in str(value).lower() for value in row), axis=1)
#         ].reset_index(drop=True)

#     st.session_state["dir_filtered_df"] = filtered_df.reset_index(drop=True)

# # Reset filters button
# def reset_filters():
#     st.session_state["dir_selected_position"] = "All"
#     st.session_state["dir_selected_unit"] = "All"
#     st.session_state["dir_selected_location"] = "All"
#     st.session_state["dir_selected_month"] = "All"
#     st.session_state["dir_searched_text"] = ""
#     filtered_df = concat_df.copy()
#     st.session_state["dir_filtered_df"] = filtered_df

# --- Streamlit sidebar --- 
with st.sidebar:
    st.title("Jackson County Prosecuting Attorney's Office")
    st.write("**JCPAO Dashboard Overview**")
    st.write("Welcome to the JCPAO Dashboard! Please use the interactive widgets below to explore the dashboard:")
    st.divider()



# Total Rcvd / Fld / Ntfld / Disp YTD 

def total_ytd(df: pd.DataFrame, date_col: str, metric_label: str, chart_type: str, show_metric: bool = True):

    # Prepare DF for groupby
    df[date_col] = pd.to_datetime(df[date_col])
    df["year"] = df[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    df["month"] = df[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    # # Current year (today's date)
    # df_current_ytd = df[(df["year"] == current_year) & (df[date_col] <= today)]

    # # Same date previous year
    # df_last_ytd = df[(df["year"] == current_year - 1) &
    #                 (df["month"] < today.month) |
    #                 ((df["month"] == today.month) & (df[date_col].dt.day <= today.day))]

    # Filter DF to cases received as of today's date 
    mask = (
        (df[date_col].dt.month < today.month) |
        ((df[date_col].dt.month == today.month) & (df[date_col].dt.day <= today.day))
    )

    df = df[mask]

    # Group by
    annual_count = df.groupby("year")["pbk_num"].count().reset_index()
    annual_count.rename(columns={"pbk_num": "total_cases"}, inplace=True)

    # Sparkline 
    sparkline_data = annual_count["total_cases"].tolist()

    # Delta
    # current_total = df_current_ytd["pbk_num"].nunique()
    # last_total = df_last_ytd["pbk_num"].nunique()
    # delta = current_total - last_total # sparkline_data[-1] - sparkline_data[-2] // year-to-year change)
    delta = sparkline_data[-1] - sparkline_data[-2]

    # Calculate % difference
    if sparkline_data[-2] == 0:
        delta_pct = "N/A"
    else:
        delta_pct = f"{(delta / sparkline_data[-2] * 100):+.1f}%"

    if show_metric:
        st.metric(
            label=metric_label,
            value=f"{sparkline_data[-1]} cases",
            delta=f"{delta} (YoY) | {delta_pct}", # ({last_total} YTD {current_year - 1})
            # delta_color="off",
            # width="content",
            chart_data=sparkline_data,
            chart_type=chart_type,
            border=True
        )
    # else:
    #     st.write(f"Compare with: *{last_total} ({current_year - 1} YTD)*")

# YTD Metrics

st.markdown("<h4 style='text-align: center;'>Criminal Cases Processed Year-to-Date</h4>", unsafe_allow_html=True)
st.write(" ")
ytd_metrics = st.container(horizontal=True)
st.write(" ")

with ytd_metrics:

    rcvd_ytd, fld_ytd, ntfld_ytd, disp_ytd = st.columns(4)

    with rcvd_ytd:
        total_ytd(RCVD, "ref_date", "***Total Received (YTD)***", "area")
    
    with fld_ytd:
        total_ytd(FLD, "earliest_fld_date", "***Total Filed (YTD)***", "area")

    with ntfld_ytd:
        total_ytd(NTFLD, "earliest_ntfld_date", "***Total Not Filed (YTD)***", "area")
    
    with disp_ytd:
        total_ytd(DISP, "earliest_disp_date", "***Total Disposed (YTD)***", "area")

# Cases by Year and Category 

def total_by_year(rcvd: pd.DataFrame, fld: pd.DataFrame, ntfld: pd.DataFrame, disp: pd.DataFrame) -> pd.DataFrame:

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    def prep_df(df: pd.DataFrame, date_col: str, status: str) -> pd.DataFrame:

        # Prepare DF for groupby
        df[date_col] = pd.to_datetime(df[date_col])
        df["Year"] = df[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
        df["Month"] = df[date_col].dt.month

        # Group by
        df = df.groupby("Year")["pbk_num"].count().reset_index()
        df.rename(columns={"pbk_num": "Total Cases"}, inplace=True)

        df["Case Status"] = status

        return df

    # Create list of DFs 
    rcvd = prep_df(rcvd, "ref_date", "Received")
    fld = prep_df(fld, "earliest_fld_date", "Filed")
    ntfld = prep_df(ntfld, "earliest_ntfld_date", "Not Filed")
    disp = prep_df(disp, "earliest_disp_date", "Disposed")

    # List of DFs
    dfs = [rcvd, fld, ntfld, disp]

    # Concatenate DFs (should be 2016 - 2025 YTD)
    df = pd.concat(dfs, ignore_index=True)

    # Final cleaning
    df["Case Status"] = pd.Categorical(df["Case Status"], categories=["Received", "Filed", "Not Filed", "Disposed"], ordered=True)
    df["Year"] = ["2025 YTD" if year == 2025 else str(year) for year in df["Year"]]

    return df

# Bar Chart of Processed Cases by Year
cases_by_year = st.container()

with cases_by_year:
    # st.dataframe(total_by_year(RCVD, FLD, NTFLD, DISP))
    # st.bar_chart(total_by_year(RCVD, FLD, NTFLD, DISP), x="Year", y="Total Cases", color="Case Status", stack=False)

    order = ["Received", "Filed", "Not Filed", "Disposed"]

    chart = (
        alt.Chart(total_by_year(RCVD, FLD, NTFLD, DISP))
        .mark_bar()
        .encode(
            x="Year:O",
            y=alt.Y("Total Cases:Q", title="Case Volume"),
            color=alt.Color("Case Status:N", sort=order),  # 👈 enforce order
            xOffset=alt.XOffset("Case Status:N", sort=order)
        )
        .properties(
            title={
                "text": "Cases Processed by Year and Status",
                "anchor": "middle",
                "fontSize": 24,
                "fontWeight": "bold"
            }
        )
    )

    st.altair_chart(chart, use_container_width=True)


# Most Common Charge Categories by Year 

# Cases by Referring Agency and Category 

def total_by_agency(rcvd: pd.DataFrame, fld: pd.DataFrame, ntfld: pd.DataFrame, disp: pd.DataFrame) -> pd.DataFrame:

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    def prep_df(df: pd.DataFrame, date_col: str, status: str) -> pd.DataFrame:

        # Prepare DF for groupby
        df[date_col] = pd.to_datetime(df[date_col])
        df["Year"] = df[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
        df["Month"] = df[date_col].dt.month

        # Group by
        df = df.groupby(["Year", "agency_name"])["pbk_num"].count().reset_index()
        df.rename(columns={"pbk_num": "Total Cases"}, inplace=True)

        df["Case Status"] = status

        return df

    # Create list of DFs 
    rcvd = prep_df(rcvd, "ref_date", "Received")
    fld = prep_df(fld, "earliest_fld_date", "Filed")
    ntfld = prep_df(ntfld, "earliest_ntfld_date", "Not Filed")
    disp = prep_df(disp, "earliest_disp_date", "Disposed")

    # List of DFs
    dfs = [rcvd, fld, ntfld, disp]

    # Concatenate DFs (should be 2016 - 2025 YTD)
    df = pd.concat(dfs, ignore_index=True)

    # Final cleaning
    df["Case Status"] = pd.Categorical(df["Case Status"], categories=["Received", "Filed", "Not Filed", "Disposed"], ordered=True)
    df["Year"] = ["2025 YTD" if year == 2025 else str(year) for year in df["Year"]]

    df = df[df["Year"]=="2025 YTD"]

    return df

# Bar Chart of Processed Cases by Referring Agency
cases_by_agency = st.container()

with cases_by_agency:
    # st.dataframe(total_by_agency(RCVD, FLD, NTFLD, DISP))
    # st.bar_chart(total_by_agency(RCVD, FLD, NTFLD, DISP), x="agency_name", y="Total Cases", color="Case Status", stack=False)

    order = ["Received", "Filed", "Not Filed", "Disposed"]

    chart = (
        alt.Chart(total_by_agency(RCVD, FLD, NTFLD, DISP))
        .mark_bar()
        .encode(
            x=alt.X("agency_name:O", title="Police Agency"),
            y=alt.Y("Total Cases:Q", title="Case Volume"),
            color=alt.Color("Case Status:N", sort=order),  # 👈 enforce order
            xOffset=alt.XOffset("Case Status:N", sort=order)
        )
        .properties(
            title={
                "text": "Cases Processed by Referring Police Agency and Status",
                "anchor": "middle",
                "fontSize": 24,
                "fontWeight": "bold"
            }
        )
    )

    st.altair_chart(chart, use_container_width=True)

    test_df = total_by_agency(RCVD, FLD, NTFLD, DISP)

    # Sort by Year ascending, then Case Status descending
    sorted_df = test_df.sort_values(by=["Case Status", "Total Cases"], ascending=[True, False])
    # cols = st.columns(4)
    # with cols[0]:
    #     st.write(sorted_df[sorted_df['Case Status']=="Received"]['agency_name'].tolist())
    # with cols[1]:
    #     st.write(sorted_df[sorted_df['Case Status']=="Filed"]['agency_name'].tolist())
    # with cols[2]:
    #     st.write(sorted_df[sorted_df['Case Status']=="Not Filed"]['agency_name'].tolist())
    # with cols[3]:
    #     st.write(sorted_df[sorted_df['Case Status']=="Disposed"]['agency_name'].tolist())