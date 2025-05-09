from Bot_App.core import order_utils

def test_generate_order_id_consistency():
    sample_order = {
        "enteredTime": "2024-01-01T00:00:00Z",
        "orderLegCollection": [
            {"instruction": "BUY_TO_OPEN", "instrument": {"symbol": "AAPL 01/01/2025 $200 Call"}}
        ]
    }
    id1 = order_utils.generate_order_id(sample_order)
    id2 = order_utils.generate_order_id(sample_order)
    assert id1 == id2
    assert isinstance(id1, str)


def test_parse_option_description():
    desc = "AAPL 01/01/2025 $200 Call"
    assert order_utils.parse_option_description(desc, 2) == "01/01/2025"
    assert order_utils.parse_option_description(desc, 3) == "200"
    assert order_utils.parse_option_description(desc, 4) == "Call"