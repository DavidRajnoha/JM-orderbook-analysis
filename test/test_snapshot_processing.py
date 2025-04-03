import pytest
import json
import pandas as pd

# Import the functions to test
from src.preprocessing.snapshot import (
    process_offers,
    compute_statistics,
    load_and_process_snapshot
)


@pytest.fixture
def basic_snapshot_file(tmp_path, basic_snapshot_data):
    """Create a temporary snapshot file for testing."""
    file_path = tmp_path / "test_snapshot.json"
    with open(file_path, 'w') as f:
        json.dump(basic_snapshot_data, f)
    return str(file_path)


def test_load_and_process_snapshot(basic_snapshot_file):
    """Test complete snapshot processing pipeline."""
    timestamp = pd.Timestamp('2024-01-01 12:00:00')
    result = load_and_process_snapshot(basic_snapshot_file, timestamp)

    # Test basic structure and values
    assert result['timestamp'] == timestamp
    assert result['total_offers'] == 3
    assert result['total_liquidity'] == 2250000  # Sum of all maxsizes

    # Test fee analysis
    assert result['relative_fees_count'] == 2
    assert result['absolute_fees_count'] == 1
    assert 'relative_fees_satoshis_mean' in result
    assert 'absolute_fees_satoshis_mean' in result

    # Test maker and bond analysis
    assert result['total_unique_makers'] == 3
    assert result['total_fidelity_bonds'] == 2
    assert result['total_bond_value'] == 15000000


def test_fee_calculations(basic_snapshot_data):
    """Test fee calculations for both relative and absolute fees."""
    offer_stats = process_offers(basic_snapshot_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    # Check relative fees
    assert abs(computed_stats['relative_fees_percentage_mean'] - 0.0025) < 1e-6  # Average of 0.3% and 0.2%
    assert computed_stats['relative_fees_count'] == 2

    # Check absolute fees
    assert computed_stats['absolute_fees_satoshis_mean'] == 1500.0
    assert computed_stats['absolute_fees_count'] == 1


def test_order_size_statistics(basic_snapshot_data):
    """Test order size calculations."""
    offer_stats = process_offers(basic_snapshot_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    assert computed_stats['order_size_min'] == 50000  # Minimum minsize
    assert computed_stats['order_size_max'] == 1000000  # Maximum maxsize
    assert computed_stats['order_size_mean'] == 750000  # Average of maxsizes


def test_empty_snapshot():
    """Test handling of empty snapshot data."""
    empty_data = {"offers": [], "fidelitybonds": []}
    offer_stats = process_offers(empty_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    # Test all relevant fields are zero for empty data
    assert computed_stats['total_offers'] == 0
    assert computed_stats['total_liquidity'] == 0
    assert computed_stats['all_fees_count'] == 0
    assert computed_stats['relative_fees_count'] == 0
    assert computed_stats['absolute_fees_count'] == 0
    assert computed_stats['relative_fees_satoshis_mean'] == 0
    assert computed_stats['absolute_fees_satoshis_mean'] == 0
    assert computed_stats['order_size_mean'] == 0


def test_dataframe_compatibility(basic_snapshot_file):
    """Test if the output can be properly converted to a pandas DataFrame."""
    timestamp = pd.Timestamp('2024-01-01 12:00:00')
    result = load_and_process_snapshot(basic_snapshot_file, timestamp)

    # Try creating a DataFrame
    df = pd.DataFrame([result])

    # Check if all expected columns are present
    expected_columns = {
        'timestamp', 'total_offers', 'total_liquidity',
        'relative_fees_count', 'relative_fees_satoshis_mean',
        'absolute_fees_count', 'absolute_fees_satoshis_mean',
        'order_size_mean', 'order_size_median', 'order_size_min', 'order_size_max',
        'total_unique_makers', 'total_fidelity_bonds', 'total_bond_value'
    }

    assert all(col in df.columns for col in expected_columns)
    assert len(df) == 1
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp'])
