import streamlit as st
import joblib
from pathlib import Path
import pandas as pd

# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Saved XGBoost model location
MODEL_PATH = PROJECT_ROOT / "models" / "xgboost_pipeline.joblib"

model = joblib.load(MODEL_PATH)

# Highlight the factory with the lowest predicted lead time
def highlight_best_factory(row):
    if row.name == 0:
        return [
            "background-color: #E8F5E9; color: #1B5E20; font-weight: bold"
        ] * len(row)

    return [""] * len(row)

def render_ml_prediction():

    st.title("ML Prediction & Optimization")

    st.caption(
        "Machine learning-based shipping lead-time prediction "
        "and factory optimization."
    )

    st.divider()

    with st.container(border=True):

        st.subheader("Shipping Lead-Time Prediction")

        st.info(
        "Enter order details to estimate the shipping lead time.")

        st.subheader("Enter Order Details")

    with st.form("prediction_form"):

        ship_mode = st.selectbox(
            "Ship Mode",
            ["Standard Class", "First Class", "Second Class", "Same Day"])

        product_name = st.selectbox(
            "Product Name",
            [
                "Wonka Bar - Milk Chocolate",
                "Wonka Bar - Triple Dazzle Caramel",
                "Wonka Bar - Nutty Crunch Surprise",
                "Wonka Bar -Scrumdiddlyumptious",
                "Wonka Bar - Fudge Mallows",
                "Wonka Gum",
                "Kazookles",
                "Lickable Wallpaper",
                "Fizzy Lifting Drinks",
                "Laffy Taffy",
                "SweeTARTS",
                "Nerds",
                "Hair Toffee",
                "Everlasting Gobstopper",
                "Fun Dip"
            ])

        current_factory = st.selectbox(
            "Current Factory",
            [
                "Wicked Choccy's",
                "Lot's O' Nuts",
                "Secret Factory",
                "The Other Factory",
                "Sugar Shack"
            ])

        units = st.number_input(
            "Units",
            min_value=1,
            max_value=14,
            value=5,
            step=1)

        region = st.selectbox(
            "Region",
            ["Interior", "Atlantic", "Gulf", "Pacific"])

        country = st.selectbox(
            "Country/Region",
            ["United States", "Canada"])

        order_month = st.selectbox(
            "Order Month",
            list(range(1, 13)))

        day_names = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"]

        order_day = st.selectbox(
            "Order Day of Week",
            list(range(7)),
            format_func=lambda day: day_names[day])

        predict_button = st.form_submit_button(
            "Predict Shipping Lead Time")

    # Run prediction only after form submission
    if predict_button:

        input_data = pd.DataFrame([{
            "Ship Mode": ship_mode,
            "Product Name": product_name,
            "Current Factory": current_factory,
            "Units": units,
            "Region": region,
            "Country/Region": country,
            "Order Month": order_month,
            "Order DayOfWeek": order_day}])

        # Compare the same order across all factories
        factories = [
            "Wicked Choccy's",
            "Lot's O' Nuts",
            "Secret Factory",
            "The Other Factory",
            "Sugar Shack"]

        comparison_data = []

        for factory in factories:

            factory_input = input_data.copy()
            factory_input["Current Factory"] = factory

            predicted_days = model.predict(factory_input)[0]

            comparison_data.append({
                "Factory": factory,
                "Predicted Candidate Lead Time (Days)": round(
                    float(predicted_days), 2
                )})

        comparison_df = pd.DataFrame(comparison_data)

        # Sort factories from lowest to highest prediction
        comparison_df = comparison_df.sort_values(
            by="Predicted Candidate Lead Time (Days)"
        ).reset_index(drop=True)

      
                # Factory Performance Comparison Card
        with st.container(border=True):

            st.subheader("Factory Performance Comparison")

            styled_comparison = comparison_df.style.apply(
                highlight_best_factory,
                axis=1
            ).format({
                "Predicted Candidate Lead Time (Days)": "{:.2f}"})

            st.dataframe(
                styled_comparison,
                use_container_width=True,
                hide_index=True)
        
        # Identify current and recommended factories
        best_factory = comparison_df.iloc[0]

        current_factory_result = comparison_df[
            comparison_df["Factory"] == current_factory
        ].iloc[0]

        current_days = float(
            current_factory_result["Predicted Candidate Lead Time (Days)"])

        best_days = float(
            best_factory["Predicted Candidate Lead Time (Days)"])

        # Calculate estimated improvement
        days_saved = current_days - best_days

        if current_days > 0:
            improvement_percentage = (days_saved / current_days) * 100
        else:
            improvement_percentage = 0

        st.divider()
        st.subheader("What-If Scenario Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current Factory",
                current_factory,
                f"{current_days:.2f} candidate days",
                delta_color="inverse")

        with col2:
            st.metric(
                "Recommended Factory",
                best_factory["Factory"],
                f"{best_days:.2f} candidate days",
                delta_color="normal")

        with col3:
            st.metric(
                "Estimated Days Saved",
                f"{days_saved:.2f}",
                f"{improvement_percentage:.2f}% improvement",
                delta_color="normal")


        if days_saved > 0:
            st.success(
                f"Moving from {current_factory} to {best_factory['Factory']} "
                f"could reduce the candidate lead-time estimate by "
                f"{days_saved:.2f} days.")
        elif days_saved == 0:
            st.info(
                "The recommended factory has the same predicted estimate "
                "as the current factory.")
        else:
            st.warning(
                "The selected factory already has a lower predicted estimate "
                "than the recommended factory.")

    #    # Recommendation Dashboard
    st.divider()
    st.subheader("Recommendation Dashboard")

    recommendation_path = (
        PROJECT_ROOT / "data" / "processed" / "final_recommendations.csv")

    if recommendation_path.exists():

        recommendations = pd.read_csv(recommendation_path)

        recommendations = recommendations.sort_values(
            by="Priority Score",
            ascending=False)

        # Recommendation Summary KPIs
        total_recommendations = len(recommendations)

        high_volume_count = (
            recommendations["Evidence Volume"] == "High-volume evidence").sum()

        average_distance_saving = recommendations[
            "Distance Saving (km)"].mean()

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.metric(
                    "Total Recommendations",
                    total_recommendations)

        with col2:
            with st.container(border=True):
                st.metric(
                    "High-Volume Evidence",
                    high_volume_count)

        with col3:
            with st.container(border=True):
                st.metric(
                    "Average Distance Saving",
                    f"{average_distance_saving:,.2f} km")

        st.caption(
            "Ranked factory reassignment opportunities based on "
            "geographic and profitability indicators.")

        display_columns = [
            "Product Name",
            "Current Factory",
            "Alternative Factory",
            "Orders_scenario",
            "Distance Saving (km)",
            "Reduction (%)",
            "Gross Margin (%)",
            "Priority Score",
            "Evidence Volume",
            "Recommendation Status"]

        st.dataframe(
            recommendations[display_columns],
            use_container_width=True,
            hide_index=True)

        # Risk & Impact Panel
        st.divider()
        st.subheader("Risk & Impact Panel")

        low_volume_count = (
            recommendations["Evidence Volume"] == "Low-volume evidence").sum()

        pending_validation_count = (
            recommendations["Manufacturing Compatibility"]
            == "Pending validation").sum()

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.metric(
                    "Low-Volume Recommendations",
                    low_volume_count)

        with col2:
            with st.container(border=True):
                st.metric(
                    "Awaiting Manufacturing Validation",
                    pending_validation_count)

        if low_volume_count > 0:
            st.warning(
                f"{low_volume_count} recommendations have low-volume "
                "evidence. Review them carefully before making decisions.")

        if pending_validation_count > 0:
            st.warning(
                f"{pending_validation_count} recommendations still need "
                "manufacturing compatibility validation.")

        st.info(
            "Profitability is estimated from historical product margins. "
            "Actual profit impact, factory capacity and logistics benefits "
            "must be validated before reassignment.")

    else:
        st.error("Recommendation CSV file was not found.")