import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def load_data(file):
    df = pd.read_csv(file)
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    df['Net P/L'] = df['Net P/L'].str.replace(',', '.').astype(float)
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
