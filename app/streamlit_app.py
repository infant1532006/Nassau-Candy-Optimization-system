import os
import sys
import base64
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import load_audit_data
from src.optimization import summarize_opportunities
from src.recommendation_engine import (generate_geographic_opportunities,classify_opportunities,select_best_geographic_alternative,)
from src.factory_rules import (get_expected_factory,PRODUCT_FACTORY_MAPPING,)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PROJECT_ROOT = Path(__file__).resolve().parent.parent


st.set_page_config(
    page_title="Nassau Candy Optimization",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded",)

st.markdown(
    """
    <style>
    /* ========================================
       1. MAIN DASHBOARD SPACING
    ======================================== */
    .block-container {
        max-width: 100% !important;
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 2rem !important;}

    /* ========================================
       2. SIDEBAR BACKGROUND
    ======================================== */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #EAE4D8;}

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
        padding-bottom: 1rem;}

    /* ========================================
       3. SIDEBAR BRAND
    ======================================== */
    
.sidebar-brand {
    text-align: center;
    padding: 4px 6px 12px;
    border-bottom: 1px solid #EEE8DC;
    margin-bottom: 22px;}
.sidebar-brand-logo {
    display: block;
    width: 210px;
    max-width: 100%;
    height: auto;
    margin: 0 auto 4px;
    object-fit: contain;
}
.sidebar-brand-label {
    color: #A17A2D;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    margin-bottom: 6px;
}

.sidebar-brand-title {
    color: #252536;
    font-size: 20px;
    font-weight: 750;
    line-height: 1.3;
    margin-bottom: 5px;
}

.sidebar-brand-subtitle {
    color: #667085;
    font-size: 11px;
    line-height: 1.5;
}


    /* ========================================
       4. COMPACT HTML NAVIGATION LINKS
    ======================================== */
    [data-testid="stSidebar"] a[href^="#"] {
        display: block;
        color: #252536 !important;
        text-decoration: none !important;
        background: #FFFFFF;
        border-radius: 9px;
        padding: 5px 12px !important;
        margin: 0 !important;
        line-height: 1.3;
        font-size: 14px;
        font-weight: 500;
        transition: background 0.2s ease;
    }

    /* Navigation hover effect */
    [data-testid="stSidebar"] a[href^="#"]:hover {
        background: #F7F0E1 !important;
        color: #785719 !important;
        text-decoration: none !important;
    }

    /* ========================================
       5. STREAMLIT RADIO NAVIGATION
       Applies if st.sidebar.radio is used
    ======================================== */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        gap: 3px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 9px;
        padding: 6px 10px !important;
        margin: 0 !important;
        line-height: 1.3;
        transition: background 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #F8F3E9 !important;
    }

    /* Gold indicator for selected radio option */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #F7F0E1 !important;
        border-left: 4px solid #B48A3C !important;
        color: #785719 !important;
        font-weight: 700 !important;
    }

    /* ========================================
       6. FEASIBILITY STATUS CARD
    ======================================== */
    .feasibility-card {
        background: #FBF8F1;
        border: 1px solid #E8D9B7;
        border-radius: 12px;
        padding: 15px 13px;
        margin-top: 24px;
    }

    .feasibility-title {
        color: #785719;
        font-size: 13px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .feasibility-badge {
        display: inline-block;
        color: #785719;
        background: #F0E2C3;
        border-radius: 20px;
        padding: 4px 9px;
        font-size: 10px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .feasibility-description {
        color: #69665E;
        font-size: 11px;
        line-height: 1.6;
        margin: 0;
    }

    /* Selected sidebar navigation link */
[data-testid="stSidebar"] a[href^="#"].active-nav {
    background: #F7F0E1 !important;
    border-left: 4px solid #B48A3C !important;
    color: #785719 !important;
    font-weight: 700 !important;
    text-decoration: none !important;
}


/* Compact sidebar navigation */
.sidebar-navigation {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.sidebar-navigation .nav-link {
    display: block;
    box-sizing: border-box;
    width: 100%;
    padding: 7px 10px;
    margin: 0;
    border-radius: 8px;
    border-left: 4px solid transparent;
    background: #FFFFFF;
    color: #252536 !important;
    text-decoration: none !important;
    font-size: 14px;
    line-height: 1.3;
    font-weight: 500;
    transition: background 0.2s ease;
}

.sidebar-navigation .nav-link:hover {
    background: #F8F3E9;
    color: #785719 !important;
}

/* Selected navigation option */
.sidebar-navigation .nav-link.active-nav {
    background: #F7F0E1 !important;
    border-left-color: #B48A3C !important;
    color: #785719 !important;
    font-weight: 700 !important;
}
/* ML Prediction navigation button */
[data-testid="stSidebar"] div[data-testid="stButton"] {
    width: 100%;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    width: 100%;
    min-height: 0;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    text-align: left;
    background: #FFFFFF !important;
    color: #252536 !important;
    border: none !important;
    border-left: 4px solid transparent !important;
    border-radius: 8px;
    padding: 7px 10px !important;
    margin: 0 !important;
    font-size: 14px;
    font-weight: 500;
    box-shadow: none !important;
}

[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: #F8F3E9 !important;
    color: #785719 !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)

logo_path = PROJECT_ROOT / "assets" / "nassau_candy_logo.png"

if logo_path.exists():
    with open(logo_path, "rb") as logo_file:
        logo_base64 = base64.b64encode(logo_file.read()).decode("utf-8")

    st.markdown(
        f"""
       <div style="
    width: 100%;
    text-align: center;
    padding:0;
    margin: 0;
">
            <img
                src="data:image/png;base64,{logo_base64}"
                style="width: 400px; max-width: 90%; height: auto; object-fit: contain; display: block; margin: 0 auto;"
            />
        </div>
        """,
        unsafe_allow_html=True,)

st.markdown(
    """
    <div style="text-align: center; margin: 0 0 20px 0;">
        <h1 style="
            font-size: 36px;
            font-weight: 700;
            color: #252536;
            margin: 8px 0 10px 0;
        ">
            Nassau Candy Factory Optimization
        </h1>
        <p style="
            font-size: 16px;
            color: #667085;
            margin: 0;
        ">
            Geographic analysis and factory feasibility screening
        </p>
    </div>
    """,
    unsafe_allow_html=True,)
st.warning(
    "Geographic distance is only a screening measure. "
    "Factory changes require feasibility review. "
    "Distance reductions do not guarantee lower costs "
    "or faster deliveries.")

# Sidebar brand
st.sidebar.markdown(
    f"""
    <div class="sidebar-brand">
        <img
            src="data:image/png;base64,{logo_base64}"
            class="sidebar-brand-logo"
            alt="Nassau Candy"
        />
        <div class="sidebar-brand-label">
            FACTORY INTELLIGENCE
        </div>
        <div class="sidebar-brand-title">
            Optimization Suite
        </div>
        <div class="sidebar-brand-subtitle">
            Geographic Analysis &amp; Feasibility
        </div>
    </div>

    <div class="sidebar-section-label">
        WORKSPACE NAVIGATION
    </div>
    """,
    unsafe_allow_html=True,)

# Interactive sidebar navigation
navigation_items = {
    "📊  Dashboard Overview": "dashboard-overview",
    "🛡️  Opportunity Classification": "opportunity-classification",
    "📍  Geographic Opportunity Summary": "geographic-opportunity-summary",
    "🔎  Explore Opportunities": "explore-opportunities",
    "🧠  ML Prediction": "ml-prediction",
}

# Sidebar navigation links
# Sidebar navigation links
st.sidebar.markdown(
    """
    <div class="sidebar-navigation">
        <a class="nav-link" href="?page=dashboard#dashboard-overview" target="_self">
            📊 Dashboard Overview
        </a>
        <a class="nav-link" href="?page=dashboard#opportunity-classification" target="_self">
            🛡️ Opportunity Classification
        </a>
        <a class="nav-link" href="?page=dashboard#geographic-opportunity-summary" target="_self">
            📍 Geographic Opportunity Summary
        </a>
        <a class="nav-link" href="?page=dashboard#explore-opportunities" target="_self">
            🔎 Explore Opportunities
        </a>
        <a class="nav-link" href="?page=ml_prediction" target="_self">
            🧠 ML Prediction
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)


# Sidebar feasibility status panel
st.sidebar.markdown(
    """
    <div class="feasibility-card">
        <div class="feasibility-title">
            🏭 Factory Feasibility
        </div>
        <div class="feasibility-badge">
            REVIEW REQUIRED
        </div>
        <p class="feasibility-description">
            Geographic alternatives are screening candidates only.
            Validate product rules, production capacity, costs and
            logistics before approving any factory change.
        </p>
    </div>
    """,
    unsafe_allow_html=True,)


st.markdown(
    f"""
    <script>
    </script>
    """,
    unsafe_allow_html=True,)

st.sidebar.markdown("---")

# ML Prediction page routing
if st.query_params.get("page") == "ml_prediction":
    from ml_prediction import render_ml_prediction

    render_ml_prediction()
    st.stop()

@st.cache_data
def load_analysis():
    audit_data = load_audit_data()
    opportunities = generate_geographic_opportunities(audit_data)
    best_alternatives = select_best_geographic_alternative(
        opportunities)
    summary = summarize_opportunities(opportunities)
    classified = classify_opportunities(opportunities)

    return (
        audit_data,
        opportunities,
        best_alternatives,
        summary,
        classified,)

try:
    with st.spinner("Analyzing the dataset..."):
        (audit_data,
    opportunities,
    best_alternatives,
    summary,
    classified,) = load_analysis()

    st.markdown(
        """
        <style>
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e8e9f0;
            border-radius: 16px;
            padding: 22px 20px;
            min-height: 125px;
            box-shadow: 0 4px 14px rgba(31, 41, 55, 0.05);
        }
        .kpi-label {
            color: #667085;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 12px;}

        .kpi-value {
            color: #252536;
            font-size: 30px;
            font-weight: 750;
            line-height: 1.2;}

        .kpi-note {
            color: #8a8fa3;
            font-size: 12px;
            margin-top: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.header("Dashboard Overview", anchor="dashboard-overview")
    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Dataset Records</div>
                <div class="kpi-value">{len(audit_data):,}</div>
                <div class="kpi-note">Records analyzed</div>
            </div>
            """,
            unsafe_allow_html=True,)

    with kpi2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Geographic Opportunities</div>
                <div class="kpi-value">{len(opportunities):,}</div>
                <div class="kpi-note">Potential distance reductions</div>
            </div>
            """,
            unsafe_allow_html=True,)

    with kpi3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Summary Combinations</div>
                <div class="kpi-value">{len(summary):,}</div>
                <div class="kpi-note">Product and factory combinations</div>
            </div>
            """,
            unsafe_allow_html=True,)

    st.markdown("### Opportunity Classification")

    kpi4, kpi5 = st.columns(2)

    with kpi4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Mapping-Compatible</div>
                <div class="kpi-value">{len(classified['mapping_compatible']):,}</div>
                <div class="kpi-note">Matches the current product-factory rules</div>
            </div>
            """,
            unsafe_allow_html=True,)

    with kpi5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Requires Feasibility Review</div>
                <div class="kpi-value">{len(classified['requires_review']):,}</div>
                <div class="kpi-note">Not approved for reassignment</div>
            </div>
            """,
            unsafe_allow_html=True,)
    # Geographic Coverage Analysis
    total_records = len(audit_data)
    records_with_closer_alternative = opportunities["Row ID"].nunique()
    records_without_closer_alternative = max(
        0, total_records - records_with_closer_alternative)

    st.subheader("Geographic Coverage Analysis")
    st.caption(
        "Records with at least one geographically closer alternative "
        "versus records without one.")
    
    coverage_col1, coverage_col2, coverage_col3 = st.columns(3)

    with coverage_col1:
        st.metric(
            "Total Records",
            f"{total_records:,}",)

    with coverage_col2:
        closer_percentage = (
            records_with_closer_alternative / total_records * 100
            if total_records > 0 else 0)
        st.metric(
            "Records with Closer Alternative",
            f"{records_with_closer_alternative:,}",
            delta=None,)
        st.caption(f"{closer_percentage:.2f}% of records")

    with coverage_col3:
        no_closer_percentage = (
            records_without_closer_alternative / total_records * 100
            if total_records > 0 else 0)
        st.metric(
            "Records without Closer Alternative",
            f"{records_without_closer_alternative:,}",
            delta=None,)
        st.caption(f"{no_closer_percentage:.2f}% of records")


    coverage_data = pd.DataFrame(
        {
            "Category": [
                "At least one closer alternative",
                "No closer alternative",
            ],
            "Records": [
                records_with_closer_alternative,
                records_without_closer_alternative,]})

    coverage_fig = px.pie(
        coverage_data,
        names="Category",
        values="Records",
        hole=0.72,
        color="Category",
        color_discrete_map={
            "At least one closer alternative": "#B48A3C",
            "No closer alternative": "#E5E5E5",
        },
    )

    total_records = coverage_data["Records"].sum()
    closer_records = coverage_data.loc[
        coverage_data["Category"] == "At least one closer alternative",
        "Records",].sum()

    coverage_percentage = (
        closer_records / total_records * 100
        if total_records > 0
        else 0)

    coverage_fig.update_traces(
        textinfo="percent",
        textposition="inside",
        insidetextorientation="horizontal",
        marker_line_color="#FFFFFF",
        marker_line_width=3,
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Records: %{value:,}<br>"
            "Share: %{percent}<extra></extra>"),)

    coverage_fig.update_layout(
        template="plotly_white",
        height=280,
        showlegend=True,
        legend_title_text="",
        font={"family": "Arial, sans-serif", "color": "#252536"},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin={"l": 10, "r": 10, "t": 15, "b": 15},
        annotations=[
            {
                "text": f"<b>{coverage_percentage:.1f}%</b><br>"
                        "<span style='font-size:11px'>With alternatives</span>",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 22, "color": "#252536"},
            }
        ],
    )

    
    coverage_col1, coverage_col2 = st.columns(2, gap="medium")

    with coverage_col1:
        with st.container(border=True):
            st.subheader("Opportunity Coverage")
            st.plotly_chart(
                coverage_fig,
                use_container_width=True,
                config={"displayModeBar": False},)
    with coverage_col2:
        with st.container(border=True):
            st.subheader("Opportunity Insights")

            total_records = coverage_data["Records"].sum()

            closer_records = coverage_data.loc[
                coverage_data["Category"]
                == "At least one closer alternative",
                "Records",].sum()

            no_closer_records = coverage_data.loc[
                coverage_data["Category"]
                == "No closer alternative",
                "Records",].sum()

            closer_pct = (
                closer_records / total_records * 100
                if total_records > 0 else 0)

            no_closer_pct = (
                no_closer_records / total_records * 100
                if total_records > 0 else 0)

        st.caption("KEY FINDING")
        st.markdown(f"#### {closer_pct:.1f}% have a closer alternative")

        st.markdown(
            f"🟡 **{closer_records:,.0f}** with closer alternatives")
        st.markdown(
            f"⚪ **{no_closer_records:,.0f}** without closer alternatives")

        st.caption(
            "Validate capacity, costs and logistics before relocation.")

    st.subheader("Geographic Opportunity Summary") 
    factory_chart_data = (
        summary.groupby("Alternative Factory", as_index=False)
        .agg(
            Average_Distance_Saved_km=(
                "Avg_Distance_Saved_km",
                "mean",))
        .sort_values(
            "Average_Distance_Saved_km",
            ascending=False,))

    chart_col1, chart_col2 = st.columns(2, gap="medium")

    with chart_col1:
        st.subheader("Average Distance Saved")

        fig = px.bar(
            factory_chart_data,
            x="Average_Distance_Saved_km",
            y="Alternative Factory",
            title="Distance Saved by Factory",
            labels={
                "Alternative Factory": "Alternative Factory",
                "Average_Distance_Saved_km": "Distance Saved (km)",
            },
            color_discrete_sequence=["#B48A3C"],)

        fig.update_layout(
            template="plotly_white",
            height=350,
            title={
                "x": 0.02,
                "xanchor": "left",
                "font": {"size": 17, "color": "#252536"},
            },
            font={"family": "Arial, sans-serif", "color": "#252536"},
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin={"l": 10, "r": 10, "t": 55, "b": 35},
            xaxis={
                "title": "Distance Saved (km)",
                "gridcolor": "#E5E5EF",
                "zeroline": False,
            },
            yaxis={
                "title": "",
                "showgrid": False,
                "tickfont": {"size": 10},
            },
            xaxis_range=[0,factory_chart_data["Average_Distance_Saved_km"].max() * 1.18,],
            uniformtext_minsize=10,)

        fig.update_traces(
            marker_line_color="#8E6B2D",
            marker_line_width=0.7,
            text=factory_chart_data[
                "Average_Distance_Saved_km"
            ].map(lambda value: f"{value:,.0f} km"),
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Average distance saved: %{x:,.2f} km"
                "<extra></extra>"
            ),)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},)

    with chart_col2:
        st.subheader("Average Percentage Saved")

        percentage_chart_data = (
            summary.groupby("Alternative Factory", as_index=False)
            .agg(
                Average_Percentage_Saved=(
                    "Avg_Distance_Saved_pct",
                    "mean",
                )
            )
            .sort_values(
                "Average_Percentage_Saved",
                ascending=False,
            )
        )

        percentage_fig = px.scatter(
            percentage_chart_data,
            x="Average_Percentage_Saved",
            y="Alternative Factory",
            title="Percentage Reduction by Factory",
            labels={
                "Alternative Factory": "Alternative Factory",
                "Average_Percentage_Saved": "Distance Saved (%)",
            },
            color_discrete_sequence=["#B48A3C"],)

        percentage_fig.update_layout(
            template="plotly_white",
            height=350,
            title={
                "x": 0.02,
                "xanchor": "left",
                "font": {"size": 17, "color": "#252536"},
            },
            font={"family": "Arial, sans-serif", "color": "#252536"},
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin={"l": 10, "r": 15, "t": 55, "b": 35},
            xaxis={
                "title": "Distance Saved (%)",
                "ticksuffix": "%",
                "gridcolor": "#E5E5EF",
                "zeroline": False,
            },
            yaxis={
                "title": "",
                "showgrid": False,
                "tickfont": {"size": 10},
                "categoryorder": "total ascending",
            },
        )

        percentage_fig.update_traces(
            marker={
                "size": 13,
                "color": "#B48A3C",
                "line": {"color": "#8E6B2D", "width": 1.5},
            },
            mode="markers+text",
            texttemplate="%{x:.1f}%",
            textposition="middle right",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Average percentage saved: %{x:.2f}%"
                "<extra></extra>"
            ),)

        percentage_fig.update_xaxes(
            showgrid=True,
            gridcolor="#EAE1CF",
            gridwidth=1,
            ticksuffix="%",)

        percentage_fig.update_yaxes(showgrid=False)

        st.plotly_chart(
            percentage_fig,
            use_container_width=True,
            config={"displayModeBar": False},)

    st.caption(
            "Ranked by average straight-line distance reduction; "
            "these are not approved factory reassignment decisions.")
    display_summary = summary.rename(
    columns={
        "Product Name": "Product",
        "Current Factory": "Current Factory",
        "Alternative Factory": "Alternative Factory",
        "Mapping Compatible": "Mapping Compatible",
        "Records": "Records",
        "Avg_Distance_Saved_km": "Avg. Distance Saved (km)",
        "Avg_Distance_Saved_pct": "Avg. Distance Saved (%)",
    })

    st.dataframe(
    display_summary,
    use_container_width=True,
    hide_index=True,)

    st.markdown(
    """
    <div style="margin-top: 12px; margin-bottom: 18px;">
        <h2 style="color: #252536; margin-bottom: 4px;">
            Data Quality Overview
        </h2>
        <p style="color: #74748A; font-size: 14px; margin-top: 0;">
            Dataset completeness, duplicate detection, and factory
            assignment validation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,)

    missing_opportunity_values = opportunities.isna().sum().sum()
    missing_audit_values = audit_data.isna().sum().sum()
    complete_audit_records = audit_data.notna().all(axis=1).sum()

    audit_record_completeness = (
    complete_audit_records / len(audit_data) * 100
    if len(audit_data) > 0
    else 0
    )
    duplicate_audit_rows = audit_data.duplicated().sum()
    expected_factories = audit_data["Product Name"].map(
        get_expected_factory)

    factory_mismatches = (
        audit_data["Current Factory"] != expected_factories).sum()

    valid_products = set(PRODUCT_FACTORY_MAPPING.keys())
    valid_factories = set(PRODUCT_FACTORY_MAPPING.values())

    invalid_product_records = (
        ~audit_data["Product Name"].isin(valid_products)).sum()

    invalid_factory_records = (
        ~audit_data["Current Factory"].isin(valid_factories)).sum()

    quality_checks = [
        missing_opportunity_values == 0,
        missing_audit_values == 0,
        duplicate_audit_rows == 0,
        factory_mismatches == 0,]

    quality_score = (
        sum(quality_checks) / len(quality_checks) * 100)

   
    # Display data quality metrics in a consistent grid
    st.markdown(
        """
        <style>
        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #EAE4D8;
            border-radius: 12px;
            padding: 16px 18px;
            min-height: 112px;
            box-shadow: 0 2px 8px rgba(37, 37, 54, 0.04);}

        [data-testid="stMetricLabel"] {
            color: #667085;
            font-size: 13px;
            font-weight: 500;}

        [data-testid="stMetricValue"] {
            color: #252536;
            font-size: 27px;
            font-weight: 700;}
        </style>
        """,
        unsafe_allow_html=True,)

    quality_metrics = [
        ("Missing Opportunity Cells", f"{missing_opportunity_values:,}"),
        ("Missing Audit Cells", f"{missing_audit_values:,}"),
        ("Duplicate Audit Records", f"{duplicate_audit_rows:,}"),
        ("Factory Mapping Mismatches", f"{factory_mismatches:,}"),
        ("Complete Audit Records", f"{audit_record_completeness:.2f}%"),
        ("Invalid Products", f"{invalid_product_records:,}"),
        ("Invalid Factories", f"{invalid_factory_records:,}"),]

    quality_row1 = st.columns(4, gap="medium")
    quality_row2 = st.columns(3, gap="medium")

    for column, (label, value) in zip(quality_row1, quality_metrics[:4]):
        with column:
            st.metric(label, value)

    for column, (label, value) in zip(quality_row2, quality_metrics[4:]):
        with column:
            st.metric(label, value)



    st.caption(
        "These counts represent missing cells across each complete dataset, "
        "not the number of affected records.")
    st.subheader("Explore Opportunities")

    if (
        missing_audit_values == 0
        and duplicate_audit_rows == 0
        and factory_mismatches == 0):

        st.progress(
        quality_score / 100,
        text=f"Data Quality Check Pass Rate: {quality_score:.0f}%",)
        st.success(
            "Data checks passed: no missing audit values, "
            "duplicate rows, or factory assignment mismatches detected.")
    else:
        st.warning(
            "Data quality issues detected. Review the metrics above.")

        st.subheader("Best Geographic Alternatives")
    st.caption(
        "One geographically closest alternative per record, "
        "ranked by straight-line distance reduction.")

    st.warning(
        "These are screening candidates, not approved factory "
        "changes. All alternatives require feasibility review.")

    if best_alternatives.empty:
        st.info("No geographic alternatives are available.")
    else:
        best_display = best_alternatives.rename(
            columns={
                "Row ID": "Record ID",
                "Product Name": "Product",
                "Current Factory": "Current Factory",
                "Alternative Factory": "Best Geographic Alternative",
                "distance_saved_km": "Distance Saved (km)",
                "distance_saved_percent": "Distance Saved (%)",
                "Mapping Compatible": "Mapping Compatible",})

        st.metric(
            "Records with a Closer Alternative",
            f"{len(best_display):,}",)

        st.dataframe(
            best_display[
                [
                    "Record ID",
                    "Product",
                    "Current Factory",
                    "Best Geographic Alternative",
                    "Distance Saved (km)",
                    "Distance Saved (%)",
                    "Mapping Compatible",]],
            width="stretch",
            hide_index=True,)
        col1, col2 = st.columns(2)

    current_factories = sorted(
        opportunities["Current Factory"].dropna().unique())
    selected_factory = col1.selectbox(
        "Select current factory",
        current_factories,)

    factory_opportunities = opportunities[
        opportunities["Current Factory"] == selected_factory]

    product_names = sorted(
        factory_opportunities["Product Name"].dropna().unique())

    selected_product = st.selectbox(
        "Select product",
        ["All products"] + product_names,
        key="product_filter",
    )

    if selected_product != "All products":
        factory_opportunities = factory_opportunities[
            factory_opportunities["Product Name"] == selected_product]

    alternative_factories = sorted(
        factory_opportunities["Alternative Factory"].dropna().unique())

    selected_alternative = col2.selectbox(
        "Select alternative factory",
        ["All alternatives"] + alternative_factories,)

    if selected_alternative != "All alternatives":
        factory_opportunities = factory_opportunities[
            factory_opportunities["Alternative Factory"]
            == selected_alternative
        ]
    
    minimum_distance_saved = st.slider(
        "Minimum straight-line distance saved (km)",
        min_value=0.0,
        max_value=5000.0,
        value=0.0,
        step=10.0,)
    factory_opportunities = factory_opportunities[
        factory_opportunities["distance_saved_km"]
        >= minimum_distance_saved]


    st.write(
        f"Showing {len(factory_opportunities):,} geographic opportunities.")

    st.dataframe(
        factory_opportunities,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Row ID": st.column_config.NumberColumn(
                "Record ID", format="%d"),
            "Product Name": st.column_config.TextColumn(
                "Product", width="large"),
            "Current Factory": st.column_config.TextColumn("Current Factory"),
            "Alternative Factory": st.column_config.TextColumn("Alternative Factory"),
            "Expected Factory": st.column_config.TextColumn("Expected Factory"),
            "current_distance_km": st.column_config.NumberColumn("Current Distance (km)", format="%.2f"),
            "alternative_distance_km": st.column_config.NumberColumn("Alternative Distance (km)", format="%.2f"),
            "distance_saved_km": st.column_config.NumberColumn("Distance Saved (km)", format="%.2f"),
            "distance_saved_percent": st.column_config.NumberColumn("Distance Saved (%)", format="%.2f"),
            "is_closer": st.column_config.CheckboxColumn("Closer Alternative"),
            "Mapping Compatible": st.column_config.CheckboxColumn("Mapping Compatible"),
            "Requires Feasibility Review": st.column_config.CheckboxColumn(
                "Requires Review"),},)

    st.download_button(
        "Download Summary CSV",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="nassau_candy_opportunity_summary.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download Filtered Opportunities CSV",
        data=factory_opportunities.to_csv(index=False).encode("utf-8"),
        file_name="nassau_candy_filtered_opportunities.csv",
        mime="text/csv",
    )

except Exception as error:
    st.error("The analysis could not be loaded.")
    st.exception(error)
