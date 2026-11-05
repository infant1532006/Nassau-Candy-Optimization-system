# Nassau Candy Factory Optimization

A Streamlit-based decision-support application for exploring geographic
factory reassignment opportunities and estimating candidate shipping
lead time for Nassau Candy Distributor orders.

> **Important:** This application is an analytical prototype. Geographic
> distance is a screening measure, not proof of lower freight cost or
> faster delivery. Factory changes require operational, manufacturing,
> capacity, and logistics validation.

## Overview

The project analyzes Nassau Candy Distributor order records against five
predefined factory locations. It combines data preprocessing, geographic
distance calculations, factory-product mapping rules, recommendation
screening, and a saved machine-learning pipeline in an interactive
Streamlit application.

The application is designed to help users:

-   Review order and geographic data quality.
-   Identify alternative factories that are geographically closer to an
    order destination.
-   Separate mapping-compatible opportunities from alternatives that
    need additional review.
-   Compare distance savings by product and factory.
-   Explore individual opportunities using interactive filters.
-   Estimate a candidate lead-time proxy for a user-entered order and
    compare the model's estimates across the five factories.
-   Review and download generated opportunity summaries.

This research paper documents the problem background, proposed
methodology, implementation, experiments, and findings of the
Nassau Candy Factory Optimization project.

📄 [Read the Research Paper (PDF)]:https://drive.google.com/file/d/1m00Sv3RUVNzOu8HUbfiGMz_zfZynlr0N/view?usp=drive_link

## Main Features

### 1. Dashboard overview

Presents high-level information from the processed audit dataset,
including geographic opportunity coverage and data-quality indicators.

### 2. Opportunity classification

Separates geographic alternatives into: - **Mapping compatible:** the
alternative factory matches the predefined product-to-factory mapping. -
**Requires review:** the alternative factory does not match that mapping
and needs further feasibility assessment.

A mapping-compatible result is not the same as an approved factory
reassignment.

### 3. Geographic opportunity summary

Summarizes potential straight-line distance savings by product, current
factory, alternative factory, and mapping compatibility.

### 4. Explore opportunities

Allows users to inspect and filter candidate alternatives by: - Current
factory - Product - Alternative factory - Minimum straight-line distance
saved

The dashboard also provides CSV downloads for the opportunity summary
and filtered opportunity records.

### 5. ML prediction and what-if comparison

The ML Prediction page loads the saved pipeline at
`models/xgboost_pipeline.joblib`. Users provide order attributes such as
shipping mode, product, current factory, units, region, country/region,
order month, and order day of week.

The application evaluates the same entered order against each of the
five factories, sorts the resulting candidate lead-time estimates, and
displays a what-if comparison.

These are **model estimates of the project's reconstructed lead-time
target**, not verified delivery-time forecasts.

### 6. Recommendation dashboard

Displays the prepared recommendation records in
`data/processed/final_recommendations.csv`, including priority and
evidence indicators. The supplied recommendation data marks profit
assessment and manufacturing compatibility as pending/estimated
validation; it should not be interpreted as confirmed financial or
operational approval.

## Technology Stack

-   **Language:** Python
-   **Application:** Streamlit
-   **Data processing:** pandas, NumPy
-   **Machine learning:** scikit-learn, XGBoost, joblib
-   **Visualization:** Plotly, Matplotlib, Seaborn
-   **Scientific computing:** SciPy
-   **Notebooks:** Jupyter
-   **Environment and dependency management:** uv

## Repository Structure

``` text
Nassau-Candy-Optimization/
│
├── app/
│   ├── streamlit_app.py          # Main Streamlit dashboard
│   ├── ml_prediction.py          # ML prediction and recommendation page
│   └── pages/
│
├── assets/
│   └── nassau_candy_logo.png
│
├── data/
│   ├── Nassau_Candy_Distributor.csv
│   └── processed/
│       ├── nassau_candy_processed_audit.csv
│       ├── nassau_candy_modeling_dataset.csv
│       ├── final_recommendations.csv
│       └── preprocessing_report.txt
│
├── models/
│   ├── best_lead_time_model.joblib
│   ├── categorical_preprocessor.joblib
│   └── xgboost_pipeline.joblib
│
├── notebook/
│   ├── 01_data_preprocessing.ipynb
│   └── 03_model_training.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── factory_rules.py
│   ├── optimization.py
│   └── recommendation_engine.py
│
├── tests/
│   ├── test_best_alternative.py
│   ├── test_classify_opportunities.py
│   ├── test_data_loader.py
│   ├── test_full_pipeline.py
│   ├── test_geographic_opportunities.py
│   ├── test_optimization.py
│   └── test_recommendation_engine.py
│
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── start.txt
└── uv.lock
```

