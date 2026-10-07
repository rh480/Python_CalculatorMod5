############################
# Calculator Memento Tests #
############################

import datetime
from decimal import Decimal
from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def test_memento_to_dict():
    """
    Test that a CalculatorMemento can be converted to a dictionary.

    """

    timestamp = datetime.datetime.now()

    calculation = Calculation(
        operation="Addition",
        operand1=Decimal("2"), 
        operand2=Decimal("3"))
    
    memento = CalculatorMemento(history=[calculation], timestamp=timestamp)

    memento_dict = memento.to_dict()

    assert memento_dict['timestamp'] == timestamp.isoformat()
    assert len(memento_dict['history']) == 1

    calc_dict = memento_dict['history'][0]
    
    assert calc_dict['operation'] == "Addition"
    assert calc_dict['operand1'] == "2"
    assert calc_dict['operand2'] == "3"
    assert calc_dict['result'] == "5"

def test_memento_from_dict():
    """
    Test that a CalculatorMemento can be recreated from a dictionary.
    
    """

    timestamp = datetime.datetime.now().isoformat()

    data = {
        "history": [
            {
                "operation": "Addition",
                "operand1": "2",
                "operand2": "3",
                "result": "5",
                "timestamp": timestamp
            }
        ],
        "timestamp": timestamp
    }

    memento = CalculatorMemento.from_dict(data)

    assert len(memento.history) == 1

    calculation = memento.history[0]

    assert calculation.operation == "Addition"
    assert calculation.operand1 == Decimal("2")
    assert calculation.operand2 == Decimal("3")
    assert calculation.result == Decimal("5")

    assert memento.timestamp == datetime.datetime.fromisoformat(timestamp)