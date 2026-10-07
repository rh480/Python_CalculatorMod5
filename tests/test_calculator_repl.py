
############################
# Calculator REPL Tests #
############################

from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

#Help 

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

##history 

@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
@patch('app.calculator.Calculator.load_history')
def test_calculator_repl_history_empty(mock_load_history, mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("No calculations in history")



@patch('builtins.input', side_effect=['add', '2', '3', 'history', 'exit'])
@patch('builtins.print')
def test_calculator_repl_history_with_calculation(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nCalculation History:")

##clear

@patch('builtins.input', side_effect=['clear', 'exit'])
@patch('builtins.print')
def test_calculator_repl_clear(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("History cleared")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")

##Undo

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_undo_empty(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Nothing to undo")

@patch('builtins.input', side_effect=['add', '2', '3', 'undo','exit'])
@patch('builtins.print')
def test_calculator_repl_undo(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Operation undone")

##Redo 

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_calculator_repl_redo_empty(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Nothing to redo")

@patch('builtins.input', side_effect=[
    'add', '2', '3',
    'undo',
    'redo',
    'exit'
])
@patch('builtins.print')
def test_calculator_repl_redo(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Operation redone")

#Save

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
def test_calculator_repl_save(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save:
        calculator_repl()
        mock_save.assert_called()
        mock_print.assert_any_call("History saved successfully")


@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
@patch('app.calculator.Calculator.save_history')
def test_calculator_repl_save_error(mock_save, mock_print, mock_input):
    mock_save.side_effect = OperationError("Save failed")
    calculator_repl()
    mock_print.assert_any_call("Error saving history: Save failed")

#Load

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_calculator_repl_load(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history') as mock_load:
        calculator_repl()
        mock_load.assert_called()
        mock_print.assert_any_call("History loaded successfully")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
@patch('app.calculator.Calculator.load_history')
def test_calculator_repl_load_error(mock_load, mock_print, mock_input):
    mock_load.side_effect = OperationError("Load failed")
    calculator_repl()
    mock_print.assert_any_call("Error loading history: Load failed")


#Cancel

@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_first_number(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")


@patch('builtins.input', side_effect=['add', '2', 'cancel', 'exit'])
@patch('builtins.print')
def test_calculator_repl_cancel_second_number(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

#Error Handling

@patch(
    'builtins.input',
    side_effect=['divide', '5', '0', 'exit']
)
@patch('builtins.print')
def test_calculator_repl_operation_error(mock_print, mock_input):
    calculator_repl()
    assert any(
        call.args[0].startswith("Error:")
        for call in mock_print.call_args_list
    )

@patch('builtins.input', side_effect=['apple', 'exit'])
@patch('builtins.print')
def test_calculator_repl_unknown_command(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call(
        "Unknown command: 'apple'. Type 'help' for available commands."
    )

@patch('builtins.input')
@patch('builtins.print')
def test_calculator_repl_keyboard_interrupt(mock_print, mock_input):
    mock_input.side_effect = [KeyboardInterrupt, 'exit']
    calculator_repl()
    mock_print.assert_any_call("\nOperation cancelled")


@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_calculator_repl_eof(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")

##Exception Handling

#initialization error
@patch('app.calculator_repl.Calculator')
@patch('app.calculator_repl.logging.error')
@patch('builtins.print')
def test_calculator_repl_initialization_error(
    mock_print,
    mock_logging_error,
    mock_calculator
):
    mock_calculator.side_effect = Exception("Initialization failed")

    with pytest.raises(Exception, match="Initialization failed"):
        calculator_repl()

    mock_print.assert_any_call("Fatal error: Initialization failed")
    mock_logging_error.assert_called_once_with(
        "Fatal error in calculator REPL: Initialization failed"
    )

@patch('builtins.input')
@patch('builtins.print')
def test_calculator_repl_general_error(mock_print, mock_input):
    mock_input.side_effect = [Exception("Unexpected failure"), 'exit']

    calculator_repl()

    mock_print.assert_any_call("Error: Unexpected failure")


@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
@patch('app.calculator.Calculator.perform_operation')
def test_calculator_repl_unexpected_operation_error(
    mock_perform_operation,
    mock_print,
    mock_input
):
    mock_perform_operation.side_effect = Exception("Unexpected failure")

    calculator_repl()

    mock_print.assert_any_call("Unexpected error: Unexpected failure")
