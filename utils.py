import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pypfopt import CLA, risk_models, expected_returns

def plot_correlation_matrix(correlation_matrix):
    """
    Create a correlation matrix heatmap using plotly
    """
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1
    ))
    
    fig.update_layout(
        title='Asset Correlation Matrix',
        height=500
    )
    
    return fig


def plot_correlation_matrix_seaborn(cov_matrix):
    """
    Create a correlation matrix plot using seaborn
    """
    # Convert covariance matrix to correlation matrix
    corr_matrix = cov_matrix.copy()
    for i in range(len(cov_matrix.columns)):
        for j in range(len(cov_matrix.columns)):
            corr_matrix.iloc[i,j] = cov_matrix.iloc[i,j]/(np.sqrt(cov_matrix.iloc[i,i])*np.sqrt(cov_matrix.iloc[j,j]))
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create heatmap
    sns.heatmap(
        corr_matrix, 
        annot=True,  # Show numbers in cells
        cmap='coolwarm',  # Color scheme
        center=0,  # Center the colormap at 0
        square=True,  # Make cells square
        fmt='.2f',  # Format numbers to 2 decimal places
        ax=ax
    )
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Add title
    plt.title('Correlation Matrix', pad=20)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

# def plot_efficient_frontier(optimizer):
#     """
#     Plot the efficient frontier using plotly
#     """
#     returns = []
#     risks = []
    
#     # Generate points along the efficient frontier
#     for return_target in np.linspace(0.1, 0.4, 30):
#         try:
#             weights = optimizer.optimize_efficient_return(return_target)
#             portfolio_performance = optimizer.get_portfolio_performance(weights)
#             returns.append(portfolio_performance[0])
#             risks.append(portfolio_performance[1])
#         except:
#             continue
            
#     fig = go.Figure()
    
#     # Add efficient frontier line
#     fig.add_trace(go.Scatter(
#         x=risks,
#         y=returns,
#         mode='lines',
#         name='Efficient Frontier'
#     ))
    
#     fig.update_layout(
#         title='Efficient Frontier',
#         xaxis_title='Portfolio Risk (Volatility)',
#         yaxis_title='Expected Return',
#         height=500
#     )
    
#     return fig 

# def plot_efficient_frontier(optimizer):
#     """
#     Creates an interactive Plotly graph of the efficient frontier using CLA
    
#     Args:
#         optimizer: PortfolioOptimizer instance
    
#     Returns:
#         fig: Plotly figure object
#     """
#     import plotly.graph_objects as go
#     from pypfopt import CLA
#     import numpy as np
    
#     # Get the efficient frontier data using CLA
#     mu = optimizer.expected_returns  # This is already a pandas Series
#     S = optimizer.covariance_matrix  # Using the correct attribute name
    
#     # Initialize CLA object
#     cla = CLA(mu, S)
    
#     # Generate points along the efficient frontier
#     assets = len(mu)
#     valid_points = []  # Store valid points as we find them
    
#     # Get efficient frontier points
#     returns_range = np.linspace(mu.min(), mu.max(), 100)  # Reduced number of points for stability
    
#     for ret in returns_range:
#         try:
#             weights = cla.efficient_return(ret)
#             std = np.sqrt(weights.T @ S @ weights)
#             sharpe = ret / std if std > 0 else 0
#             valid_points.append({
#                 'return': ret,
#                 'volatility': std,
#                 'sharpe': sharpe,
#                 'weights': weights
#             })
#         except Exception:
#             continue
    
#     # Check if we have any valid points
#     if not valid_points:
#         # If no valid points, create a basic scatter plot of individual assets
#         fig = go.Figure()
#         fig.add_trace(
#             go.Scatter(
#                 x=np.sqrt(np.diag(S)),
#                 y=mu,
#                 mode='markers+text',
#                 name='Individual Assets',
#                 text=mu.index,
#                 textposition="top center",
#                 marker=dict(color='black', size=8),
#             )
#         )
#     else:
#         # Convert valid points to arrays for plotting
#         rets = np.array([p['return'] for p in valid_points])
#         stds = np.array([p['volatility'] for p in valid_points])
#         sharpes = np.array([p['sharpe'] for p in valid_points])
        
