## Step 1: Defining the goal
- The objective is to create a user-friendly application for analyzing personal expenses based on bank statements.
- The app should automatically categorize expenses (food, transport, entertainment, etc.) and visualize the results.

## Step 2: Data preparation
- Input data format - CSV or TXT file containing the bank statement.
- Key fields: transaction date, description, amount.
> Date,Description,Amount
> 2025-07-01,Pyaterochka Store,1500.50
> 2025-07-02,Taxi to work,300
> 2025-07-03,Pobeda Cinema,800
> 2025-07-04,Internet payment,400
> 2025-07-05,Vkusno Restaurant,1200

- Develop a function to read and preprocess the file (date parsing, data cleaning).
In my code, the function responsible for reading and preprocessing the file - including date parsing and data cleaning - is called load_and_preprocess_data.
This function handles loading the input file (CSV or TXT), parsing the date column, verifying that the required columns are present, cleaning the data by removing invalid entries (such as rows with unrecognized dates), and formatting the data properly for further analysis.
For example, it reads the file from disk or from an uploaded buffer, converts the 'Date' column to datetime, checks for missing or incorrect data, and prepares the dataset to be used by the analysis functions.

```cs
def load_and_preprocess_data(file_path=None, uploaded_file=None):
    """
    Load and preprocess bank statement data.

    Args:
        file_path (str): Path to local file.
        uploaded_file (UploadedFile): File uploaded via Streamlit.

    Returns:
        pd.DataFrame or None: Preprocessed data or None if loading fails.
    """
    data = None
    try:
        if file_path:
            # Try to load file from disk, pandas will infer delimiter automatically
            data = pd.read_csv(file_path, delimiter=None)
            st.success(f"File successfully loaded from {file_path}")
        elif uploaded_file:
            try:
                # Try reading uploaded file with comma delimiter
                data = pd.read_csv(uploaded_file, delimiter=',')
            except:
                # If fails, reset file pointer and try tab delimiter
                uploaded_file.seek(0)
                data = pd.read_csv(uploaded_file, delimiter='\t')
            st.success("File successfully loaded from uploaded file")
        else:
            st.warning("No file path or uploaded file provided.")
            return None

        # Check required columns
        required_columns = {'Date', 'Description', 'Amount'}
        if not required_columns.issubset(data.columns):
            st.error(f"The file must contain columns: {required_columns}")
            return None

        # Convert 'Date' to datetime and drop rows with invalid dates
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        if data['Date'].isnull().any():
            st.warning("Some dates were not recognized and will be excluded")
            data = data.dropna(subset=['Date'])

        return data

    except Exception as e:
        st.error(f"Failed to load or preprocess data: {e}")
        return None
```


## Step 3: Transaction categorization
- Create a dictionary of categories and keywords (e.g., “cafe” belongs to food).
```cs
categories = {
    'Food': ['store', 'cafe', 'restaurant', 'groceries', 'snack'],
    'Transport': ['taxi', 'metro', 'bus', 'gasoline', 'transport'],
    'Entertainment': ['cinema', 'theater', 'club', 'concert', 'entertainment'],
    'Bills': ['internet', 'electricity', 'water', 'gas', 'utilities'],
}
```
- Write a function that assigns each transaction to a category based on its description.
```cs
def categorize(description):
    description = description.lower()
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    return 'Other'
```
This function checks the description and returns the matching category.

