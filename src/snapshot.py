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
    Processes the list of offers to extract relevant statistics.

    Parameters:
        offers (List[Dict[str, Any]]): A list of offer dictionaries.

    Returns:
        Dict[str, Any]: A dictionary containing aggregated statistics.
    """
    total_liquidity = 0
    fees = []
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

        # Count fee types
        fee_types[ordertype] += 1

        # Track unique makers
        unique_makers.add(counterparty)

    # Compile statistics
    stats = {
        'total_offers': len(offers),
        'total_liquidity': total_liquidity,
        'fees': fees,
        'order_sizes': order_sizes,
        'fee_types': fee_types,
        'min_order_sizes': min_order_sizes,
        'max_order_sizes': max_order_sizes,
        'unique_makers': unique_makers,
    }

    return stats


def compute_statistics(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes statistical measures from the processed offer data.

    Parameters:
        stats (Dict[str, Any]): The aggregated statistics from process_offers.

    Returns:
        Dict[str, Any]: A dictionary containing computed statistical measures.
    """
    fees = stats['fees']
    order_sizes = stats['order_sizes']
    min_order_sizes = stats['min_order_sizes']
    max_order_sizes = stats['max_order_sizes']
    fee_types = stats['fee_types']
    unique_makers = stats['unique_makers']

    computed_stats = {
        'total_offers': stats['total_offers'],
        'total_liquidity': stats['total_liquidity'],
        'average_fee': mean(fees) if fees else 0,
        'median_fee': median(fees) if fees else 0,
        'average_order_size': mean(order_sizes) if order_sizes else 0,
        'median_order_size': median(order_sizes) if order_sizes else 0,
        'min_order_size': min(min_order_sizes) if min_order_sizes else 0,
        'max_order_size': max(max_order_sizes) if max_order_sizes else 0,
        'fee_types_distribution': dict(fee_types),
        'total_unique_makers': len(unique_makers),
    }

    return computed_stats


def process_fidelity_bonds(fidelitybonds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Processes fidelity bonds to extract relevant statistics.

    Parameters:
        fidelitybonds (List[Dict[str, Any]]): A list of fidelity bond dictionaries.

    Returns:
        Dict[str, Any]: A dictionary containing aggregated fidelity bond statistics.
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
        Dict[str, Any]: Computed statistics for the snapshot, including timestamp.
    """
    data = load_data(filepath)
    offers = data.get('offers', [])
    fidelitybonds = data.get('fidelitybonds', [])

    # Process offers and fidelity bonds
    offer_stats_raw = process_offers(offers)
    fidelity_stats = process_fidelity_bonds(fidelitybonds)

    # Compute statistics
    offer_stats = compute_statistics(offer_stats_raw)

    # Combine offer stats and fidelity bond stats
    snapshot_stats = {
        'timestamp': timestamp,
        'total_offers': offer_stats['total_offers'],
        'total_liquidity': offer_stats['total_liquidity'],
        'average_fee': offer_stats['average_fee'],
        'median_fee': offer_stats['median_fee'],
        'average_order_size': offer_stats['average_order_size'],
        'median_order_size': offer_stats['median_order_size'],
        'min_order_size': offer_stats['min_order_size'],
        'max_order_size': offer_stats['max_order_size'],
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