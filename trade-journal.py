import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import calendar
from datetime import datetime

def load_data(file):
    df = pd.read_csv(file)
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    df['Net P/L'] = df['Net P/L'].str.replace(',', '').astype(float)
    return df

def calculate_pnl(df):
    return df['Net P/L'].sum()

def analyze_trades(df):
    winning_trades = df[df['Net P/L'] > 0]
    losing_trades = df[df['Net P/L'] < 0]
    return winning_trades, losing_trades

def create_pnl_graph(df):
    df_sorted = df.sort_values('Date/Time')
    cumulative_pnl = df_sorted['Net P/L'].cumsum()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted['Date/Time'], y=cumulative_pnl,
                             mode='lines', name='Cumulative P/L'))
    fig.update_layout(title='Cumulative Profit/Loss Over Time',
                      xaxis_title='Date/Time',
                      yaxis_title='Cumulative P/L')
    return fig

def create_calendar_data(df):
    daily_data = df.groupby(df['Date/Time'].dt.date).agg({
        'Net P/L': 'sum',
        'Symbol': 'count'
    }).reset_index()
    return daily_data

st.title('Trade Journal')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    st.subheader('Data Preview')
    st.dataframe(df.head())
    
    total_pnl = calculate_pnl(df)
    st.subheader(f'Total P/L: ${total_pnl:.2f}')
    
    winning_trades, losing_trades = analyze_trades(df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Winning Trades')
        st.write(f'Count: {len(winning_trades)}')
        st.dataframe(winning_trades[['Date/Time', 'Symbol', 'Net P/L']])
    
    with col2:
        st.subheader('Losing Trades')
        st.write(f'Count: {len(losing_trades)}')
        st.dataframe(losing_trades[['Date/Time', 'Symbol', 'Net P/L']])
    
    st.subheader('Profit/Loss Graph')
    fig = create_pnl_graph(df)
    st.plotly_chart(fig)
    
    st.subheader('Trade Calendar')
    daily_data = create_calendar_data(df)
    
    # Display calendar
    current_date = datetime.now()
    year = st.selectbox('Select Year', range(df['Date/Time'].dt.year.min(), df['Date/Time'].dt.year.max() + 1), index=current_date.year - df['Date/Time'].dt.year.min())
    month = st.selectbox('Select Month', range(1, 13), index=current_date.month - 1)
    
    cal = calendar.monthcalendar(year, month)
    
    # Create a DataFrame for the selected month
    month_data = daily_data[
        (daily_data['Date/Time'].dt.year == year) & 
        (daily_data['Date/Time'].dt.month == month)
    ]
    
    # Display calendar
    st.write(f"Calendar for {calendar.month_name[month]} {year}")
    
    # Create calendar table
    table_data = [["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append("")
            else:
                date = pd.Timestamp(year=year, month=month, day=day)
                day_data = month_data[month_data['Date/Time'].dt.date == date.date()]
                if not day_data.empty:
                    pnl = day_data['Net P/L'].values[0]
                    trades = day_data['Symbol'].values[0]
                    cell_content = f"{day}\n${pnl:.2f}\n{trades} trades"
                else:
                    cell_content = str(day)
                week_data.append(cell_content)
        table_data.append(week_data)
    
    st.table(table_data)
