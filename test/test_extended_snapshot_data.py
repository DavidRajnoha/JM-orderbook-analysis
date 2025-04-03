from decimal import Decimal
import pandas as pd
import json
from src.preprocessing.snapshot import (
    process_offers,
    compute_statistics,
    process_fidelity_bonds,
    load_and_process_snapshot,
    parse_cjfee
)


def test_very_small_relative_fees(extended_snapshot_data):
    """Test handling of very small relative fees (0.000003)."""
    offer_stats = process_offers(extended_snapshot_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    # Check if small fees are processed correctly
    relative_fees = computed_stats['relative_fees']['percentages']
    assert relative_fees['mean'] > 0
    assert relative_fees['mean'] < 0.01  # Should be much smaller than 1%

    # Verify specific small fee calculation
    small_fee_offer = next(
        offer for offer in extended_snapshot_data['offers']
        if offer['cjfee'] == "0.000003"
    )
    fee = parse_cjfee(small_fee_offer['cjfee'],
                      small_fee_offer['ordertype'],
                      small_fee_offer['minsize'])
    assert fee == float(Decimal("0.000003") * Decimal(str(small_fee_offer['minsize'])))


def test_large_maxsize_handling(extended_snapshot_data):
    """Test handling of very large maxsize values."""
    offer_stats = process_offers(extended_snapshot_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    # Verify large maxsize is processed correctly
    assert computed_stats['order_sizes']['max'] >= 5000000000  # 5B satoshis
    assert isinstance(computed_stats['order_sizes']['max'], (int, float))

    # Test total liquidity calculation with large values
    total_liquidity = computed_stats['total_liquidity']
    assert total_liquidity > 5000000000
    assert isinstance(total_liquidity, (int, float))


def test_fidelity_bond_scientific_notation(extended_snapshot_data):
    """Test handling of fidelity bond values in scientific notation."""
    # Process fidelity bonds
    fidelity_stats = process_fidelity_bonds(extended_snapshot_data['fidelitybonds'])

    # Check total calculation
    expected_total = sum(
        fb['bond_value'] for fb in extended_snapshot_data['fidelitybonds']
    )
    assert abs(fidelity_stats['total_bond_value'] - expected_total) < 0.0001

    # Test precision maintenance
    assert isinstance(fidelity_stats['total_bond_value'], float)
    assert fidelity_stats['total_bond_value'] > 0


def test_fee_range_validation(extended_snapshot_data):
    """Test handling of the full range of real cjfee values."""
    offer_stats = process_offers(extended_snapshot_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    rel_fees = computed_stats['relative_fees']

    # Check fee ratio bounds
    assert 0.000001 <= rel_fees['percentages']['mean'] <= 0.01
    assert rel_fees['count'] > 0

    # Verify fee calculations for each type
    for offer in extended_snapshot_data['offers']:
        if offer['ordertype'] == 'sw0reloffer':
            fee = parse_cjfee(offer['cjfee'], offer['ordertype'], offer['minsize'])
            assert isinstance(fee, float)
            assert fee > 0


def test_txfee_handling(basic_snapshot_data):
    """Test proper handling of txfee field."""
    # Modify a test case to include non-zero txfee
    basic_snapshot_data['offers'][0]['txfee'] = 1000

    offer_stats = process_offers(basic_snapshot_data['offers'])
    computed_stats = compute_statistics(offer_stats)

    # Verify txfee doesn't affect other calculations
    assert computed_stats['total_offers'] == len(basic_snapshot_data['offers'])
    assert computed_stats['total_liquidity'] > 0


def test_full_snapshot_processing(extended_snapshot_data, tmp_path):
    """Test complete snapshot processing with extended data."""
    # Save extended data to temporary file
    file_path = tmp_path / "extended_snapshot.json"
    with open(file_path, 'w') as f:
        json.dump(extended_snapshot_data, f)

    # Process snapshot
    timestamp = pd.Timestamp('2024-01-01 12:00:00')
    result = load_and_process_snapshot(str(file_path), timestamp)

    # Verify all components are processed correctly
    assert result['total_offers'] == len(extended_snapshot_data['offers'])
    assert result['total_liquidity'] > 0
    assert result['relative_fees']['count'] > 0
    assert result['fidelity_stats']['total_fidelity_bonds'] == len(extended_snapshot_data['fidelitybonds'])