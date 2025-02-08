import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
import matplotlib.pyplot as plt
from pypfopt import plotting, risk_models

from portfolio_optimizer import PortfolioOptimizer
from data_manager import DataManager
from utils import plot_correlation_matrix, plot_correlation_matrix_seaborn, plot_efficient_frontier_cla

def main():
    st.set_page_config(page_title="Portfolio Optimizer", layout="wide")
    st.title("Portfolio Optimization Tool")
    
    # Initialize session state
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    
    # Sidebar for data input and model selection
    with st.sidebar:
        st.header("Configuration")
        
        # Data Input Section
        st.subheader("Data Input")
        data_source = st.radio(
            "Choose Data Source",
            ["Stock Tickers", "Local CSV File"]
        )
        
        if data_source == "Stock Tickers":
            # Default tickers from the example
            default_tickers = "MSFT,AMZN,KO,MA,COST,LUV,XOM,PFE,JPM,UNH,ACN,DIS,GILD,F,TSLA"
            tickers_input = st.text_area(
                "Enter stock tickers (comma-separated)",
                value=default_tickers,
                help="Enter stock tickers separated by commas"
            )
            tickers = [ticker.strip() for ticker in tickers_input.split(",")]
            
            # Use period instead of start/end dates
            period = st.selectbox(
                "Select Time Period",
                ["1y", "2y", "5y", "10y", "max"],
                index=4,  # default to max
                help="Select the time period for historical data"
            )

        else:  # Local CSV File
            uploaded_file = st.file_uploader(
                "Upload CSV file with stock prices",
                type="csv",
                help="CSV file should have dates as index and stock prices in columns"
            )
            
            # Option to use sample data
            use_sample_data = st.checkbox(
                "Use sample data (S&P 500 prices)",
                help="Use built-in sample data for testing"
            )
        
        # Model Selection
        st.subheader("Model Selection")
        risk_model = st.selectbox(
            "Risk Model",
            ["Sample Covariance", "Ledoit-Wolf Shrinkage", "Semi Covariance"]
        )
        
        returns_model = st.selectbox(
            "Expected Returns Model",
            ["Mean Historical Return", "CAPM Return", "EMA Historical Return"]
        )
        
        # Optimization Parameters
        st.subheader("Optimization Parameters")
        allow_short = st.checkbox("Allow Short Selling", False)
        weight_bounds = (-1, 1) if allow_short else (0, 1)
        
        optimization_method = st.selectbox(
            "Optimization Method",
            ["Maximum Sharpe Ratio", "Minimum Volatility", 
             "Efficient Return", "Efficient Risk"]
        )

    # Main content
    try:
        # Load and process data
        with st.spinner("Loading data..."):
            data_manager = st.session_state.data_manager
            
            if data_source == "Stock Tickers":
                prices_df = data_manager.get_stock_data(tickers, period)
            else:
                if use_sample_data:
                    # Load sample data from the package
                    sample_data_path = "cookbook/data/spy_prices.csv"
                    if os.path.exists(sample_data_path):
                        prices_df = pd.read_csv(
                            sample_data_path,
                            index_col=0,
                            parse_dates=True
                        )
                    else:
                        st.error("Sample data file not found!")
                        return
                elif uploaded_file is not None:
                    prices_df = pd.read_csv(
                        uploaded_file,
                        index_col=0,
                        parse_dates=True
                    )
                else:
                    st.warning("Please upload a CSV file or use sample data")
                    return
            
            # Display raw data
            st.subheader("Raw Price Data")
            col1, col2 = st.columns(2)
            with col1:
                st.write("First 5 rows")
                st.dataframe(prices_df.head())
            with col2:
                st.write("Last 5 rows")
                st.dataframe(prices_df.tail())
            
            optimizer = PortfolioOptimizer(
                prices_df,
                risk_model=risk_model,
                returns_model=returns_model,
                weight_bounds=weight_bounds
            )

        # Display basic statistics
        st.header("Portfolio Analysis")
        
        
        # Create matplotlib figure for covariance matrix
        fig_cov, ax_cov = plt.subplots(figsize=(10, 8))
        
        # Get covariance matrix based on selected risk model
        if risk_model == "Sample Covariance":
            cov_matrix = risk_models.sample_cov(prices_df)
        elif risk_model == "Ledoit-Wolf Shrinkage":
            cov_matrix = risk_models.CovarianceShrinkage(prices_df).ledoit_wolf()
        else:  # Semi Covariance
            cov_matrix = risk_models.semicovariance(prices_df)
        # print("risk_model:" ,risk_model)
        # print(cov_matrix)
            
        # # Plot covariance matrix
        st.subheader("Covariance Matrix")
        fig_corr = plot_correlation_matrix_seaborn(cov_matrix)
        st.pyplot(fig_corr)
        
        # Asset Returns (full width)
        st.subheader("Asset Returns")
        
        # Create matplotlib figure for asset returns
        fig_returns, ax_returns = plt.subplots(figsize=(10, 6))
        returns_series = optimizer.get_expected_returns()['Expected Return']
        # print(returns_series)
        returns_series.plot.barh(ax=ax_returns)
        ax_returns.set_title('Expected Returns by Asset')
        ax_returns.set_xlabel('Expected Return')
        plt.tight_layout()
        st.pyplot(fig_returns)

        # Optimization Section
        st.header("Portfolio Optimization - Summary")


        
        if optimization_method == "Maximum Sharpe Ratio":
            weights = optimizer.optimize_maximum_sharpe()
        elif optimization_method == "Minimum Volatility":
            weights = optimizer.optimize_minimum_volatility()
        elif optimization_method == "Efficient Return":
            target_return = st.slider(
                "Target Return (%)", 
                min_value=0, 
                max_value=100, 
                value=20
            ) / 100
            weights = optimizer.optimize_efficient_return(target_return)
        else:  # Efficient Risk
            target_risk = st.slider(
                "Target Risk (%)", 
                min_value=0, 
                max_value=50, 
                value=20
            ) / 100
            weights = optimizer.optimize_efficient_risk(target_risk)


        weights_display = weights[weights > 0.001]  # Filter out very small weights
        weights_data = pd.DataFrame({
            'Asset': weights_display.index,
            'Weight': weights_display.values * 100
        }).round(2)

        # Performance metrics
        perf = optimizer.get_portfolio_performance(weights)
        metrics_data = pd.DataFrame({
            'Metric': ['Expected Return', 'Volatility', 'Sharpe Ratio'],
            'Value': [
                f"{perf[0]:.2%}",
                f"{perf[1]:.2%}",
                f"{perf[2]:.2f}"
            ]
        })

        
        # Create pie chart with explicit type conversion
        fig_pie = go.Figure(data=[go.Pie(
            labels=weights_data['Asset'].tolist(),  # Convert to list explicitly
            values=weights_data['Weight'].astype(float).tolist(),  # Convert to float and list
            hole=0.3,
            textinfo='value+label+percent',  # Modified to show all information
            hovertemplate="<b>%{label}</b><br>" +
                        "Weight: %{value:.2f}%<br>" +
                        "<extra></extra>",
            textposition='outside',
            texttemplate='%{label}<br>%{value:.2f}%',  # Show exact values
            showlegend=True
        )])

        # Update layout
        fig_pie.update_layout(
            title={
                'text': "Portfolio Allocation",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=True,
            legend={
                'orientation': 'v',
                'yanchor': 'middle',
                'y': 0.5,
                'xanchor': 'right',
                'x': 1.1
            },
            height=500,
            margin=dict(t=50, b=50, l=50, r=150)
        )

        # Ensure the figure is properly updated
        fig_pie.update_traces(
            rotation=90,
            pull=[0.05] * len(weights_data),
            textfont_size=12
        )


        # Create two columns with better spacing
        col_weights, col_performance = st.columns([1, 1])

        with col_weights:
            st.markdown("### Optimal Portfolio Weights")
            # Format the weights dataframe
            weights_df = pd.DataFrame({
                'Asset': weights.index,
                'Weight (%)': (weights.values * 100).round(2)  # Round to 2 decimal places
            }).reset_index(drop=True)  # Reset index to hide it
            # Display with improved styling
            st.dataframe(
                weights_df,
                use_container_width=True
            )

        with col_performance:
            st.markdown("### Portfolio Performance")
            # Create and format metrics dataframe
            metrics_df = pd.DataFrame({
                'Metric': ['Expected Return', 'Volatility', 'Sharpe Ratio'],
                'Value': [
                    f"{perf[0]:.2%}",
                    f"{perf[1]:.2%}",
                    f"{perf[2]:.2f}"
                ]
            }).reset_index(drop=True)  # Reset index to hide it
            # Display with improved styling
            st.dataframe(
                metrics_df,
                use_container_width=True
            )

        # Display pie chart with some spacing
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        st.plotly_chart(fig_pie, use_container_width=True)        


        # Plot efficient frontier
        st.subheader("Efficient Frontier")
        # fig_ef = plot_efficient_frontier_cla(optimizer)
        # print(f'fig_ef: ${fig_ef}')
        # st.plotly_chart(fig_ef)
        
        fig_ef = plot_efficient_frontier_cla(prices_df)
        st.plotly_chart(fig_ef, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")





if __name__ == "__main__":
    main() 