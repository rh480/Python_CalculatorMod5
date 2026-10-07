import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError
import logging


#Parameterized tests for different operations
@pytest.mark.parametrize("operation, operand1, operand2, expected", [
    ("Addition", Decimal("2"), Decimal("3"), Decimal("5")),
    ("Subtraction", Decimal("5"), Decimal("3"), Decimal("2")),
    ("Multiplication", Decimal("4"), Decimal("2"), Decimal("8")),
    ("Division", Decimal("8"), Decimal("2"), Decimal("4")),
    ("Power", Decimal("2"), Decimal("3"), Decimal("8")),
    ("Root", Decimal("16"), Decimal("2"), Decimal("4")),
])
def test_calculation_operations(operation, operand1, operand2, expected):
    calc = Calculation(
        operation=operation,
        operand1=operand1,
        operand2=operand2
    )

    assert calc.result == expected


def test_division_by_zero():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("0"))


def test_negative_power():
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("-3"))



def test_invalid_root():
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation(operation="Root", operand1=Decimal("-16"), operand2=Decimal("2"))


def test_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation(operation="Unknown", operand1=Decimal("5"), operand2=Decimal("3"))


def test_to_dict():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }


def test_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == "Addition"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")


def test_invalid_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


def test_format_result():
    calc = Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"


def test_equality():
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc1 == calc2
    assert calc1 != calc3

def test_equality_with_non_calculation():
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))

    assert calc1 == calc2
    assert calc1 != calc3
    assert calc1 != "not a calculation"



# New Test to Cover Logging Warning
def test_from_dict_result_mismatch(caplog):
    """
    Test the from_dict method to ensure it logs a warning when the saved result
    does not match the computed result.
    """
    # Arrange
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "10",  # Incorrect result to trigger logging.warning
        "timestamp": datetime.now().isoformat()
    }

    # Act
    with caplog.at_level(logging.WARNING):
        calc = Calculation.from_dict(data)

    # Assert
    assert "Loaded calculation result 10 differs from computed result 5" in caplog.text


def test_str():
    calc = Calculation(
        operation="Addition",
        operand1=Decimal("2"),
        operand2=Decimal("3")
    )

    assert str(calc) == "Addition(2, 3) = 5"

def test_repr():
    calc = Calculation(
        operation="Addition",
        operand1=Decimal("2"),
        operand2=Decimal("3")
    )

    result = repr(calc)

    assert "Calculation(operation='Addition'" in result
    assert "operand1=2" in result
    assert "operand2=3" in result
    assert "result=5" in result



def test_calculation_error():
    calc = Calculation.__new__(Calculation)

    calc.operation = "Addition"

    class ErrorValue:
        def __add__(self, other):
            raise ArithmeticError("Test arithmetic error")

    calc.operand1 = ErrorValue()
    calc.operand2 = Decimal("3")

    with pytest.raises(OperationError, match="Calculation failed: Test arithmetic error"):
        calc.calculate()