#         # Create the plot
#         fig = go.Figure()
        
#         # Add efficient frontier line
#         fig.add_trace(
#             go.Scatter(
#                 x=stds,
#                 y=rets,
#                 mode='lines',
#                 name='Efficient Frontier',
#                 line=dict(color='blue', width=2)
#             )
#         )
        
#         # Add maximum Sharpe ratio point if we have valid sharpe ratios
#         if len(sharpes) > 0 and np.max(sharpes) > 0:
#             max_sharpe_idx = np.argmax(sharpes)
#             fig.add_trace(
#                 go.Scatter(
#                     x=[stds[max_sharpe_idx]],
#                     y=[rets[max_sharpe_idx]],
#                     mode='markers',
#                     name='Maximum Sharpe Ratio',
#                     marker=dict(color='red', size=12, symbol='star')
#                 )
#             )
        
#         # Add minimum volatility point
#         min_vol_idx = np.argmin(stds)
#         fig.add_trace(
#             go.Scatter(
#                 x=[stds[min_vol_idx]],
#                 y=[rets[min_vol_idx]],
#                 mode='markers',
#                 name='Minimum Volatility',
#                 marker=dict(color='green', size=12, symbol='diamond')
#             )
#         )
        
#         # Individual assets
#         fig.add_trace(
#             go.Scatter(
#                 x=np.sqrt(np.diag(S)),
#                 y=mu,
#                 mode='markers+text',
#                 name='Individual Assets',
#                 text=mu.index,
#                 textposition="top center",
#                 marker=dict(color='black', size=8),
#             )
#         )
    
#     # Update layout
#     fig.update_layout(
#         title='Efficient Frontier',
#         xaxis_title='Expected Volatility',
#         yaxis_title='Expected Return',
#         showlegend=True,
#         height=600,
#         template='plotly_white',
#         hovermode='closest'
#     )
    
#     # Format axes to show percentages
#     fig.update_layout(
#         xaxis=dict(tickformat='.1%'),
#         yaxis=dict(tickformat='.1%')
#     )
    
#     return fig

# def plot_efficient_frontier(optimizer):
#     """
#     Creates an interactive Plotly graph of the efficient frontier using EfficientFrontier
#     instead of CLA for better stability
    
#     Args:
#         optimizer: PortfolioOptimizer instance
    
#     Returns:
#         fig: Plotly figure object
#     """
#     import plotly.graph_objects as go
#     from pypfopt import EfficientFrontier
#     import numpy as np
    
#     # Get the efficient frontier data
#     mu = optimizer.expected_returns
#     S = optimizer.covariance_matrix
    
#     # Generate points along the efficient frontier
#     n_points = 50
#     returns = []
#     volatilities = []
    
#     # Calculate the range of target returns
#     min_ret = mu.min()
#     max_ret = mu.max()
#     target_returns = np.linspace(min_ret, max_ret, n_points)
    
#     # Calculate efficient frontier points using EfficientFrontier
#     for target_return in target_returns:
#         try:
#             # Initialize EfficientFrontier object
#             ef = EfficientFrontier(mu, S, weight_bounds=optimizer.weight_bounds)
            
#             # Find the optimal portfolio for the target return
#             weights = ef.efficient_return(target_return)
            
#             # Get portfolio performance
#             ret, vol, _ = ef.portfolio_performance()
#             returns.append(ret)
#             volatilities.append(vol)
#         except Exception as e:
#             continue
    
#     # Create the plot
#     fig = go.Figure()
    
#     # Add efficient frontier line if we have points
#     if returns and volatilities:
#         fig.add_trace(
#             go.Scatter(
#                 x=volatilities,
#                 y=returns,
#                 mode='lines',
#                 name='Efficient Frontier',
#                 line=dict(color='blue', width=2)
#             )
#         )
        
#         # Add minimum volatility portfolio
#         ef = EfficientFrontier(mu, S, weight_bounds=optimizer.weight_bounds)
#         weights = ef.min_volatility()
#         ret, vol, _ = ef.portfolio_performance()
        
#         fig.add_trace(
#             go.Scatter(
#                 x=[vol],
#                 y=[ret],
#                 mode='markers',
#                 name='Minimum Volatility',
#                 marker=dict(color='green', size=12, symbol='diamond')
#             )
#         )
        
