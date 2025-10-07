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

def dv_timeseries(df: pd.DataFrame, date_col: str, title_name: str, ):

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
        if y != current_year:
            year_dates = pd.date_range(start=f'{y}-01-01', end=f'{y}-12-31')
        else:
            year_dates = pd.date_range(start=f'{y}-01-01', end=today.strftime("%Y-%m-%d"))
        # for ct in case_types:
        for d in year_dates:
            full_index.append((y, d)) #,ct

    full_index = pd.MultiIndex.from_tuples(full_index, names=['year', date_col])

    daily_counts = daily_counts.set_index(['year', date_col]).reindex(full_index, fill_value=0).reset_index()

    daily_counts['cumulative_cases'] = daily_counts.groupby('year')['daily_cases'].cumsum()
    # daily_counts['month_day'] = pd.to_datetime(df[date_col].dt.strftime(f"{current_year}-%m-%d"))
    
    daily_counts = daily_counts[~((daily_counts[date_col].dt.month == 2) & (daily_counts[date_col].dt.day == 29))] # Drop Feb 29
    daily_counts[date_col] = daily_counts[date_col].apply(lambda x: x.replace(year=current_year))
    daily_counts['is_current'] = daily_counts['year'] == current_year

    # Display altair chart
    # st.title(f"{title_name} Domestic Assault Cases, Cumulative")

    chart = alt.Chart(daily_counts).mark_line().encode(
        x=alt.X(f'{date_col}:T', title=f"{title_name} Date"), 
        y=alt.Y('cumulative_cases:Q', title="Cumulative Case Volume"),
        color='year:N',
        strokeDash=alt.condition(
        alt.datum.is_current,
            alt.value([0]),      # solid line if current year
            alt.value([5,5])     # dashed if not current year
        ),
        size=alt.condition(
            alt.datum.is_current,
            alt.value(3),   # thicker line if current year
            alt.value(1)    # thinner line otherwise
        ),
        tooltip=[
            alt.Tooltip(f'{date_col}:T', title="Date"),
            alt.Tooltip('year:N', title="Year"),
            alt.Tooltip('cumulative_cases:Q', title="Total Cases")
        ] # ,'case_type:N'
    ).interactive()

    # Vertical line
    today_line = alt.Chart(pd.DataFrame({'Today':[today.strftime("%Y-%m-%d")]})).mark_rule(
        color='red',
        # strokeDash=[4,4]  # dashed red line
    ).encode(
        x='Today:T'
    )

    # Text label (offset above the chart line)
    today_text = alt.Chart(pd.DataFrame({
        'month_day':[today.strftime("%Y-%m-%d")],
        'label':["Today"]
    })).mark_text(
        align='left',
        baseline='bottom',
        dx=5,
        dy=-5,
        color='red'
    ).encode(
        x='Today:T',
        y=alt.value(10),   # pin near the x-axis baseline
        text='label'
    )


    st.altair_chart((chart + today_line + today_text), use_container_width=True)



# Not Filed Reasons

