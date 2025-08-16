import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="🚀 Startup Analysis Dashboard")

# Load Data
df = pd.read_csv('Startup_Funding_cleaned_final.csv')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# ---------------------- Overall Analysis ---------------------- #
def load_overall_analysis():
    st.title("📊 Overall Analysis")
    total = round(df['amount'].sum())
    max_funding = round(df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0])
    avg_funding = round(df.groupby('startup')['amount'].sum().mean())
    num_startups = df['startup'].nunique()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('💰 Total Funding', str(total) + ' Cr')
    with col2:
        st.metric('🏆 Max Funding', str(max_funding) + ' Cr')
    with col3:
        st.metric('📈 Avg Funding', str(avg_funding) + ' Cr')
    with col4:
        st.metric('🏢 Number of Startups', str(num_startups))

    st.header('📆 Month-on-Month (MOM) Graph')
    selected_option = st.selectbox('📌 Select Type', ['Total', 'Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype(str) + '-' + temp_df['year'].astype(str)
    fig5, ax5 = plt.subplots()
    ax5.plot(temp_df['x_axis'], temp_df['amount'], marker='o', color='teal')
    plt.xticks(rotation=45)
    st.pyplot(fig5)

# ---------------------- Startup Details ---------------------- #
def load_startup_details(startup):
    st.title(f'🏢 Detailed Analysis for: {startup}')
    startup_df = df[df['startup'] == startup].copy()

    st.subheader('🧾 Recent Funding Rounds')
    st.dataframe(startup_df[['date', 'investors', 'vertical', 'city', 'round', 'amount']]
                 .sort_values(by='date', ascending=False).head(5))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('📆 Funding Over Time')
        yearly = startup_df.groupby('year')['amount'].sum()
        st.line_chart(yearly)
    with col2:
        st.subheader('📊 Funding by Round')
        round_data = startup_df.groupby('round')['amount'].sum()
        st.bar_chart(round_data)

    st.subheader('🤝 Investor Contributions')
    investor_series = startup_df['investors'].dropna().str.split(',').explode().str.strip()
    startup_df = startup_df.reset_index(drop=True)
    investor_series = investor_series.reset_index(drop=True)
    startup_df = startup_df.assign(investor=investor_series)
    top_investors = startup_df.groupby('investor')['amount'].sum().sort_values(ascending=False)
    st.bar_chart(top_investors)
    st.dataframe(top_investors.reset_index().rename(columns={'investor': 'Investor', 'amount': 'Total Investment'}))

# ---------------------- Investor Details ---------------------- #
def load_investor_details(investor):
    st.title(f"💼 Investor Analysis: {investor}")
    last5_df = df[df['investors'].str.contains(investor)].head()[['date', 'startup', 'vertical', 'subvertical', 'city', 'round', 'amount']]

    st.subheader('🆕 Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        big_series = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('🏆 Biggest Investments')
        fig, ax = plt.subplots()
        ax.bar(big_series.index, big_series.values, color="orange")
        st.pyplot(fig)
    with col2:
        vertical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum()
        st.subheader('🏭 Sectors Invested In')
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series, labels=vertical_series.index, autopct='%1.1f%%')
        st.pyplot(fig1)
    with col3:
        round_series = df[df['investors'].str.contains(investor)].groupby('round')['amount'].sum()
        st.subheader('📊 Stages Invested In')
        fig2, ax2 = plt.subplots()
        ax2.pie(round_series, labels=round_series.index, autopct='%1.1f%%')
        st.pyplot(fig2)
    with col4:
        city_series = df[df['investors'].str.contains(investor)].groupby('city')['amount'].sum()
        st.subheader('🌆 Cities Invested In')
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series, labels=city_series.index, autopct='%1.1f%%')
        st.pyplot(fig3)

    year_series = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum()
    st.subheader('📈 Year-on-Year (YOY) Investment Trend')
    fig4, ax4 = plt.subplots()
    ax4.plot(year_series.index, year_series.values, marker='o', color='green')
    st.pyplot(fig4)

# ---------------------- Sidebar Navigation ---------------------- #
st.sidebar.title('📊 Startup Funding Analysis')
option = st.sidebar.selectbox("🔎 Select One", ['Overall Analysis', 'Startups', 'Investors'])

if option == 'Overall Analysis':
    load_overall_analysis()
elif option == 'Startups':
    selected_startup = st.sidebar.selectbox('🏢 Select Startup', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('📌 Show Startup Details')
    st.title('🚀 Startup Analysis')
    if btn1:
        load_startup_details(selected_startup)
else:
    selected_investors = st.sidebar.selectbox('💼 Select Investor', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('📌 Show Investor Details')
    if btn2:
        load_investor_details(selected_investors)