## Step 4: Visualization and analysis
- Use Pandas and Matplotlib libraries to analyze data and generate charts.
**[Pandas](https://pandas.pydata.org/)** is a Python library for data manipulation and analysis. It provides convenient data structures like DataFrame and Series that allow efficient handling, processing, and visualization of tabular data. Pandas is widely used for data cleaning, aggregation, filtering, as well as for working with time series and performing statistical analysis.
**[Matplotlib](https://matplotlib.org/)** is a popular Python library for creating plots and data visualizations. It enables the creation of various types of charts — line plots, histograms, scatter plots, pie charts, and more. Matplotlib is commonly used in scientific research, data analysis, and reporting to visually represent information clearly.

Pandas is used for data processing, grouping, and aggregation (groupby, sum, apply, to_datetime).
Matplotlib is used to create visualizations such as pie charts (plot.pie) and other types of plots.

```cs
category_sums = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
```
Here, Pandas is used to group data by the "Category" column and calculate the sum of expenses in each category.
```cs
  fig1, ax1 = plt.subplots()
    category_sums.plot.pie(autopct='%1.1f%%', startangle=90, ax=ax1)
    ax1.set_ylabel('')
    ax1.set_title('Expense Distribution by Category')
    st.pyplot(fig1)
```
Here, Matplotlib creates a pie chart to visualize the distribution of expenses by category. The chart is displayed in Streamlit using st.pyplot().

- Create a pie chart to show expenses by category.
- Implement monthly expense comparison to highlight increases or decreases.
```cs
 data['Month'] = data['Date'].dt.to_period('M')
    monthly_sums = data.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)

 if len(monthly_sums) > 1:
        current_month = monthly_sums.index[-1]
        previous_month = monthly_sums.index[-2]
        diff = monthly_sums.loc[current_month] - monthly_sums.loc[previous_month]

        st.subheader(f"Expense Changes: {previous_month} → {current_month}")
        for category, change in diff.items():
            if change > 0:
                st.write(f"📈 Expenses for **{category}** increased by {change:.2f}")
            elif change < 0:
                st.write(f"📉 Expenses for **{category}** decreased by {abs(change):.2f}")
            else:
                st.write(f"➖ Expenses for **{category}** remained unchanged")
```
What happens:
Extract the month from the date.
Calculate the total expenses per category for each month.
Compare the last two months.
Display changes for each category: increase, decrease, or no change.

## Step 5: Web interface development
- Use Streamlit to build a simple and interactive user interface.
**[Streamlit](https://streamlit.io/)** is a Python library that enables fast and easy creation of interactive web applications for data visualization and machine learning without the need for web development skills.
```cs
def main():
    st.title("Financial Expense Analysis")

    file_path = r"X:\bank_statement.txt"
    data = load_and_preprocess_data(file_path=file_path)

    # If file loading from disk failed, ask user to upload manually
    if data is None:
        uploaded_file = st.file_uploader("Upload a CSV or TXT file with your bank statement", type=["csv", "txt"])
        if uploaded_file is not None:
            data = load_and_preprocess_data(uploaded_file=uploaded_file)

    if data is not None:
        analyze_data(data)
```
- Add the ability for users to upload their files through the web app.
- Display a table with processed data and visual charts.

##Step 6: Testing and improvements
Add error handling (e.g., missing required columns or incorrect date format).
1. Handling missing required columns
```cs
# In analyze_data()
if not {'Date', 'Description', 'Amount'}.issubset(data.columns):
    st.error("The file must contain columns: 'Date', 'Description', 'Amount'")
    return

# In load_and_preprocess_data()
required_columns = {'Date', 'Description', 'Amount'}
if not required_columns.issubset(data.columns):
    st.error(f"The file must contain columns: {required_columns}")
    return None
```
This checks if the necessary columns are present. If not, the app stops further processing and shows an error message to the user.

2. Handling incorrect date format
```cs
# Attempt to convert 'Date' column to datetime
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Drop rows with unrecognized dates
if data['Date'].isnull().any():
    st.warning("Some dates were not recognized and will be excluded")
    data = data.dropna(subset=['Date'])
```
This handles invalid date formats by coercing parsing errors to NaT, warning the user, and excluding those rows from further analysis.

<img width="2555" height="1346" alt="Image" src="https://github.com/user-attachments/assets/65d777a2-6388-41ff-abe4-5d8bbb8065b0" />

# 📁 app.py
```cs
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

categories = {
    'Food': ['store', 'cafe', 'restaurant', 'groceries', 'snack'],
    'Transport': ['taxi', 'metro', 'bus', 'gasoline', 'transport'],
    'Entertainment': ['cinema', 'theater', 'club', 'concert', 'entertainment'],
    'Bills': ['internet', 'electricity', 'water', 'gas', 'utilities'],
}

def categorize(description):
    description = description.lower()
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    return 'Other'

def analyze_data(data):
    if not {'Date', 'Description', 'Amount'}.issubset(data.columns):
        st.error("The file must contain columns: 'Date', 'Description', 'Amount'")
        return

    data['Category'] = data['Description'].apply(categorize)
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    if data['Date'].isnull().any():
        st.warning("Some dates were not recognized and will be excluded")
        data = data.dropna(subset=['Date'])

    st.subheader("Processed Data")
    st.dataframe(data.head(20))

    category_sums = data.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    st.subheader("Expenses by Category")
    st.write(category_sums)

    fig1, ax1 = plt.subplots()
    category_sums.plot.pie(autopct='%1.1f%%', startangle=90, ax=ax1)
    ax1.set_ylabel('')
    ax1.set_title('Expense Distribution by Category')
    st.pyplot(fig1)

    data['Month'] = data['Date'].dt.to_period('M')
    monthly_sums = data.groupby(['Month', 'Category'])['Amount'].sum().unstack(fill_value=0)

    if len(monthly_sums) > 1:
        current_month = monthly_sums.index[-1]
        previous_month = monthly_sums.index[-2]
        diff = monthly_sums.loc[current_month] - monthly_sums.loc[previous_month]

        st.subheader(f"Expense Changes: {previous_month} → {current_month}")
        for category, change in diff.items():
            if change > 0:
                st.write(f"📈 Expenses for **{category}** increased by {change:.2f}")
            elif change < 0:
                st.write(f"📉 Expenses for **{category}** decreased by {abs(change):.2f}")
            else:
                st.write(f"➖ Expenses for **{category}** remained unchanged")

def load_and_preprocess_data(file_path=None, uploaded_file=None):
    """
    Load and preprocess bank statement data.

    Args:
        file_path (str): Path to local file.
        uploaded_file (UploadedFile): File uploaded via Streamlit.

    Returns:
        pd.DataFrame or None: Preprocessed data or None if loading fails.
    """
    data = None
    try:
        if file_path:
            # Try to load file from disk, pandas will infer delimiter automatically
            data = pd.read_csv(file_path, delimiter=None)
            st.success(f"File successfully loaded from {file_path}")
        elif uploaded_file:
            try:
                # Try reading uploaded file with comma delimiter
                data = pd.read_csv(uploaded_file, delimiter=',')
            except:
                # If fails, reset file pointer and try tab delimiter
                uploaded_file.seek(0)
                data = pd.read_csv(uploaded_file, delimiter='\t')
            st.success("File successfully loaded from uploaded file")
        else:
            st.warning("No file path or uploaded file provided.")
            return None

        # Check required columns
        required_columns = {'Date', 'Description', 'Amount'}
        if not required_columns.issubset(data.columns):
            st.error(f"The file must contain columns: {required_columns}")
            return None

        # Convert 'Date' to datetime and drop rows with invalid dates
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        if data['Date'].isnull().any():
            st.warning("Some dates were not recognized and will be excluded")
            data = data.dropna(subset=['Date'])

        return data

    except Exception as e:
        st.error(f"Failed to load or preprocess data: {e}")
        return None

def main():
    st.title("Financial Expense Analysis")

    file_path = r"X:\bank_statement.txt"
    data = load_and_preprocess_data(file_path=file_path)

    # If file loading from disk failed, ask user to upload manually
    if data is None:
        uploaded_file = st.file_uploader("Upload a CSV or TXT file with your bank statement", type=["csv", "txt"])
        if uploaded_file is not None:
            data = load_and_preprocess_data(uploaded_file=uploaded_file)

    if data is not None:
        analyze_data(data)

if __name__ == "__main__":
    main()
```
