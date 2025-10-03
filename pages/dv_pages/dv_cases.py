import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt


from read_data import RCVD, FLD, NTFLD, DISP

# --- Streamlit page title ---

st.markdown("<h1 style='text-align: center;'>Prosecuting Domestic Assault Cases</h1>", unsafe_allow_html=True)

with st.expander("Domestic Assault Cases - Data Notes", expanded=False, icon="📝"):
    notes_text = Path("assets/text/dv_pages/dv_assaults.txt").read_text(encoding="utf-8")
    st.markdown(notes_text)

st.divider()


# Total Rcvd / Fld / Ntfld / Disp YTD <For 'dv'==TRUE>

def dv_ytd(df: pd.DataFrame, date_col: str, metric_label: str, chart_type: str, delta_color: str = "normal", show_metric: bool = True):

    # Filter DV for only those with DV assaults
    df = df[df['dv']]

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
            delta_color=delta_color,
            height=185, # "content" / "stretch" / int 
            # width="content",
            chart_data=sparkline_data,
            chart_type=chart_type,
            border=True
        )
    # else:
    #     st.write(f"Compare with: *{last_total} ({current_year - 1} YTD)*")

# YTD Metrics

st.markdown("<h4 style='text-align: center;'>Domestic Assault Cases Processed Year-to-Date</h4>", unsafe_allow_html=True)
st.write(" ")
ytd_dv_metrics = st.container(horizontal=True)
st.write(" ")

with ytd_dv_metrics:

    rcvd_dv_ytd, fld_dv_ytd, ntfld_dv_ytd, disp_dv_ytd = st.columns(4)

    with rcvd_dv_ytd:
        dv_ytd(RCVD, "ref_date", "***Total Received (YTD)***", "area")
    
    with fld_dv_ytd:
        dv_ytd(FLD, "earliest_fld_date", "***Total Filed (YTD)***", "area")

    with ntfld_dv_ytd:
        dv_ytd(NTFLD, "earliest_ntfld_date", "***Total Not Filed (YTD)***", "area", "inverse")
    
    with disp_dv_ytd:
        dv_ytd(DISP, "earliest_disp_date", "***Total Disposed (YTD)***", "area")
    

def filter_dv(df: pd.DataFrame):
    df = df[df['dv']]

# Grouped cumulative time series for processed cases over time 

def dv_timeseries(df: pd.DataFrame, date_col: str):

    # Filter DV for only those with DV assaults
    df = df[df['dv']]

    # Prepare DF for groupby
    df[date_col] = pd.to_datetime(df[date_col]) # Convert date col to datetime
    df["year"] = df[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    df["month"] = df[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    # Count processed cases per day 
    # daily_counts = df.groupby(date_col).size().reset_index(name='daily_cases')
    daily_counts = df.groupby(["year", date_col]).size().reset_index(name='daily_cases')

    all_years = df['year'].unique()
    # case_types = df['case_type'].unique()

    # Create full date range per year
    full_index = []
    for y in all_years:
        year_dates = pd.date_range(start=f'{y}-01-01', end=f'{y}-12-31')
        # for ct in case_types:
        for d in year_dates:
            full_index.append((y, d)) #,ct

    full_index = pd.MultiIndex.from_tuples(full_index, names=['year', date_col])

    daily_counts = daily_counts.set_index(['year', date_col]).reindex(full_index, fill_value=0).reset_index()

    daily_counts['cumulative_cases'] = daily_counts.groupby('year')['daily_cases'].cumsum()



    # # Calculate cumsum
    # daily_counts['cumulative_cases'] = daily_counts['daily_cases'].cumsum()

    # # Fill in empty (missing) dates
    # all_dates = pd.date_range(df[date_col].min(), df[date_col].max())
    # daily_counts = daily_counts.set_index(date_col).reindex(all_dates, fill_value=0).rename_axis(date_col).reset_index()
    # daily_counts['cumulative_cases'] = daily_counts['daily_cases'].cumsum()

    #
    st.write(daily_counts)

dv_timeseries(RCVD, "ref_date")
dv_timeseries(FLD, "earliest_fld_date")
dv_timeseries(NTFLD, "earliest_ntfld_date")
dv_timeseries(DISP, "earliest_disp_date")


st.title("Cumulative Cases by Type and Year")

chart = alt.Chart(daily_counts).mark_line(point=True).encode(
    x='processed_date:T',
    y='cumulative_cases:Q',
    color='case_type:N',
    tooltip=['processed_date:T','year:N','case_type:N','cumulative_cases:Q']
).interactive()

st.altair_chart(chart, use_container_width=True)
