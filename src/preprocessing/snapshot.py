import json
from collections import defaultdict
from statistics import mean, median

import pandas as pd
from typing import List, Dict, Any


def load_data(filepath: str) -> Dict[str, Any]:
    """
    Loads JSON data from a given file path.

    Parameters:
        filepath (str): The path to the JSON file.

    Returns:
        Dict[str, Any]: The parsed JSON data as a dictionary.
    """
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def process_offers(offers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Processes the list of offers to extract relevant analysis.

    Parameters:
        offers (List[Dict[str, Any]]): A list of offer dictionaries.

    Returns:
        Dict[str, Any]: A dictionary containing aggregated analysis.
    """
    total_liquidity = 0
    fees = []
    relative_fees_satoshis = []
    relative_fees_ratios = []
    absolute_fees = []
    order_sizes = []
    fee_types = defaultdict(int)
    min_order_sizes = []
    max_order_sizes = []
    unique_makers = set()

    for offer in offers:
        minsize = offer.get('minsize', 0)
        maxsize = offer.get('maxsize', 0)
        ordertype = offer.get('ordertype', '')
        cjfee = offer.get('cjfee', '0')
        counterparty = offer.get('counterparty', '')
        fidelity_bond_value = offer.get('fidelity_bond_value', 0)

        # Update total liquidity
        total_liquidity += maxsize

        # Store order sizes
        order_sizes.append(maxsize)
        min_order_sizes.append(minsize)
        max_order_sizes.append(maxsize)

        # Calculate fee for a nominal amount (e.g., minsize)
        nominal_amount = minsize if minsize > 0 else 100000  # Default nominal amount
        fee = parse_cjfee(cjfee, ordertype, nominal_amount)
        fees.append(fee)

        if ordertype == 'sw0reloffer':
            try:
                ratio = float(cjfee)
                fee_satoshis = ratio * nominal_amount
                relative_fees_ratios.append(ratio)
                relative_fees_satoshis.append(fee_satoshis)
            except (ValueError, TypeError):
                pass
        elif ordertype == 'sw0absoffer':
            try:
                fee = float(cjfee)
                absolute_fees.append(fee)
            except (ValueError, TypeError):
                pass

        # Count fee types
        fee_types[ordertype] += 1

        # Track unique makers
        unique_makers.add(counterparty)

    # Compile analysis
    stats = {
        'total_offers': len(offers),
        'total_liquidity': total_liquidity,
        'fees': fees,
        'order_sizes': order_sizes,
        'fee_types': fee_types,
        'relative_fees_satoshis': relative_fees_satoshis,
        'relative_fees_ratios': relative_fees_ratios,
        'absolute_fees': absolute_fees,
        'min_order_sizes': min_order_sizes,
        'max_order_sizes': max_order_sizes,
        'unique_makers': unique_makers,
    }

    return stats


def compute_statistics(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes statistical measures from the processed offer data.

    Parameters:
        stats (Dict[str, Any]): The aggregated analysis from process_offers.

    Returns:
        Dict[str, Any]: A dictionary containing computed statistical measures.
    """
    order_sizes = stats['order_sizes']
    min_order_sizes = stats['min_order_sizes']
    max_order_sizes = stats['max_order_sizes']
    fee_types = stats['fee_types']
    unique_makers = stats['unique_makers']

    # Fee calculations
    relative_fees_satoshis = stats['relative_fees_satoshis']
    relative_fees_ratios = stats['relative_fees_ratios']
    absolute_fees = stats['absolute_fees']
    all_fees = stats['fees']  # Combined fees in satoshis

    # Calculate fee type ratios
    total_fee_offers = sum(fee_types.values())
    fee_ratios = {
        fee_type: count / total_fee_offers if total_fee_offers > 0 else 0
        for fee_type, count in fee_types.items()
    }

    computed_stats = {
        'total_offers': stats['total_offers'],
        'total_liquidity': stats['total_liquidity'],

        # Combined fee analysis (in satoshis)
        'all_fees': {
            'mean': mean(all_fees) if all_fees else 0,
            'median': median(all_fees) if all_fees else 0,
            'count': len(all_fees),
        },

        # Relative fee analysis
        'relative_fees': {
            'count': fee_types.get('sw0reloffer', 0),
            'ratio': fee_ratios.get('sw0reloffer', 0),
            'satoshis': {
                'mean': mean(relative_fees_satoshis) if relative_fees_satoshis else 0,
                'median': median(relative_fees_satoshis) if relative_fees_satoshis else 0,
            },
            'percentages': {
                'mean': mean(relative_fees_ratios) if relative_fees_ratios else 0,
                'median': median(relative_fees_ratios) if relative_fees_ratios else 0,
            }
        },

        # Absolute fee analysis
        'absolute_fees': {
            'count': fee_types.get('sw0absoffer', 0),
            'ratio': fee_ratios.get('sw0absoffer', 0),
            'satoshis': {
                'mean': mean(absolute_fees) if absolute_fees else 0,
                'median': median(absolute_fees) if absolute_fees else 0,
            }
        },

        # Order size analysis
        'order_sizes': {
            'mean': mean(order_sizes) if order_sizes else 0,
            'median': median(order_sizes) if order_sizes else 0,
            'min': min(min_order_sizes) if min_order_sizes else 0,
            'max': max(max_order_sizes) if max_order_sizes else 0,
        },

        'total_unique_makers': len(unique_makers),
        'fee_types_distribution': dict(fee_types),
    }

    return computed_stats


def process_fidelity_bonds(fidelitybonds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Processes fidelity bonds to extract relevant analysis.

    Parameters:
        fidelitybonds (List[Dict[str, Any]]): A list of fidelity bond dictionaries.

    Returns:
        Dict[str, Any]: A dictionary containing aggregated fidelity bond analysis.
    """
    total_fidelity_bonds = len(fidelitybonds)
    total_bond_value = sum(fb.get('bond_value', 0) for fb in fidelitybonds)

    return {
        'total_fidelity_bonds': total_fidelity_bonds,
        'total_bond_value': total_bond_value,
    }


def load_and_process_snapshot(filepath: str, timestamp: pd.Timestamp) -> Dict[str, Any]:
    """
    Loads and processes a single snapshot file.

    Parameters:
        filepath (str): Path to the snapshot file.
        timestamp (pd.Timestamp): Timestamp of the snapshot.

    Returns:
        Dict[str, Any]: Flattened analysis for the snapshot, suitable for pandas DataFrame.
    """
    data = load_data(filepath)
    offers = data.get('offers', [])
    fidelitybonds = data.get('fidelitybonds', [])

    # Process offers and fidelity bonds
    offer_stats_raw = process_offers(offers)
    fidelity_stats = process_fidelity_bonds(fidelitybonds)

    # Compute analysis
    offer_stats = compute_statistics(offer_stats_raw)

    # Create flattened snapshot stats
    snapshot_stats = {
        'timestamp': timestamp,
        'total_offers': offer_stats['total_offers'],
        'total_liquidity': offer_stats['total_liquidity'],

        # All fees (combined)
        'all_fees_mean': offer_stats['all_fees']['mean'],
        'all_fees_median': offer_stats['all_fees']['median'],
        'all_fees_count': offer_stats['all_fees']['count'],

        # Relative fees
        'relative_fees_count': offer_stats['relative_fees']['count'],
        'relative_fees_ratio': offer_stats['relative_fees']['ratio'],
        'relative_fees_satoshis_mean': offer_stats['relative_fees']['satoshis']['mean'],
        'relative_fees_satoshis_median': offer_stats['relative_fees']['satoshis']['median'],
        'relative_fees_percentage_mean': offer_stats['relative_fees']['percentages']['mean'],
        'relative_fees_percentage_median': offer_stats['relative_fees']['percentages']['median'],

        # Absolute fees
        'absolute_fees_count': offer_stats['absolute_fees']['count'],
        'absolute_fees_ratio': offer_stats['absolute_fees']['ratio'],
        'absolute_fees_satoshis_mean': offer_stats['absolute_fees']['satoshis']['mean'],
        'absolute_fees_satoshis_median': offer_stats['absolute_fees']['satoshis']['median'],

        # Order sizes
        'order_size_mean': offer_stats['order_sizes']['mean'],
        'order_size_median': offer_stats['order_sizes']['median'],
        'order_size_min': offer_stats['order_sizes']['min'],
        'order_size_max': offer_stats['order_sizes']['max'],

        # Makers and bonds
        'total_unique_makers': offer_stats['total_unique_makers'],
        'total_fidelity_bonds': fidelity_stats['total_fidelity_bonds'],
        'total_bond_value': fidelity_stats['total_bond_value'],
    }

    return snapshot_stats


def parse_cjfee(cjfee: Any, ordertype: str, amount: int) -> float:
    """
    Parses the 'cjfee' field and calculates the fee based on the order type.

    Parameters:
        cjfee (Any): The coinjoin fee, which can be a string or a number.
        ordertype (str): The type of order ('sw0reloffer' or 'sw0absoffer').
        amount (int): The nominal amount to calculate the fee against.

    Returns:
        float: The calculated fee in satoshis.
    """
    try:
        if ordertype == 'sw0reloffer':
            # Relative fee, cjfee is a percentage in decimal form
            fee = float(cjfee) * amount
        elif ordertype == 'sw0absoffer':
            # Absolute fee, cjfee is in satoshis
            fee = float(cjfee)
        else:
            fee = 0
        return fee
    except (ValueError, TypeError):
        # Handle cases where cjfee is malformed
        return 0