#         # Add maximum Sharpe ratio portfolio
#         ef = EfficientFrontier(mu, S, weight_bounds=optimizer.weight_bounds)
#         weights = ef.max_sharpe()
#         ret, vol, _ = ef.portfolio_performance()
        
#         fig.add_trace(
#             go.Scatter(
#                 x=[vol],
#                 y=[ret],
#                 mode='markers',
#                 name='Maximum Sharpe Ratio',
#                 marker=dict(color='red', size=12, symbol='star')
#             )
#         )
    
#     # Add individual assets
#     fig.add_trace(
#         go.Scatter(
#             x=np.sqrt(np.diag(S)),
#             y=mu,
#             mode='markers+text',
#             name='Individual Assets',
#             text=mu.index,
#             textposition="top center",
#             marker=dict(color='black', size=8),
#         )
#     )
    
#     # Update layout
#     fig.update_layout(
#         title='Efficient Frontier',
#         xaxis_title='Expected Volatility',
#         yaxis_title='Expected Return',
#         showlegend=True,
#         height=600,
#         template='plotly_white',
#         hovermode='closest',
#         xaxis=dict(
#             tickformat='.1%',
#             range=[0, max(np.sqrt(np.diag(S))) * 1.2]  # Add some padding
#         ),
#         yaxis=dict(
#             tickformat='.1%',
#             range=[min(mu) * 1.2, max(mu) * 1.2]  # Add some padding
#         )
#     )
    
#     return fig



def plot_efficient_frontier_cla(prices_df):
    """
    Create an unconstrained efficient frontier plot using Critical Line Algorithm (CLA)
    
    Parameters:
    prices_df (pd.DataFrame): DataFrame of asset prices
    
    Returns:
    plotly.graph_objects.Figure: Interactive plot of the efficient frontier
    """
    # Calculate expected returns and covariance matrix
    mu = expected_returns.mean_historical_return(prices_df)
    S = risk_models.sample_cov(prices_df)
    
    # Initialize CLA object
    cla = CLA(mu, S)
    
    # Get efficient frontier points
    cla.max_sharpe()
    optimal_ret, optimal_risk, max_sharpe = cla.portfolio_performance()
    opt_weights = cla.weights
    
    # Calculate frontier values
    cla.efficient_frontier(points=50)
    mus, sigmas, weights = cla.frontier_values
    
    # Create figure
    fig = go.Figure()
    
    # Plot efficient frontier line
    hover_template = "Risk: %{x:.4f}<br>Return: %{y:.4f}<br>"
    for i, ticker in enumerate(prices_df.columns):
        hover_template += f"{ticker}: %{{customdata[{i}]:.2%}}<br>"
    
    # Add efficient frontier trace
    fig.add_trace(
        go.Scatter(
            x=sigmas,
            y=mus,
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='blue', width=2),
            customdata=weights,
            hovertemplate=hover_template + "<extra></extra>"
        )
    )
    
    # Add maximum Sharpe ratio point
    fig.add_trace(
        go.Scatter(
            x=[optimal_risk],
            y=[optimal_ret],
            mode='markers',
            name='Maximum Sharpe Ratio',
            marker=dict(
                symbol='star',
                size=15,
                color='red'
            ),
            hovertemplate=f"Risk: %{{x:.4f}}<br>Return: %{{y:.4f}}<br>Sharpe Ratio: {max_sharpe:.4f}<extra></extra>"
        )
    )
    
    # Add individual assets
    asset_returns = mu
    asset_risk = np.sqrt(np.diag(S))
    
    fig.add_trace(
        go.Scatter(
            x=asset_risk,
            y=asset_returns,
            mode='markers+text',
            name='Individual Assets',
            marker=dict(
                symbol='circle',
                size=10,
                color='black'
            ),
            text=prices_df.columns,
            textposition="top center",
            hovertemplate="Asset: %{text}<br>Risk: %{x:.4f}<br>Return: %{y:.4f}<extra></extra>"
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Efficient Frontier (Unconstrained - CLA)',
        xaxis_title='Volatility (Risk)',
        yaxis_title='Expected Return',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        hovermode='closest',
        height=600
    )
    
    return fig