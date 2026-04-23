# Polynomial Expression Solver GUI - Usage Guide

## Features

### 1. **Load Expression**
   - Enter a polynomial expression in the text field (e.g., `3x^2 + 2x + 1`)
   - Click "Load Expression" to initialize the solver
   - The expression will appear in the "Current Expression" display

### 2. **View Expression Information**
   - **Degree**: Shows the highest power of x in the polynomial
   - **Coefficients**: Displays all coefficients in order (from constant to highest degree)

### 3. **Perform Operations**
   - Enter a second polynomial expression
   - Choose an operation:
     - **Add (+)**: Combines two polynomials
     - **Subtract (-)**: Finds the difference between polynomials
     - **Multiply (*)**: Multiplies polynomials together
     - **Divide (/)**: Divides one polynomial by another
   - The result becomes the new current expression

### 4. **Session History**
   - The left panel shows a complete history of all operations performed
   - Each entry displays:
     - Timestamp when the operation was performed
     - Operation name (e.g., "Added", "Multiplied")
     - The resulting expression
   - History entries are logged in chronological order

### 5. **Load Previous Versions**
   - Click on any history entry to view its details
   - Details show: timestamp, operation performed, and the expression at that point
   - Click "Load Selected" to restore that version as your current expression
   - This allows you to go back in time and branch off into new operations

### 6. **Clear History**
   - Click "Clear History" to remove all session records
   - Useful for starting a new calculation sequence

## Supported Polynomial Formats

- Simple polynomials: `x^2 + 2x + 1`
- Implicit multiplication: `2x` instead of `2*x`
- Negative coefficients: `-3x^2 - 5`
- Decimal values: `2.5x^3 + 1.2`
- Complex expressions: `(x + 1)*(x - 1)` = `x^2 - 1`

## Example Workflow

1. Load: `x^2 + 3x + 2`
2. Add: `x + 1` → Results in `x^2 + 4x + 3`
3. Multiply: `x - 1` → Results in `x^3 + 3x^2 - x - 3`
4. Load history to go back to step 1
5. Try a different operation from step 1

## Running the Application

```bash
python polybot2.py
```

A graphical window will open with all features ready to use.
