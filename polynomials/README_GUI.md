# Polynomial Expression Solver with GUI

A Python-based polynomial expression solver featuring a graphical user interface with **full session history tracking and the ability to load previous polynomial versions**.

## What's New

✨ **Interactive Graphical Interface** - User-friendly GUI replacing the command-line prompts

📊 **Session History Panel** - View all operations performed in the current session with timestamps

⏮️ **History Navigation** - Load any previous polynomial version from your session history

📈 **Expression Information** - Instantly see degree, coefficients, and current expression

## Key Features

### Main Window Layout

**Left Panel: Session History**
- Chronological list of all polynomial states
- Each entry shows timestamp, operation, and resulting expression
- Click on any entry to view detailed information
- "Load Selected" button to restore any previous polynomial version
- "Clear History" button to start fresh

**Right Panel: Operations & Display**

1. **Current Expression Display**
   - Shows the active polynomial in simplified form
   - Real-time updates after each operation

2. **Expression Information**
   - Degree: The highest power of x
   - Coefficients: All coefficients in order

3. **Operations**
   - Enter a second polynomial expression
   - Choose operation: Add (+), Subtract (-), Multiply (*), or Divide (/)
   - Result automatically becomes the new current expression

4. **Operation Log**
   - Running log of actions performed
   - Shows timestamps for all changes
   - Displays history entry details when selected

## How to Use

### Running the Application

```bash
python polybot2.py
```

### Basic Workflow

1. **Enter Initial Expression**
   - Type a polynomial (e.g., `x^2 + 3x + 2`)
   - Click "Load Expression"

2. **Perform Operations**
   - Enter a second polynomial in the "Second Expression" field
   - Click one of the operation buttons (Add, Subtract, Multiply, Divide)
   - The result becomes your new current expression

3. **Access History**
   - View all previous states in the left history panel
   - Click any entry to see its details
   - Click "Load Selected" to revert to that version

4. **Continue Working**
   - Perform new operations from any loaded previous state
   - Create multiple branches of calculations

### Supported Polynomial Formats

- Power notation: `x^2`, `x^3`
- Implicit multiplication: `2x`, `3x^2` (equivalent to `2*x`, `3*x^2`)
- Negative terms: `-2x^2 - 3x + 1`
- Decimal coefficients: `2.5x^3 + 1.2x`
- Parentheses: `(x + 1)(x - 1)`
- Combined operations: `2x^3 + x(x - 1)`

## Examples

### Example 1: Quadratic Expansion

```
1. Load: x^2 + 2x + 1
2. Multiply by: x - 1
3. Result: x^3 + x^2 - x - 1
4. Load history → Multiply by: 2x
5. Result: 2x^3 + 2x^2 - 2x - 2
```

### Example 2: Polynomial Simplification

```
1. Load: 3x^2 + 2x + 5
2. Add: -x^2 - x + 3
3. Result: 2x^2 + x + 8
4. Load history entry 1
5. Subtract: x^2 + x - 2
6. Result: 2x^2 + x + 7
```

## Technical Details

### Class Structure

- **HistoryEntry**: Stores a polynomial snapshot with timestamp and operation description
- **Expression**: Enhanced polynomial solver with history tracking
  - `_add_to_history()`: Records current state
  - `get_history()`: Returns all history entries
  - `load_history_state(index)`: Restores a previous state

- **PolynomialGUI**: Tkinter-based graphical interface
  - Manages UI layout and user interactions
  - Handles expression loading and operations
  - Updates history display and operation log

### Polynomial Representation

Internally, polynomials are stored as dictionaries:
```python
{degree: coefficient, ...}
# Example: x^2 + 2x + 1 → {2: 1.0, 1: 2.0, 0: 1.0}
```

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- No external dependencies

## Features in Detail

### History Tracking
- Automatic recording of initial expression
- Timestamp for each operation
- Operation description (Add, Subtract, Multiply, Divide)
- Nondestructive access to previous states

### Smart UI Updates
- Real-time display refresh
- Automatic degree and coefficient calculation
- Operation log with newest entries first
- Synchronized history selection

### Mathematical Operations
- Polynomial addition and subtraction
- Polynomial multiplication with term expansion
- Polynomial division with quotient/remainder
- GCD computation for rational simplification
- Automatic coefficient normalization

## Tips & Tricks

1. **Explore Different Paths**: Load a previous version and try a different operation
2. **Chain Operations**: Use operation results directly rather than re-entering
3. **Verify Results**: Check degree and coefficients to validate polynomial expansion
4. **Clear When Needed**: Start fresh history for a new calculation sequence

## Future Enhancements

Possible additions:
- Polynomial factorization
- Root finding
- Graphing polynomial functions
- Export history as PDF report
- Save/load sessions to files

## License

Open source - Use freely for educational and personal projects.

## Author

Created for polynomial mathematics education and exploration.