## Data

The supplied original CSV contains **10,194 rows and 18 columns**. The
project creates processed datasets for audit and modeling workflows.

  -------------------------------------------------------------------------------------------------------
  File                                                 Purpose                                 Dimensions
  ---------------------------------------------------- --------------------- ----------------------------
  `data/Nassau_Candy_Distributor.csv`                  Original order                         10,194 × 18
                                                       dataset               

  `data/processed/nassau_candy_processed_audit.csv`    Processed audit and                    10,194 × 42
                                                       geographic dataset    

  `data/processed/nassau_candy_modeling_dataset.csv`   Modeling dataset                        10,194 × 5

  `data/processed/final_recommendations.csv`           Prepared                                   11 × 30
                                                       recommendation output 
  -------------------------------------------------------------------------------------------------------

The audit dataset includes order details, product and factory
assignments, financial fields, date-derived fields, geographic
coordinates, distances to the five factories, and distance to the mapped
current factory.

### Factory-product mapping

The project defines 15 product-to-factory assignments in
`src/factory_rules.py`:

  -----------------------------------------------------------------------
  Factory                             Assigned products
  ----------------------------------- -----------------------------------
  Lot's O' Nuts                       Wonka Bar - Nutty Crunch Surprise;
                                      Wonka Bar - Fudge Mallows; Wonka
                                      Bar -Scrumdiddlyumptious

  Wicked Choccy's                     Wonka Bar - Milk Chocolate; Wonka
                                      Bar - Triple Dazzle Caramel

  Sugar Shack                         Laffy Taffy; SweeTARTS; Nerds; Fun
                                      Dip; Fizzy Lifting Drinks

  Secret Factory                      Everlasting Gobstopper; Lickable
                                      Wallpaper; Wonka Gum

  The Other Factory                   Hair Toffee; Kazookles
  -----------------------------------------------------------------------

## Methodology

### Data preprocessing and validation

The preprocessing workflow prepares an audit dataset and a separate
modeling dataset. The supplied preprocessing report records the
following checks:

-   No missing values in the processed audit dataset.
-   No duplicate `Row ID` values.
-   No completely duplicated audit rows.
-   Product-to-factory mapping validation passed.
-   Factory-distance validation passed.
-   Financial formula validation passed.
-   Calendar feature validation passed.
-   Modeling dataset reload comparison passed.
-   No missing values in the modeling dataset.

Repeated business records were retained because they were not
established to be accidental duplicates.

### Geographic opportunity screening

For each order record, the recommendation logic compares the distance to
the mapped current factory with distances to the other factory
locations.

Distance savings are calculated as:

``` text
Distance Saved (km) =
    Current Factory Distance - Alternative Factory Distance

Distance Saved (%) =
    (Distance Saved / Current Factory Distance) * 100
```

Only alternatives with a positive distance reduction are retained as
geographic opportunities. The system then classifies mapping
compatibility and selects the closest geographic alternative per record.

**Distance values are straight-line geographic distances. They are not
road, truck-route, travel-time, or actual freight-cost calculations.**

### Machine-learning workflow

The repository contains model-training notebooks and serialized model
artifacts. The Streamlit prediction page loads the saved XGBoost
pipeline and evaluates an entered order across the five candidate
factories.

The modeling target is named `Lead Time` in the processed modeling
dataset. The preprocessing report explains that this target was
reconstructed using a baseline adjustment because the raw order-date and
ship-date differences were implausibly large.

Therefore: - The target is a **reconstructed lead-time proxy**. - It is
not verified actual shipping or delivery time. - Predictions should be
interpreted as estimates against that proxy. - Alternative-factory
predictions are scenario comparisons and may be extrapolations because
the historical dataset does not establish actual outcomes for products
manufactured at every alternative factory.

The training notebook contains model comparisons and evaluation
experiments. Reported scores should be interpreted in the context of the
reconstructed target and the specific experiment/split in which they
were calculated, not as proof of real-world forecasting accuracy.

## Installation

### Prerequisites

