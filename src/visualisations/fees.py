import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple


def plot_fee_metrics(df: pd.DataFrame, window_size: int = 1000) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot fee-related metrics over time.

    Args:
        df: DataFrame containing fee metrics
        window_size: Size of the rolling window for smoothing

    Returns:
        fig, ax: Figure and Axes objects
    """
    # Calculate smoothed metrics
    df_smooth = pd.DataFrame(index=df.index)
    metrics = [
        'relative_fees_percentage_mean',
        'relative_fees_satoshis_mean',
        'absolute_fees_satoshis_mean'
    ]

    for metric in metrics:
        df_smooth[f'{metric}_smooth'] = df[metric].rolling(
            window=window_size, center=True).mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

    # Plot relative fee percentages
    ax1.plot(df_smooth.index,
             df_smooth['relative_fees_percentage_mean_smooth'],
             label='Relative Fee %')
    ax1.set_title('Average Relative Fee Percentage Over Time')
    ax1.set_ylabel('Fee Percentage')
    ax1.legend()

    # Plot fee comparison in satoshis
    ax2.plot(df_smooth.index,
             df_smooth['relative_fees_satoshis_mean_smooth'],
             label='Relative Fees (sats)')
    ax2.plot(df_smooth.index,
             df_smooth['absolute_fees_satoshis_mean_smooth'],
             label='Absolute Fees (sats)')
    ax2.set_title('Fee Comparison in Satoshis')
    ax2.set_ylabel('Satoshis')
    ax2.legend()

    plt.tight_layout()
    return fig, (ax1, ax2)


def plot_fee_type_distribution(df: pd.DataFrame, window_size: int = 1000) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot the distribution of fee types over time.

    Args:
        df: DataFrame containing fee metrics
        window_size: Size of the rolling window for smoothing

    Returns:
        fig, ax: Figure and Axes objects
    """
    # Calculate smoothed ratios
    df_smooth = pd.DataFrame(index=df.index)
    df_smooth['relative_ratio_smooth'] = df['relative_fees_ratio'].rolling(
        window=window_size, center=True).mean()
    df_smooth['absolute_ratio_smooth'] = df['absolute_fees_ratio'].rolling(
        window=window_size, center=True).mean()

    fig, ax = plt.subplots(figsize=(12, 6))

    # Create stacked area plot
    ax.fill_between(df_smooth.index, df_smooth['relative_ratio_smooth'],
                    label='Relative Fee Offers', alpha=0.5)
    ax.fill_between(df_smooth.index, df_smooth['absolute_ratio_smooth'],
                    label='Absolute Fee Offers', alpha=0.5)

    ax.set_title('Fee Type Distribution Over Time')
    ax.set_ylabel('Ratio')
    ax.legend()

    return fig, ax


def plot_fee_volume_metrics(df: pd.DataFrame, window_size: int = 1000) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot fee counts and volumes over time.

    Args:
        df: DataFrame containing fee metrics
        window_size: Size of the rolling window for smoothing

    Returns:
        fig, ax: Figure and Axes objects
    """
    # Calculate smoothed metrics
    df_smooth = pd.DataFrame(index=df.index)
    count_metrics = ['relative_fees_count', 'absolute_fees_count']

    for metric in count_metrics:
        df_smooth[f'{metric}_smooth'] = df[metric].rolling(
            window=window_size, center=True).mean()

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot fee counts
    ax.plot(df_smooth.index, df_smooth['relative_fees_count_smooth'],
            label='Relative Fee Offers')
    ax.plot(df_smooth.index, df_smooth['absolute_fees_count_smooth'],
            label='Absolute Fee Offers')

    ax.set_title('Number of Fee Offers Over Time')
    ax.set_ylabel('Number of Offers')
    ax.legend()

    return fig, ax