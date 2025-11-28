# ADS HW1 - Data Analysis & Engineering Project

A comprehensive data analysis and engineering project focusing on customer churn prediction using the Telco Customer Churn dataset. This project includes exploratory data analysis, data cleaning, visualization, feature engineering, and a bonus web scraping component.

## 📋 Project Overview

This project implements a complete data analysis pipeline covering:
1. **Exploratory Data Analysis (EDA)** and Data Cleaning
2. **Data Visualization** with multiple chart types
3. **Feature Engineering** with feature selection and dimensionality reduction
4. **Web Scraping** (Bonus) - Samand car listings from bama.ir

## 📊 Dataset

### Telco Customer Churn Dataset

The project uses the **Telco Customer Churn** dataset, which contains information about 7,043 customers with 21 features each. The dataset includes:

- **Target Variable:** `Churn` (Yes/No) - indicates whether a customer left within the last month
- **Features:**
  - Customer demographics (Gender, SeniorCitizen, Partner, Dependents)
  - Services (PhoneService, MultipleLines, InternetService, OnlineSecurity, etc.)
  - Account information (Tenure, Contract, PaymentMethod)
  - Billing (MonthlyCharges, TotalCharges)
  - CustomerFeedback (generated using GPT-3.5)

**Dataset Source:** [Kaggle - Telco Customer Churn with Realistic Customer Feedback](https://www.kaggle.com/datasets/beatafaron/telco-customer-churn-realistic-customer-feedback)

**Local Path:** `data/telco_customer_churn.csv`

## 📁 Project Structure

```
ADS_HW1/
├── data/                          # Dataset files
│   ├── telco_customer_churn.csv   # Main dataset
│   └── samand_listings.xlsx       # Scraped car data (bonus)
├── notebooks/                      # Jupyter notebooks
│   ├── ads_hw1_analysis_final.ipynb  # Main analysis notebook
│   └── ads_hw1_analysis.ipynb        # Development notebook
├── scripts/                        # Python scripts
│   └── bama_scraper.py            # Web scraper for bama.ir
├── reports/                        # Generated reports (if any)
├── docs/                          # Documentation
│   └── todo_list.txt
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended)
- Ubuntu 24.04 LTS (or compatible Linux environment)

### Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd ADS_HW1
   ```

2. **Create and activate virtual environment:**
   ```bash
   uv venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv pip sync requirements.txt
   ```

## 📦 Dependencies

The project requires the following Python packages:

- **Data Processing:** `pandas`, `numpy`
- **Visualization:** `matplotlib`, `seaborn`, `plotly`, `bokeh`
- **Machine Learning:** `scikit-learn`, `scipy`
- **File I/O:** `openpyxl`, `xlsxwriter`
- **Web Scraping:** `requests`, `beautifulsoup4`
- **Plot Export:** `kaleido`

See `requirements.txt` for specific versions.

## 🎯 Project Components

### 1. Exploratory Data Analysis & Data Cleaning

**Location:** `notebooks/ads_hw1_analysis_final.ipynb`

**Tasks:**
- Comprehensive EDA with meaningful insights
- Handling missing, invalid, or duplicate values
- Converting all features to numerical values
- Normalization/standardization
- Clear explanations and readable notebook

**Key Findings:**
- Missing values in `TotalCharges` (blank entries for new customers)
- Data type conversions (categorical to numerical)
- Feature distributions and correlations

### 2. Data Visualization

**Location:** `notebooks/ads_hw1_analysis_final.ipynb`

**Visualization Types:**
- ✅ Pie charts
- ✅ Box plots
- ✅ Line charts and multi-line charts
- ✅ Bar charts (grouped and stacked)
- ✅ Scatter plots and bubble charts
- ✅ Charts with error bars
- ✅ Interactive charts using Plotly/Bokeh

**Requirements Met:**
- All charts include proper titles
- Axis labels and ranges
- Legends for clarity

### 3. Feature Engineering

**Location:** `notebooks/ads_hw1_analysis_final.ipynb`

**Feature Engineering Techniques:**
- **Ratios:** Average revenue per month (`TotalCharges / tenure`)
- **Binning:** Tenure buckets, monthly charge categories
- **Mathematical Functions:** Service count aggregations
- **Feature Combinations:** Combined service features
- **Date/Time Transformations:** Tenure-based features

**Advanced Techniques:**
- **Feature Selection:** Mutual Information analysis
- **Dimensionality Reduction:** Principal Component Analysis (PCA)

**Reflective Question:**
> "When is feature engineering a nice-to-have option, and when is it a must-have?"
>
> *Answer included in the notebook*

### 4. Web Scraping (Bonus)

**Location:** `scripts/bama_scraper.py`

**Task:**
Extract data for 50 "Samand" cars manufactured after 1385 (Persian calendar) from bama.ir.

**Extracted Fields:**
- Price
- Mileage
- Color
- Production year
- Transmission type (manual/automatic)
- Description

**Output:** `data/samand_listings.xlsx`

**Usage:**
```bash
python scripts/bama_scraper.py
```

## 📖 Usage

### Running the Analysis Notebook

1. **Start Jupyter:**
   ```bash
   jupyter notebook
   # or
   jupyter lab
   ```

2. **Open the notebook:**
   - Navigate to `notebooks/ads_hw1_analysis_final.ipynb`
   - Run all cells sequentially

3. **Note on Dataset Path:**
   - The notebook automatically checks for the Kaggle dataset path first
   - Falls back to `data/telco_customer_churn.csv` if not found

### Running the Web Scraper

```bash
python scripts/bama_scraper.py
```

The scraper will:
- Query the bama.ir API for Samand cars
- Filter for production year > 1385
- Extract required fields
- Save results to `data/samand_listings.xlsx`

## 📈 Results & Outputs

### Analysis Notebook
- Complete EDA with insights
- Cleaned and preprocessed dataset
- Comprehensive visualizations
- Feature engineering results
- PCA analysis
- Mutual information feature selection

### Web Scraper
- Excel file with 50+ Samand car listings
- All required fields extracted
- Timestamped output files

## 🔧 Technical Details

### Data Cleaning Highlights
- Handled missing `TotalCharges` values (11 records with blank entries)
- Converted categorical variables to numerical (one-hot encoding, label encoding)
- Standardized numerical features using `StandardScaler`

### Feature Engineering Highlights
- Created service count features
- Binned tenure and charges into categories
- Calculated revenue ratios
- Applied PCA for dimensionality reduction

### Visualization Highlights
- Static plots using matplotlib/seaborn
- Interactive plots using Plotly
- Error bars for uncertainty visualization
- Multi-line charts for trend analysis

## 📝 Notes

- The project follows best practices for data analysis workflows
- All code is well-documented and readable
- The notebook includes clear explanations for each step
- Error handling is implemented in the web scraper

---

**Last Updated:** November 2024