-   Python version supported by the project (`>=3.10`)
-   Git
-   [uv](https://docs.astral.sh/uv/) for environment and dependency
    management

### 1. Clone the repository

``` bash
git clone https://github.com/<your-username>/Nassau-Candy-Optimization.git
cd Nassau-Candy-Optimization
```

Replace `<your-username>` with the GitHub account that owns the
repository.

### 2. Install dependencies with uv

``` bash
uv sync
```

This installs the dependencies declared in `pyproject.toml` and uses the
project lock file when available.

### Alternative: install from requirements.txt

``` bash
python -m venv .venv
```

Windows PowerShell:

``` powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

``` bash
source .venv/bin/activate
pip install -r requirements.txt
```

For reproducible model loading, use dependency versions compatible with
the versions used to create the serialized scikit-learn and XGBoost
artifacts. The project dependency declarations should be kept aligned
with those training versions.

## Run the Streamlit Application

From the project root directory, run the following in **Windows
PowerShell**:

``` powershell
$env:PYTHONPATH = (Get-Location).Path
uv run python -m streamlit run app/streamlit_app.py
```

The `PYTHONPATH` setting makes the project root available for imports
from the `src` package.

Then open the local URL printed in the terminal, normally:

``` text
http://localhost:8501
```

Keep the terminal running while using the application. Stop the server
with `Ctrl + C`.

## Run Tests

From the project root:

Windows PowerShell:

``` powershell
$env:PYTHONPATH = (Get-Location).Path
uv run python -m pytest -q
```

Or, if the environment is already activated:

``` bash
python -m pytest -q
```

The test suite covers data loading, geographic opportunity generation,
opportunity classification, distance-based selection, optimization
summaries, and recommendation logic.

## Deployment

The application is structured for deployment on Streamlit Community
Cloud.

1.  Push the complete project repository to GitHub.

2.  Open [Streamlit Community Cloud](https://share.streamlit.io/).

3.  Connect the GitHub repository.

4.  Select the deployment branch (commonly `main`).

5.  Set the main file path to:

    ``` text
    app/streamlit_app.py
    ```

6.  Deploy and test the public application URL.

Ensure that `app/`, `src/`, `data/processed/`, `models/`, `assets/`, and
the dependency files are included in the repository. Do not commit
`.venv/`, cache directories, or secrets. Confirm that the cloud
environment uses compatible dependency versions and that project-root
imports resolve before treating the deployment as complete.

## Limitations and Responsible Interpretation

This project is a decision-support prototype, not an automated
factory-allocation system. The following limitations are documented in
the supplied preprocessing report and project outputs:

1.  **Lead-time quality:** Raw `Order Date` and `Ship Date` ranges are
    inconsistent, and raw date differences were reported as implausibly
    large. The target was reconstructed using a baseline adjustment.
2.  **Proxy target:** The model predicts the reconstructed lead-time
    proxy, not verified actual shipping or delivery time.
3.  **Geographic distance:** Factory distances are straight-line
    distances, not road or truck-route distances.
4.  **Factory feasibility:** The data does not establish production
    capacity, factory-specific manufacturing constraints, or operational
    suitability for every product-factory combination.
5.  **Financial interpretation:** Financial values have not been
    confirmed to represent a particular currency. Estimated margin or
    priority indicators are not verified savings.
6.  **Shipping costs:** The project data does not provide confirmed
    factory-specific freight costs or actual logistics cost changes.
7.  **Alternative-factory evidence:** Historical outcomes for products
    produced at all alternative factories are not established. ML
    what-if comparisons therefore require validation.
8.  **Recommendation status:** Prepared recommendations include pending
    validation fields. They are candidates for review, not approved
    operational decisions.

Before making a real factory reassignment, validate product
compatibility, production capacity, manufacturing costs, route
distances, freight rates, service levels, and operational constraints
with reliable business data.

## Future Improvements

-   Replace the reconstructed lead-time proxy with verified shipment or
    delivery timestamps.
-   Integrate road-network distances, route times, and actual freight
    rates.
-   Add factory capacity, production cost, and product compatibility
    constraints.
-   Validate alternative-factory scenarios using real operational
    history or controlled pilot data.
-   Improve model validation and monitor prediction error on future,
    independently collected records.
-   Add deployment monitoring and automated tests to the cloud workflow.

## Project Status

The repository includes the Streamlit application, source modules,
original and processed datasets, notebooks, serialized model artifacts,
recommendation output, and automated tests.

The application should be treated as an analytical prototype until the
documented data and operational limitations are resolved.

------------------------------------------------------------------------

**Project:** Nassau Candy Factory Optimization\
**Application:** Streamlit\
**Primary entry point:** `app/streamlit_app.py`