def ntfld_reasons(ntfld: pd.DataFrame = NTFLD, date_col: str = "earliest_ntfld_date"):

    # Filter DV for only those with DV assaults
    ntfld = ntfld[ntfld['dv']]

    # Prepare DF for groupby
    ntfld[date_col] = pd.to_datetime(ntfld[date_col]) # Convert date col to datetime
    ntfld["year"] = ntfld[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    ntfld["month"] = ntfld[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    all_years = ntfld['year'].unique()

    # Group by category + year and count rows
    grouped_df = (
        ntfld.groupby(["min_ntfld_category", "year"])
        .size()
        .reset_index(name="count")
    )

    # Add st.segmented_control
    years = sorted(grouped_df["year"].unique())
    # current_year = date.today().year

    selected_year = st.segmented_control(
        "Select Year",
        options=years,
        default=current_year if current_year in years else years[-1],
        key="ntfld_reasons"
    )

    filtered_df = grouped_df[grouped_df["year"] == selected_year]

    # Calculate percentage share
    filtered_df["pct"] = (
        filtered_df["count"] / filtered_df["count"].sum() * 100
    ).round(1)

    # Altair pie chart
    pie_chart = alt.Chart(filtered_df).mark_arc(innerRadius=70, outerRadius=120).encode(
        theta=alt.Theta("count:Q", stack=True, title="Total Not Filed Cases"),
        color=alt.Color("min_ntfld_category:N", legend=alt.Legend(title="Not Filed Reason")),
        tooltip=[
            alt.Tooltip("min_ntfld_category:N", title="Not Filed Reason"), 
            alt.Tooltip("count:Q", title="Total"),
            alt.Tooltip("pct:Q", title="Percent", format=f".1f")
        ]
    ).interactive()

    selection = alt.selection_multi(fields=['min_ntfld_category'], bind='legend')
    pie_chart = pie_chart.add_selection(selection).encode(
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    )

    # # Optional labels
    # text = (
    #     alt.Chart(filtered_df)
    #     .mark_text(radius=80, size=12)
    #     .encode(text=alt.Text("pct:Q", format=".1f"))
    # )

    st.altair_chart(pie_chart, use_container_width=True) # + text


# Disposed Outcomes 

def disp_outcomes(disp: pd.DataFrame = DISP, date_col: str = "earliest_disp_date"):

    # disp_dict
    disp_dict = {
        1: 'Trial (Guilty Verdict)',
        2: 'Guilty Plea',
        3: 'Plea Deal', # essentially a Guilty Plea
        4: 'Diversion',
        5: 'Defendant Deceased',
        6: 'Re-filed',
        7: 'Other Jurisdiction',
        7.5: 'Trial (Not Guilty Verdict)',
        8: 'Self Defense',
        9: 'Statute of Limitations',
        10: 'Lack of Evidence',
        11: 'Other Reason'
    }

    # Filter DV for only those with DV assaults
    disp = disp[disp['dv']]

    # Prepare DF for groupby
    disp[date_col] = pd.to_datetime(disp[date_col]) # Convert date col to datetime
    disp["year"] = disp[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    disp["month"] = disp[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    all_years = disp['year'].unique()

    # Group by category + year and count rows
    grouped_df = (
        disp.groupby(["min_disp_rank", "year"])
        .size()
        .reset_index(name="count")
    )

    grouped_df["min_disp_category"] = grouped_df["min_disp_rank"].map(disp_dict)

    # Add st.segmented_control
    years = sorted(grouped_df["year"].unique())
    # current_year = date.today().year

    selected_year = st.segmented_control(
        "Select Year",
        options=years,
        default=current_year if current_year in years else years[-1],
        key="disp_outcomes"
    )

    filtered_df = grouped_df[grouped_df["year"] == selected_year]

    # Calculate percentage share
    filtered_df["pct"] = (
        filtered_df["count"] / filtered_df["count"].sum() * 100
    ).round(1)

    # Altair pie chart
    pie_chart = alt.Chart(filtered_df).mark_arc(innerRadius=70, outerRadius=120).encode(
        theta=alt.Theta("count:Q", stack=True, title="Total Disposed Cases"),
        color=alt.Color("min_disp_category:N", legend=alt.Legend(title="Disposed Outcome")),
        tooltip=[
            alt.Tooltip("min_disp_category:N", title="Disposed Outcome"), 
            alt.Tooltip("count:Q", title="Total"),
            alt.Tooltip("pct:Q", title="Percent", format=f".1f")
        ]
    ).interactive()

    selection = alt.selection_multi(fields=['min_disp_category'], bind='legend')
    pie_chart = pie_chart.add_selection(selection).encode(
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    )

    st.altair_chart(pie_chart, use_container_width=True) # + text


# File (%) Rate

def file_rate(rcvd: pd.DataFrame = RCVD, fld: pd.DataFrame = FLD, ntfld: pd.DataFrame = NTFLD, disp: pd.DataFrame = DISP, date_col: str = "ref_date"):

    # Filter DV for only those with DV assaults
    rcvd = rcvd.loc[rcvd['dv'], ["pbk_num", "ref_date"]]
    fld_list = fld["pbk_num"].unique().tolist()
    ntfld_list = ntfld["pbk_num"].unique().tolist()
    disp_list = disp["pbk_num"].unique().tolist()

    rcvd["status"] = ["Filed" if case in fld_list else "Not Filed" if case in ntfld_list else "Under Review" for case in rcvd["pbk_num"]]

    # Prepare DF for groupby
    rcvd[date_col] = pd.to_datetime(rcvd[date_col]) # Convert date col to datetime
    rcvd["year"] = rcvd[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    rcvd["month"] = rcvd[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    all_years = rcvd['year'].unique()

    # Group by category + year and count rows
    grouped_df = (
        rcvd.groupby(["status", "year"])
        .size()
        .reset_index(name="count")
    )

    # Add st.segmented_control
    years = sorted(grouped_df["year"].unique())
    # current_year = date.today().year

    selected_year = st.segmented_control(
        "Select Year",
        options=years,
        default=current_year if current_year in years else years[-1],
        key="fld_rate"
    )

    filtered_df = grouped_df[grouped_df["year"] == selected_year]

    # Calculate percentage share
    filtered_df["pct"] = (
        filtered_df["count"] / filtered_df["count"].sum() * 100
    ).round(1)

    # Current file rate 
    fld_cases = filtered_df.loc[filtered_df["status"] == "Filed", "count"].iloc[0]
    ntfld_cases = filtered_df.loc[filtered_df["status"] == "Not Filed", "count"].iloc[0]
    file_rt = (fld_cases / (fld_cases + ntfld_cases) * 100).round(1)
    st.markdown(f":yellow-background[Of the received cases that have completed review, :red[***{file_rt}%***] have been filed.]")

    # Altair pie chart
    pie_chart = alt.Chart(filtered_df).mark_arc(innerRadius=70, outerRadius=120).encode(
        theta=alt.Theta("count:Q", stack=True, title="Total Received Cases"),
        color=alt.Color("status:N", legend=alt.Legend(title="Status of Received Cases")),
        tooltip=[
            alt.Tooltip("status:N", title="Status of Received Cases"), 
            alt.Tooltip("count:Q", title="Total"),
            alt.Tooltip("pct:Q", title="Percent", format=f".1f")
        ]
    ).interactive()

    selection = alt.selection_multi(fields=['status'], bind='legend')
    pie_chart = pie_chart.add_selection(selection).encode(
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    )

    st.altair_chart(pie_chart, use_container_width=True)

# File Lead Charges 
def file_lead_charges(fld: pd.DataFrame = FLD, date_col: str = "earliest_fld_date"):

    # Filter DV for only those with DV assaults
    fld = fld[fld['dv']]

    # Prepare DF for groupby
    fld[date_col] = pd.to_datetime(fld[date_col]) # Convert date col to datetime
    fld["year"] = fld[date_col].dt.year # .dt.to_period("Y") -- convert datetime column to 'period' object / a time interval, rather than a timestamp: 'Y' / 'M' / 'Q' / 'W' / 'D' / 'H'
    fld["month"] = fld[date_col].dt.month

    # Define current period (YTD)
    today = pd.Timestamp.today()
    current_year = today.year

    all_years = fld['year'].unique()

    # Group by category + year and count rows
    grouped_df = (
        fld.groupby(["fld_lead_category", "year"])
        .size()
        .reset_index(name="count")
    )

    # Add st.segmented_control
    years = sorted(grouped_df["year"].unique())
    # current_year = date.today().year

    selected_year = st.segmented_control(
        "Select Year",
        options=years,
        default=current_year if current_year in years else years[-1],
        key="fld_lead_charges"
    )

    filtered_df = grouped_df[grouped_df["year"] == selected_year]

    # Calculate percentage share
    filtered_df["pct"] = (
        filtered_df["count"] / filtered_df["count"].sum() * 100
    ).round(1)

    # Altair pie chart
    pie_chart = alt.Chart(filtered_df).mark_arc(innerRadius=70, outerRadius=120).encode(
        theta=alt.Theta("count:Q", stack=True, title="Total Filed Cases"),
        color=alt.Color("fld_lead_category:N", legend=alt.Legend(title="Lead Charge Code Category")),
        tooltip=[
            alt.Tooltip("fld_lead_category:N", title="Lead Charge Code Category"), 
            alt.Tooltip("count:Q", title="Total"),
            alt.Tooltip("pct:Q", title="Percent", format=f".1f")
        ]
    ).interactive()

    selection = alt.selection_multi(fields=['fld_lead_category'], bind='legend')
    pie_chart = pie_chart.add_selection(selection).encode(
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    )

    st.altair_chart(pie_chart, use_container_width=True)


# --- Display --- 

cols = st.columns(2)

with cols[0]:
    tabs = st.tabs(["Received Cases Status", "Filed Lead Charges", "Not Filed Reasons", "Disposed Outcomes"])
    with tabs[0]:
        st.subheader("Received Cases Status")
        file_rate()
    with tabs[1]:
        st.subheader("Filed Cases' Lead Charge Codes")
        file_lead_charges()
    with tabs[2]:
        st.subheader("Not Filed Case Reasons")
        ntfld_reasons()
    with tabs[3]:
        st.subheader("Disposed Case Outcomes")
        disp_outcomes()

with cols[1]:
    st.subheader("Domestic Assault Cases Rolling Total") # Cumulative Time Series
    tabs = st.tabs(["Received", "Filed", "Not Filed", "Disposed"])
    with tabs[0]:
        dv_timeseries(RCVD, "ref_date", "Received")
    with tabs[1]:
        dv_timeseries(FLD, "earliest_fld_date", "Filed")
    with tabs[2]:
        dv_timeseries(NTFLD, "earliest_ntfld_date", "Not Filed")
    with tabs[3]:
        dv_timeseries(DISP, "earliest_disp_date", "Disposed")