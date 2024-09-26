import pytest
from decimal import Decimal, getcontext

class Rebalance:
    def __init__(self, current_holdings, desired_holdings):
        self.current_holdings = current_holdings
        self.desired_holdings = desired_holdings

    def solution(self):
        self.__validate()
        return self.__solve()

    def __validate(self):
        current_total = sum(self.current_holdings.values())
        desired_total = sum(self.desired_holdings.values())
        if current_total != desired_total:
            raise ValueError("Inputs and Outputs must equate")

    def __solve(self):
        desired_holdings = self.desired_holdings
        current_holdings = self.current_holdings
        moves = {}
        
        for stock in desired_holdings:
            if stock in current_holdings:
                diff = desired_holdings[stock] - current_holdings[stock]
                if diff != 0:
                    moves[stock] = diff
            else:
                moves[stock] = desired_holdings[stock]
        
        for stock in current_holdings:
            if stock not in desired_holdings:
                moves[stock] = -current_holdings[stock]
        
        # Create return value
        i=0
        move={}
        results = []
        for stock, diff in moves.items():
            if i == 0:
                move['to_stock'] = stock
                move['to_value'] = diff
                i = i + 1
            else:
                move['from_stock'] = stock
                move['from_value'] = -diff
                i=0

        result = {"from": move['from_stock'] , "to": move['to_stock'], "amount": move['to_value']}
        results.append(result)
        return results



#########
# Tests #
#########

def test_it_validates_the_input_values_equate_to_the_output_values():
    current_holdings = {"WMT": 30}
    desired_holdings = {"TSLA": 24}

    with pytest.raises(ValueError, match="Inputs and Outputs must equate"):
        Rebalance(current_holdings, desired_holdings).solution()


def test_it_generates_exchanges_for_simple_cases():
    current_holdings = {"WMT": 24}
    desired_holdings = {"TSLA": 24}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    expected = [{"from": "WMT", "to": "TSLA", "amount": 24}]
    assert exchanges == expected


def test_it_generates_exchanges_for_more_complex_cases():
    current_holdings = {"WMT": 10, "TSLA": 20}
    desired_holdings = {"WMT": 20, "TSLA": 10}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    exchanges = sanitize_exchanges(exchanges)

    expected = sanitize_exchanges([{"from": "TSLA", "to": "WMT", "amount": 10}])

    assert exchanges == expected


def test_it_creates_exchanges_for_new_ids():
    current_holdings = {"WMT": 10, "TSLA": 10}
    desired_holdings = {"WMT": 8, "TSLA": 8, "MSFT": 4}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    exchanges = sanitize_exchanges(exchanges)

    expected = sanitize_exchanges([
        {"from": "WMT", "to": "MSFT", "amount": 2},
        {"from": "TSLA", "to": "MSFT", "amount": 2}
    ])

    assert expected == exchanges


def test_it_handles_precision():
    getcontext().prec = 16

    current_holdings = {"WMT": 3.2, "TSLA": 2.1}
    desired_holdings = {"WMT": 5, "TSLA": 0.3}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    exchanges = sanitize_exchanges(exchanges)

    expected = sanitize_exchanges([
        {"from": "TSLA", "to": "WMT", "amount": Decimal("1.8")}
    ])

    assert expected == exchanges


def test_it_handles_a_bunch_of_elements():
    current_holdings = {"WMT": 3.2, "TSLA": 2.1, "MSFT": 3.9, "AAPL": 2.8}
    desired_holdings = {"WMT": 5.0, "TSLA": 2.4, "MSFT": 2.7, "AAPL": 1.9}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    exchanges = sanitize_exchanges(exchanges)

    expected = sanitize_exchanges([
        {"from": "MSFT", "to": "WMT", "amount": 1.2},
        {"from": "AAPL", "to": "TSLA", "amount": 0.3},
        {"from": "AAPL", "to": "WMT", "amount": 0.6},
    ])

    assert expected == exchanges


def test_it_works_multiple_times():
    current_holdings = {"WMT": 3.2, "TSLA": 2.1, "MSFT": 3.9, "AAPL": 2.8}
    desired_holdings = {"WMT": 5.0, "TSLA": 2.4, "MSFT": 2.7, "AAPL": 1.9}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    exchanges = sanitize_exchanges(exchanges)

    expected = sanitize_exchanges([
        {"from": "MSFT", "to": "WMT", "amount": 1.2},
        {"from": "AAPL", "to": "TSLA", "amount": 0.3},
        {"from": "AAPL", "to": "WMT", "amount": 0.6},
    ])

    assert expected == exchanges

    rebalancer = Rebalance(current_holdings, desired_holdings)
    exchanges = sanitize_exchanges(rebalancer.solution())
    assert expected == exchanges

    # works out when called a second time on the same instance too
    exchanges = sanitize_exchanges(rebalancer.solution())
    assert expected == exchanges

#######################
# Helper test methods #
#######################


def sanitize_exchanges(exchanges):
    return sorted(exchanges, key=lambda x: x["from"] + "-" + x["to"])


if __name__ == "__main__":
    current_holdings = {"WMT": 10, "TSLA": 20}
    desired_holdings = {"WMT": 20, "TSLA": 10}

    exchanges = Rebalance(current_holdings, desired_holdings).solution()
    exchanges = sanitize_exchanges(exchanges)

    expected = sanitize_exchanges([{"from": "TSLA", "to": "WMT", "amount": 10}])

    assert exchanges == expected
