from typing import Dict, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class FeeStatistics:
    """Statistics for fee analysis."""
    mean: float
    median: float
    std: float
    min: float
    max: float
    percentiles: Dict[str, float]


def calculate_fee_statistics(df: pd.DataFrame) -> Dict[str, FeeStatistics]:
    """Calculate comprehensive fee analysis."""
    stats = {}

    # Relative fee percentage analysis
    stats['relative_percentage'] = FeeStatistics(
        mean=df['relative_fees_percentage_mean'].mean(),
        median=df['relative_fees_percentage_median'].mean(),
        std=df['relative_fees_percentage_mean'].std(),
        min=df['relative_fees_percentage_mean'].min(),
        max=df['relative_fees_percentage_mean'].max(),
        percentiles={
            '25': df['relative_fees_percentage_mean'].quantile(0.25),
            '75': df['relative_fees_percentage_mean'].quantile(0.75),
            '95': df['relative_fees_percentage_mean'].quantile(0.95)
        }
    )

    # Absolute fee analysis
    stats['absolute_satoshis'] = FeeStatistics(
        mean=df['absolute_fees_satoshis_mean'].mean(),
        median=df['absolute_fees_satoshis_median'].mean(),
        std=df['absolute_fees_satoshis_mean'].std(),
        min=df['absolute_fees_satoshis_mean'].min(),
        max=df['absolute_fees_satoshis_mean'].max(),
        percentiles={
            '25': df['absolute_fees_satoshis_mean'].quantile(0.25),
            '75': df['absolute_fees_satoshis_mean'].quantile(0.75),
            '95': df['absolute_fees_satoshis_mean'].quantile(0.95)
        }
    )

    return stats


def calculate_time_based_statistics(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
    """Calculate analysis over different time periods."""
    return df.groupby(pd.Grouper(freq=freq)).agg({
        'relative_fees_percentage_mean': ['mean', 'std', 'count'],
        'absolute_fees_satoshis_mean': ['mean', 'std', 'count'],
        'total_liquidity': ['mean', 'std', 'min', 'max'],
        'total_unique_makers': ['mean', 'min', 'max']
    })


# aggregations.py
def compute_fee_ratios(df: pd.DataFrame, window_size: int = 1000) -> pd.DataFrame:
    """Compute smoothed fee type ratios."""
    df_smooth = pd.DataFrame(index=df.index)

    # Calculate fee ratios
    df_smooth['relative_ratio'] = (
            df['relative_fees_count'] /
            (df['relative_fees_count'] + df['absolute_fees_count'])
    )

    df_smooth['absolute_ratio'] = (
            df['absolute_fees_count'] /
            (df['relative_fees_count'] + df['absolute_fees_count'])
    )

    # Add smoothed versions
    for col in ['relative_ratio', 'absolute_ratio']:
        df_smooth[f'{col}_smooth'] = df_smooth[col].rolling(
            window=window_size, center=True).mean()

    return df_smooth


def compute_volume_metrics(df: pd.DataFrame, window_size: int = 1000) -> pd.DataFrame:
    """Compute volume-related metrics."""
    df_vol = pd.DataFrame(index=df.index)

    # Calculate total volume
    df_vol['total_volume'] = (
            df['relative_fees_count'] + df['absolute_fees_count']
    )

    # Calculate market share
    df_vol['relative_share'] = df['relative_fees_count'] / df_vol['total_volume']
    df_vol['absolute_share'] = df['absolute_fees_count'] / df_vol['total_volume']

    # Add smoothed versions
    metrics = ['total_volume', 'relative_share', 'absolute_share']
    for metric in metrics:
        df_vol[f'{metric}_smooth'] = df_vol[metric].rolling(
            window=window_size, center=True).mean()

    return df_vol


# metrics.py
def calculate_liquidity_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate liquidity-related metrics."""
    return {
        'avg_liquidity': df['total_liquidity'].mean(),
        'liquidity_per_maker': (
                df['total_liquidity'] / df['total_unique_makers']
        ).mean(),
        'liquidity_volatility': df['total_liquidity'].std() / df['total_liquidity'].mean(),
    }


def calculate_market_health_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate market health indicators."""
    return {
        'maker_stability': (
                df['total_unique_makers'].rolling(window=1000).std() /
                df['total_unique_makers'].rolling(window=1000).mean()
        ).mean(),
        'fee_stability': (
                df['relative_fees_percentage_mean'].rolling(window=1000).std() /
                df['relative_fees_percentage_mean'].rolling(window=1000).mean()
        ).mean(),
        'market_depth': (
                df['total_liquidity'] * df['total_unique_makers']
        ).mean(),
    }