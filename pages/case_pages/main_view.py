import streamlit as st
import pandas as pd
from datetime import datetime

from read_data import query_table
from read_data import RCVD, FLD, NTFLD, DISP

st.title("JCPAO Dashboard Overview")
# st.write("This page is still under construction. Please come back later! 🚧")

with st.sidebar:
    st.title("JCPAO Dashboard Overview")
    st.write("Welcome to the JCPAO Dashboard!")

# # Import rcvd df 
# rcvd = RCVD
# rcvd["ref_monthyr"] = pd.to_datetime(rcvd["ref_date"]).dt.to_period("M")
# monthly_counts = rcvd.groupby("ref_monthyr")["pbk_num"].count().reset_index()
# monthly_counts.rename(columns={"pbk_num": "ref_total"}, inplace=True)

# sparkline_data = monthly_counts["ref_total"].tolist()

# # Delta 
# delta = sparkline_data[-1] - sparkline_data[-13] # (year-to-year change)

# st.metric(
#     label="Total Received Cases",
#     value=sparkline_data[-1],
#     delta=delta,
#     chart_data=sparkline_data,
#     chart_type="bar",
#     border=True
# )

# st.dataframe(rcvd)
# st.write(monthly_counts)

# Total Rcvd / Fld / Ntfld / Disp YTD 

def total_ytd(df: pd.DataFrame, date_col: str, metric_label: str, chart_type: str, show_metric: bool = True):

    # Prepare DF for groupby
    df[date_col] = pd.to_datetime(df[date_col])
    df["year"] = df[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    df["month"] = df[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    # Current year (today's date)
    df_current_ytd = df[(df["year"] == current_year) & (df[date_col] <= today)]

    # Same date previous year
    df_last_ytd = df[(df["year"] == current_year - 1) &
                    (df["month"] < today.month) |
                    ((df["month"] == today.month) & (df[date_col].dt.day <= today.day))]

    # Group by
    annual_count = df.groupby("year")["pbk_num"].count().reset_index()
    annual_count.rename(columns={"pbk_num": "total_cases"}, inplace=True)

    # Sparkline 
    sparkline_data = annual_count["total_cases"].tolist()

    # Delta
    current_total = df_current_ytd["pbk_num"].nunique()
    last_total = df_last_ytd["pbk_num"].nunique()
    delta = current_total - last_total # sparkline_data[-1] - sparkline_data[-2] // year-to-year change)

    if show_metric:
        st.metric(
            label=metric_label,
            value=f"{sparkline_data[-1]} cases",
            delta=f"{delta} YoY", # ({last_total} YTD {current_year - 1})
            # delta_color="off",
            # width="content",
            chart_data=sparkline_data,
            chart_type=chart_type,
            border=True
        )
    # else:
    #     st.write(f"Compare with: *{last_total} ({current_year - 1} YTD)*")

# YTD Metrics
ytd_metrics = st.container(horizontal=True)

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

# # Prior Yr YTD 
# prior_yr = st.container(horizontal=True)

# with prior_yr:
#     rcvd_prior, fld_prior, ntfld_prior, disp_prior = st.columns(4, vertical_alignment="bottom")

#     with rcvd_prior:
#         total_ytd(RCVD, "ref_date", "Total Cases Received (YTD)", "area", False)
    
#     with fld_prior:
#         total_ytd(FLD, "earliest_fld_date", "Total Cases Filed (YTD)", "area", False)

#     with ntfld_prior:
#         total_ytd(NTFLD, "earliest_ntfld_date", "Total Cases Not Filed (YTD)", "area", False)
    
#     with disp_prior:
#         total_ytd(DISP, "earliest_disp_date", "Total Cases Disposed (YTD)", "area", False)
        