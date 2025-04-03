import pytest
import pandas as pd
import numpy as np
from src.visualisations.fees import (
    plot_fee_metrics,
    plot_fee_type_distribution,
    plot_fee_volume_metrics
)


@pytest.fixture
def sample_df():
    """Create sample DataFrame for testing."""
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='H')
    np.random.seed(42)

    return pd.DataFrame({
        'relative_fees_percentage_mean': np.random.uniform(0.001, 0.01, len(dates)),
        'relative_fees_satoshis_mean': np.random.uniform(1000, 2000, len(dates)),
        'absolute_fees_satoshis_mean': np.random.uniform(500, 1500, len(dates)),
        'relative_fees_ratio': np.random.uniform(0.4, 0.6, len(dates)),
        'absolute_fees_ratio': np.random.uniform(0.4, 0.6, len(dates)),
        'relative_fees_count': np.random.randint(10, 20, len(dates)),
        'absolute_fees_count': np.random.randint(5, 15, len(dates))
    }, index=dates)


def test_plot_fee_metrics(sample_df):
    """Test fee metrics plotting function."""
    fig, axes = plot_fee_metrics(sample_df, window_size=24)
    assert len(axes) == 2


def test_plot_fee_type_distribution(sample_df):
    """Test fee type distribution plotting function."""
    fig, ax = plot_fee_type_distribution(sample_df, window_size=24)
    assert ax.get_ylabel() == 'Ratio'


def test_plot_fee_volume_metrics(sample_df):
    """Test fee volume metrics plotting function."""
    fig, ax = plot_fee_volume_metrics(sample_df, window_size=24)
    assert ax.get_ylabel() == 'Number of Offers'
