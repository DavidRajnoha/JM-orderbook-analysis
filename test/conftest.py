import pytest
import json
from pathlib import Path

@pytest.fixture
def basic_snapshot_data():
    """Basic test data for simple cases."""
    return {
        "offers": [
            {
                "counterparty": "J5EobsvrvAvdTTrP",
                "oid": 0,
                "ordertype": "sw0reloffer",
                "minsize": 191725,
                "maxsize": 14436090,
                "txfee": 0,
                "cjfee": "0.000009",
                "fidelity_bond_value": 0
            },
            {
                "counterparty": "J5FNKhn7mbAUcpiV",
                "oid": 0,
                "ordertype": "sw0absoffer",
                "minsize": 99320,
                "maxsize": 2066014,
                "txfee": 0,
                "cjfee": "1500",
                "fidelity_bond_value": 0
            }
        ],
        "fidelitybonds": []
    }

@pytest.fixture
def extended_snapshot_data():
    """Extended test data matching real-world scenarios."""
    return {
        "offers": [
            # Very small relative fee
            {
                "counterparty": "J59tpHyZ5Xn9C9nX",
                "oid": 0,
                "ordertype": "sw0reloffer",
                "minsize": 104012,
                "maxsize": 172068478,
                "txfee": 0,
                "cjfee": "0.000003",
                "fidelity_bond_value": 0
            },
            # Large relative fee
            {
                "counterparty": "J59Z1yYxFb7Hq9gv",
                "oid": 0,
                "ordertype": "sw0reloffer",
                "minsize": 300000,
                "maxsize": 27952209,
                "txfee": 0,
                "cjfee": "0.01",
                "fidelity_bond_value": 0
            },
            # Very large maxsize
            {
                "counterparty": "J55SJJZ1aHyunkvQ",
                "oid": 0,
                "ordertype": "sw0reloffer",
                "minsize": 456201,
                "maxsize": 5009008748,
                "txfee": 0,
                "cjfee": "0.000046",
                "fidelity_bond_value": 30326145734.23268
            }
        ],
        "fidelitybonds": [
            {
                "counterparty": "J5A4EA12SMfMETQZ",
                "utxo": {
                    "txid": "b654a5db1211416cb5112b79159c0ed9834d1df4ffd603dd486ee64adcf3b1d8",
                    "vout": 0
                },
                "bond_value": 366922375.52727914,
                "locktime": 1780272000,
                "amount": 125000000,
                "script": "0020d6cf2e98f2e532b3517cf9015191d770b4fba31cdf289c32dbd210e51bb23df3",
                "utxo_confirmations": 16547,
                "utxo_confirmation_timestamp": 1716064811,
                "utxo_pub": "03a95889d4d36481625b9a744f337b4ff18d634e2a9b64894eb5ad0072c85e6dbf",
                "cert_expiry": 427
            },
            {
                "counterparty": "J52fRtcXrcwBuzDN",
                "utxo": {
                    "txid": "66e195a664cc687927abfccc4222292721a7918c735988983a498b7ca2af2485",
                    "vout": 0
                },
                "bond_value": 358365.68579071196,
                "locktime": 1756684800,
                "amount": 928190,
                "script": "00201e077fdd620b6676938c3ae08e55f4187da35d902a0660898bb3527302ac90df",
                "utxo_confirmations": 18799,
                "utxo_confirmation_timestamp": 1714652800,
                "utxo_pub": "0386429c2c9b224231803ae23754873f8c9528000a632c481296efc814cfa8a0fa",
                "cert_expiry": 427
            }
        ]
    }