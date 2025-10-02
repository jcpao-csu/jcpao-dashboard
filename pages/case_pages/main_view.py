import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

from read_data import query_table
from read_data import RCVD, FLD, NTFLD, DISP

# --- Streamlit page title ---
# st.title("JCPAO Dashboard Overview")
st.markdown("<h1 style='text-align: center;'>JCPAO Dashboard Overview</h1>", unsafe_allow_html=True)
st.divider()
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