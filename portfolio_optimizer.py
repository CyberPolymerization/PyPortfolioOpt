from pypfopt import (
    EfficientFrontier,
    risk_models,
    expected_returns,
    objective_functions
)
import pandas as pd
import numpy as np

class PortfolioOptimizer:
    def __init__(self, prices_df, risk_model="Sample Covariance",
                 returns_model="Mean Historical Return", weight_bounds=(0, 1)):
        self.prices_df = prices_df
        self.risk_model = risk_model
        self.returns_model = returns_model
        self.weight_bounds = weight_bounds
        
        # Calculate expected returns and covariance matrix
        self.expected_returns = self._calculate_expected_returns()
        self.covariance_matrix = self._calculate_covariance_matrix()
        
    def _calculate_expected_returns(self):
        if self.returns_model == "Mean Historical Return":
            return expected_returns.mean_historical_return(self.prices_df)
        elif self.returns_model == "CAPM Return":
            return expected_returns.capm_return(self.prices_df)
        else:  # EMA Historical Return
            return expected_returns.ema_historical_return(self.prices_df)
            
    def _calculate_covariance_matrix(self):
        if self.risk_model == "Sample Covariance":
            return risk_models.sample_cov(self.prices_df)
        elif self.risk_model == "Ledoit-Wolf Shrinkage":
            return risk_models.CovarianceShrinkage(self.prices_df).ledoit_wolf()
        else:  # Semi Covariance
            return risk_models.semicovariance(self.prices_df)
            
    def get_correlation_matrix(self):
        """
        Get the correlation matrix from the covariance matrix
        """
        return risk_models.cov_to_corr(self.covariance_matrix)
        
    def get_expected_returns(self):
        """
        Get expected returns as a pandas Series
        """
        return pd.DataFrame(
            self.expected_returns,
            columns=['Expected Return']
        ).sort_values('Expected Return', ascending=True)  # Sort for better visualization
        
    def optimize_maximum_sharpe(self):
        ef = EfficientFrontier(
            self.expected_returns,
            self.covariance_matrix,
            weight_bounds=self.weight_bounds
        )
        ef.add_objective(objective_functions.L2_reg, gamma=0.1)
        weights = ef.max_sharpe()
        return pd.Series(weights)
        
    def optimize_minimum_volatility(self):
        ef = EfficientFrontier(
            self.expected_returns,
            self.covariance_matrix,
            weight_bounds=self.weight_bounds
        )
        weights = ef.min_volatility()
        return pd.Series(weights)
        
    def optimize_efficient_return(self, target_return):
        ef = EfficientFrontier(
            self.expected_returns,
            self.covariance_matrix,
            weight_bounds=self.weight_bounds
        )
        weights = ef.efficient_return(target_return)
        return pd.Series(weights)
        
    def optimize_efficient_risk(self, target_risk):
        ef = EfficientFrontier(
            self.expected_returns,
            self.covariance_matrix,
            weight_bounds=self.weight_bounds
        )
        weights = ef.efficient_risk(target_risk)
        return pd.Series(weights)
        
    def get_portfolio_performance(self, weights):
        ef = EfficientFrontier(
            self.expected_returns,
            self.covariance_matrix,
            weight_bounds=self.weight_bounds
        )
        ef.set_weights(weights)
        return ef.portfolio_performance() 