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
