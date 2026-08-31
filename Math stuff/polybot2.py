import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# We import tools that help us do things:
# re lets us look for patterns in text, tkinter makes windows, and datetime gives us the current time.

class HistoryEntry:
  """This keeps a little bookmark for one moment in time."""
  def __init__(self, expression, poly, operation=None, timestamp=None):
    # expression is the string the user typed in or the result we made
    self.expression = expression
    # poly is the internal math structure for the expression
    self.poly = poly
    # operation is the name of what we did to get here
    self.operation = operation
    # timestamp is the clock time when this step happened
    self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")

class Expression:
  # This pattern checks if one piece of text looks like a valid polynomial term.
  # It allows numbers like 3, 2.5 and variables like x, x^2, xy.
  _term_pattern = re.compile(r'^[+-]?(?:(?:\d*\.?\d*[a-z](?:\^\d+)?)+|\d*\.?\d+)$')

  def __init__(self, expression=None, prompt=True, gui=None):
    # If no expression was given, ask the person to type one.
    if expression is None:
      expression = input('Enter the expression: \n>')

    # Save the raw text expression and GUI object.
    self.expression = expression
    self.gui = gui
    # History list remembers each step so we can look back later.
    self.history = []
    self.history_index = -1

    # Break the input string into separate terms like '3x' and '+2'.
    self.terms = self.break_up_input(expression)
    # Combined expressions have *, /, or parentheses and need a different path.
    self.combined = any(op in self.expression for op in '*/()')

    if not self.combined:
      # If the expression is a plain polynomial, check it and store it.
      self.validate()
      poly = {}
      for term in self.terms:
        # See if this term has letters like x or y.
        has_vars = any(c.isalpha() for c in term)
        if has_vars:
          coeff, var_powers = Expression.parse_term_multivar(term)
          # Use a frozenset of variable-power pairs as a key in our dictionary.
          var_key = frozenset(var_powers.items())
        else:
          # If there are no variables, this is a constant number.
          coeff = float(term)
          var_key = frozenset()
        
        # Add the coefficient to the right place in the polynomial.
        if var_key in poly:
          poly[var_key] += coeff
        else:
          poly[var_key] = coeff
      self.poly = poly
    else:
      # If the expression has *, /, or parentheses, evaluate it more carefully.
      try:
        result = Expression.evaluate_expression(self.expression)
        if isinstance(result, dict):
          self.poly = result
          self.expression = Expression.poly_to_expr(result)
          self.terms = self.break_up_input(self.expression)
          self.combined = any(op in self.expression for op in '*/()')
        else:
          self.poly = None
      except:
        self.poly = None
    
    # Save the first state so we can show it in history.
    self._add_to_history("Initial expression")

    if prompt:
      # If this is a command-line run, ask the user what to do next.
      self.get_next_step()

  def _add_to_history(self, operation):
    """Add current expression state to history"""
    entry = HistoryEntry(self.expression, self.poly.copy() if self.poly else None, operation)
    self.history.append(entry)
    self.history_index = len(self.history) - 1
    if self.gui:
      self.gui.update_history()
      if operation != "Initial expression":  # Only log actual operations, not initial load
        self.gui.log_message(operation)

  def get_history(self):
    """Return list of all history entries"""
    return self.history

  def load_history_state(self, index):
    """Load a previous state from history"""
    if 0 <= index < len(self.history):
      entry = self.history[index]
      self.expression = entry.expression
      self.poly = entry.poly.copy() if entry.poly else None
      self.history_index = index
      self.terms = self.break_up_input(self.expression)
      self.combined = any(op in self.expression for op in '*/()')
      return True
    return False

  @staticmethod
  def parse_term_multivar(term):
    """Parse a term like '3x^2y' into coefficient and {variable: power} dict"""
    # Start reading the text from the beginning and pull out the number.
    i = 0
    coeff_str = ''
    while i < len(term) and (term[i].isdigit() or term[i] == '.' or (i == 0 and term[i] == '-')):
      coeff_str += term[i]
      i += 1
    
    # If there was no number, the coefficient is 1 or -1.
    if coeff_str == '' or coeff_str == '-':
      coeff = 1.0 if coeff_str == '' else -1.0
    else:
      coeff = float(coeff_str)
    
    # Read variables like x, y and their powers like ^2.
    var_powers = {}
    while i < len(term):
      if term[i].isalpha():
        var = term[i]
        i += 1
        power = 1
        if i < len(term) and term[i] == '^':
          i += 1
          power_str = ''
          while i < len(term) and term[i].isdigit():
            power_str += term[i]
            i += 1
          power = int(power_str)
        # If the same variable appears twice, add up the powers.
        var_powers[var] = var_powers.get(var, 0) + power
      else:
        i += 1
    
    return coeff, var_powers


  @staticmethod
  def normalize_poly(poly):
    # Remove terms that are basically zero to keep the polynomial clean.
    return {d: c for d, c in poly.items() if abs(c) > 1e-10}

  @staticmethod
  def add_polys(poly1, poly2):
    # Add two polynomial dictionaries term by term.
    new_poly = poly1.copy()
    for d, c in poly2.items():
      new_poly[d] = new_poly.get(d, 0) + c
    return Expression.normalize_poly(new_poly)

  @staticmethod
  def sub_polys(poly1, poly2):
    # Subtract the second polynomial from the first.
    new_poly = poly1.copy()
    for d, c in poly2.items():
      new_poly[d] = new_poly.get(d, 0) - c
    return Expression.normalize_poly(new_poly)

  @staticmethod
  def mul_polys(poly1, poly2):
    # Multiply each term in poly1 by each term in poly2.
    new_poly = {}
    for d1, c1 in poly1.items():
      for d2, c2 in poly2.items():
        # Start with the powers from the first term.
        var_dict = dict(d1)
        # Add the powers from the second term.
        for var, power in d2:
          var_dict[var] = var_dict.get(var, 0) + power
        d = frozenset(var_dict.items())
        # Multiply the numbers and add to the result term.
        new_poly[d] = new_poly.get(d, 0) + c1 * c2
    return Expression.normalize_poly(new_poly)

  @staticmethod
  def div_polys(poly1, poly2):
    # Divide poly1 by poly2 using polynomial long division.
    if not poly2:
      raise ValueError("Division by zero")
    quotient = {}
    remainder = poly1.copy()
    while remainder:
      if not remainder:
        break
      # Find the biggest term in remainder and divisor by total power sum.
      deg_r = max(remainder.keys(), key=lambda k: sum(p for v, p in k))
      deg_d = max(poly2.keys(), key=lambda k: sum(p for v, p in k))
      
      deg_r_sum = sum(p for v, p in deg_r)
      deg_d_sum = sum(p for v, p in deg_d)
      
      # If remainder is smaller than divisor, we are done.
      if deg_r_sum < deg_d_sum:
        break
      
      coeff_r = remainder[deg_r]
      coeff_d = poly2[deg_d]
      q_coeff = coeff_r / coeff_d
      
      # Subtract powers to get the quotient term.
      q_dict = dict(deg_r)
      for var, power in deg_d:
        q_dict[var] = q_dict.get(var, 0) - power
        if q_dict[var] == 0:
          del q_dict[var]
      q_deg = frozenset(q_dict.items())
      
      quotient[q_deg] = q_coeff
      
      # Subtract the divisor times quotient term from the remainder.
      for d, c in poly2.items():
        q_dict2 = dict(q_deg)
        for var, power in d:
          q_dict2[var] = q_dict2.get(var, 0) + power
        deg = frozenset(q_dict2.items())
        coeff = q_coeff * c
        if deg in remainder:
          remainder[deg] -= coeff
          if abs(remainder[deg]) < 1e-10:
            del remainder[deg]
        else:
          remainder[deg] = -coeff
          if abs(remainder[deg]) < 1e-10:
            del remainder[deg]
    
    return Expression.normalize_poly(quotient), Expression.normalize_poly(remainder)

  @staticmethod
  def gcd_polys(a, b):
    # Find the greatest common divisor of two polynomials.
    while b:
      q, r = Expression.div_polys(a, b)
      a, b = b, r
    return a

  @staticmethod
  def evaluate_expression(expr):
    # Remove spaces and turn the expression into tokens.
    expr = expr.replace(' ', '')
    tokens = Expression.tokenize(expr)
    pos = [0]  # a mutable index so nested functions can move it.
    poly = Expression.parse_expression(tokens, pos)
    if pos[0] != len(tokens):
      raise ValueError("Extra tokens in expression")
    return poly

  @staticmethod
  def tokenize(expr):
    # Turn a string into a list of numbers, variables, and operators.
    tokens = []
    i = 0
    while i < len(expr):
      if expr[i].isdigit() or (expr[i] == '-' and (i == 0 or expr[i-1] in '+-*/(')) or (expr[i] == '.' and i+1 < len(expr) and expr[i+1].isdigit()):
        num = ''
        if expr[i] == '-':
          num += '-'
          i += 1
        while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
          num += expr[i]
          i += 1
        tokens.append(('NUM', float(num) if '.' in num else int(num)))
        # If a number is followed by a letter or parentheses, insert an implicit multiplication.
        if i < len(expr) and expr[i] in '0123456789.abcdefghijklmnopqrstuvwxyz(':
          tokens.append(('OP', '*'))
      elif expr[i].isalpha():  # Any letter is a variable
        tokens.append(('VAR', expr[i]))
        i += 1
        # If a variable is followed by a number, another variable, or parentheses, add implicit multiplication.
        if i < len(expr) and expr[i] in '0123456789.abcdefghijklmnopqrstuvwxyz(':
          tokens.append(('OP', '*'))
      elif expr[i] in '+-*/^()':
        tokens.append(('OP', expr[i]))
        i += 1
        # After a closing parenthesis, if another term starts, multiply implicitly.
        if expr[i-1] == ')' and i < len(expr) and expr[i] in '0123456789.abcdefghijklmnopqrstuvwxyz(':
          tokens.append(('OP', '*'))
      elif expr[i] == ' ':
        i += 1
      else:
        raise ValueError(f"Invalid character '{expr[i]}' in expression")
    return tokens

  @staticmethod
  def parse_expression(tokens, pos):
    # Parse plus and minus at the top level.
    result = Expression.parse_term(tokens, pos)
    while pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] in '+-':
      op = tokens[pos[0]][1]
      pos[0] += 1
      right = Expression.parse_term(tokens, pos)
      if op == '+':
        result = Expression.add_polys(result, right)
      else:
        result = Expression.sub_polys(result, right)
    return result

  @staticmethod
  def parse_term(tokens, pos):
    # Parse multiplication and division before addition/subtraction.
    result = Expression.parse_factor(tokens, pos)
    while pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] in '*/':
      op = tokens[pos[0]][1]
      pos[0] += 1
      right = Expression.parse_factor(tokens, pos)
      if op == '*':
        result = Expression.mul_polys(result, right)
      else:
        q, r = Expression.div_polys(result, right)
        if not r:
          result = q
        else:
          raise ValueError("Non-exact division")
    return result

  @staticmethod
  def parse_factor(tokens, pos):
    # Parse a single number, variable, power, or parenthesized group.
    if tokens[pos[0]][0] == 'NUM':
      num = tokens[pos[0]][1]
      pos[0] += 1
      return {frozenset(): float(num)}
    elif tokens[pos[0]][0] == 'VAR':
      var = tokens[pos[0]][1]
      pos[0] += 1
      power = 1
      if pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == '^':
        pos[0] += 1
        if tokens[pos[0]][0] == 'NUM':
          power = int(tokens[pos[0]][1])
          pos[0] += 1
        else:
          raise ValueError("Expected number after ^")
      return {frozenset([(var, power)]): 1.0}
    elif tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == '(':
      pos[0] += 1
      result = Expression.parse_expression(tokens, pos)
      if pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == ')':
        pos[0] += 1
      else:
        raise ValueError("Expected )")
      return result
    else:
      raise ValueError("Invalid factor")

  def break_up_input(self, input_string):
    # Take the typed expression and split it into pieces like [+3x, -2y, +5].
    cleaned = input_string.replace(' ', '').replace('(', '').replace(')', '')
    terms = [term for term in re.split(r'(?=[+-])', cleaned) if term]
    return terms
    
  def validate(self):
    # Make sure each term looks like a polynomial term.
    for term in self.terms:
      if not Expression._term_pattern.match(term):
        raise ValueError(f"Invalid term '{term}' in expression '{self.expression}'. Expression must be a valid polynomial (e.g., 3x + 2, x^2 - 1).")
    
  def get_poly(self):
    # Return the internal polynomial structure if available.
    if self.poly is not None:
      return self.poly
    else:
      raise ValueError("Coefficients cannot be extracted from combined expressions.")
  
  @staticmethod
  def poly_to_expr(poly):
    # Turn the internal polynomial dictionary back into a nice string.
    terms = []
    
    # Find every variable used in the polynomial so we can sort things consistently.
    all_vars = set()
    for var_key in poly.keys():
      for var, _ in var_key:
        all_vars.add(var)
    var_list = sorted(all_vars)  # Sort vars alphabetically: a, b, c, ...
    
    # Sort terms by total degree and then by variable order.
    def sort_key(var_key):
      var_dict = dict(var_key)
      total_degree = sum(var_dict.values())
      power_vector = tuple(-(var_dict.get(v, 0)) for v in var_list)
      return (-total_degree, power_vector)
    
    sorted_keys = sorted(poly.keys(), key=sort_key)
    
    for var_key in sorted_keys:
      c = poly[var_key]
      if abs(c) < 1e-10:
        continue
      # If the coefficient is basically an integer, make it an integer.
      if abs(c - round(c)) < 1e-10:
        c = int(round(c))
      
      if not var_key:  # Constant term with no variables.
        terms.append(str(c))
      else:
        var_key_sorted = sorted(var_key)
        x_part = ''
        for var, power in var_key_sorted:
          if power == 1:
            x_part += var
          else:
            x_part += f'{var}^{power}'
        
        if c == 1:
          terms.append(x_part)
        elif c == -1:
          terms.append('-' + x_part)
        else:
          terms.append(f'{c}{x_part}')
    
    if not terms:
      return '0'
    expr = terms[0]
    for t in terms[1:]:
      if t.startswith('-'):
        expr += t
      else:
        expr += '+' + t
    return expr
  
  def get_degree(self):
    # Degree is the biggest power sum among all terms.
    poly = self.get_poly()
    if poly:
      max_degree = max(sum(p for v, p in term) for term in poly.keys())
      return max_degree
    else:
      return 0
  
  def get_coefficients(self):
    try:
      poly = self.get_poly()
      # Build a list of readable term descriptions.
      terms_list = []
      sorted_keys = sorted(poly.keys(), key=lambda k: (-sum(p for v, p in k), sorted(k)))
      for key in sorted_keys:
        coeff = poly[key]
        if not key:
          term_str = f"Constant: {coeff}"
        else:
          var_str = '*'.join(f"{v}^{p}" if p > 1 else v for v, p in sorted(key))
          term_str = f"{coeff} * {var_str}"
        terms_list.append(term_str)
      return terms_list if terms_list else ["0"]
    except ValueError:
      print("Coefficients cannot be extracted from combined expressions.")
      return []
  def __add__(self, other):
    # Add two Expression objects.
    if isinstance(other, Expression):
      if self.poly is not None and other.poly is not None:
        combined_poly = Expression.add_polys(self.poly, other.poly)
        new_expression = Expression.poly_to_expr(combined_poly)
      else:
        combined_expr = f'({self.expression})+({other.expression})'
        try:
          combined_poly = Expression.evaluate_expression(combined_expr)
          new_expression = Expression.poly_to_expr(combined_poly)
        except:
          new_expression = combined_expr
      result = Expression(new_expression, prompt=False, gui=self.gui)
      result._add_to_history(f"Added: ({self.expression}) + ({other.expression})")
      return result
    else:
      raise ValueError("Can only add another Expression object.")

  def __sub__(self, other):
    # Subtract one Expression from another.
    if isinstance(other, Expression):
      if self.poly is not None and other.poly is not None:
        combined_poly = Expression.sub_polys(self.poly, other.poly)
        new_expression = Expression.poly_to_expr(combined_poly)
      else:
        combined_expr = f'({self.expression})-({other.expression})'
        try:
          combined_poly = Expression.evaluate_expression(combined_expr)
          new_expression = Expression.poly_to_expr(combined_poly)
        except:
          new_expression = combined_expr
      result = Expression(new_expression, prompt=False, gui=self.gui)
      result._add_to_history(f"Subtracted: ({self.expression}) - ({other.expression})")
      return result
    else:
      raise ValueError("Can only subtract another Expression object.")

  def __mul__(self, other):
    # Multiply two Expression objects.
    if isinstance(other, Expression):
      if self.poly is not None and other.poly is not None:
        combined_poly = Expression.mul_polys(self.poly, other.poly)
        new_expression = Expression.poly_to_expr(combined_poly)
      else:
        combined_expr = f'({self.expression})*({other.expression})'
        try:
          combined_poly = Expression.evaluate_expression(combined_expr)
          new_expression = Expression.poly_to_expr(combined_poly)
        except:
          new_expression = combined_expr
      result = Expression(new_expression, prompt=False, gui=self.gui)
      result._add_to_history(f"Multiplied: ({self.expression}) * ({other.expression})")
      return result
    else:
      raise ValueError("Can only multiply by another Expression object.")

  def __truediv__(self, other):
    # Divide one Expression by another.
    if isinstance(other, Expression):
      if self.poly is not None and other.poly is not None:
        quotient, remainder = Expression.div_polys(self.poly, other.poly)
        if not remainder:
          new_expression = Expression.poly_to_expr(quotient)
        else:
          gcd = Expression.gcd_polys(self.poly, other.poly)
          if gcd and any(abs(c) > 1e-10 for c in gcd.values()) and gcd != {0: 1.0}:
            q_num, r_num = Expression.div_polys(self.poly, gcd)
            q_den, r_den = Expression.div_polys(other.poly, gcd)
            if not r_num and not r_den:
              num_expr = Expression.poly_to_expr(q_num) if q_num else '0'
              den_expr = Expression.poly_to_expr(q_den) if q_den else '1'
              new_expression = f"({num_expr})/({den_expr})"
            else:
              new_expression = f'({self.expression})/({other.expression})'
          else:
            new_expression = f'({self.expression})/({other.expression})'
      else:
        combined_expr = f'({self.expression})/({other.expression})'
        try:
          combined_poly = Expression.evaluate_expression(combined_expr)
          new_expression = Expression.poly_to_expr(combined_poly)
        except:
          new_expression = combined_expr
      result = Expression(new_expression, prompt=False, gui=self.gui)
      result._add_to_history(f"Divided: ({self.expression}) / ({other.expression})")
      return result
    else:
      raise ValueError("Can only divide by another Expression object.")
  def get_next_step(self):
    # Skip command-line questions if the GUI is showing instead.
    if self.gui:
      return
    
    while True:
      choice = input('What would you like to do next? (1: Combine with another expression, 2: Get coefficients, 3: Get degree, 4: Show current expression, 5: Exit)\n>')
      if choice == '1':
        sub_choice = input('Choose operation: (1: Add, 2: Subtract, 3: Multiply, 4: Divide)\n>')
        new_expression_input = input('Enter the new expression: \n>')
        new_expr = Expression(new_expression_input, prompt=False)
        if sub_choice == '1':
          combined = self + new_expr
        elif sub_choice == '2':
          combined = self - new_expr
        elif sub_choice == '3':
          combined = self * new_expr
        elif sub_choice == '4':
          combined = self / new_expr
        else:
          print('Invalid operation choice. Please try again.')
          continue
        # Replace current expression with the new result.
        self.expression = combined.expression
        self.terms = combined.terms
        self.poly = combined.poly
        self.combined = combined.combined
        print(f'New combined expression: {self.expression}')
      elif choice == '2':
        coeffs = self.get_coefficients()
        print(f'The coefficients of the expression are: {coeffs}')
      elif choice == '3':
        deg = self.get_degree()
        print(f'The degree of the expression is {deg}')
      elif choice == '4':
        print(f'Current expression: {self.expression}')
      elif choice == '5':
        print('Exiting...')
        break
      else:
        print('Invalid choice. Please try again.')
        continue



class PolynomialGUI:
  """The window and buttons that let people use the polynomial tool."""
  
  def __init__(self, root):
    # Save the window object and set up the window.
    self.root = root
    self.root.title("Polynomial Expression Solver")
    self.root.geometry("1000x700")
    self.expression = None
    self.setup_ui()
  
  def setup_ui(self):
    """Build the window layout with boxes, buttons, and text areas."""
    # Top frame for input
    input_frame = ttk.LabelFrame(self.root, text="Enter Polynomial Expression")
    input_frame.pack(fill=tk.X, padx=10, pady=10)
    
    ttk.Label(input_frame, text="Expression:").pack(side=tk.LEFT, padx=5)
    self.input_var = tk.StringVar()
    input_field = ttk.Entry(input_frame, textvariable=self.input_var, width=50)
    input_field.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    ttk.Button(input_frame, text="Load Expression", command=self.load_expression).pack(side=tk.LEFT, padx=5)
    
    # Main content area with a split view for history and results.
    paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Left panel - history list.
    history_frame = ttk.LabelFrame(paned, text="Session History", width=250)
    paned.add(history_frame, weight=1)
    
    self.history_listbox = tk.Listbox(history_frame, height=20)
    self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)
    
    history_button_frame = ttk.Frame(history_frame)
    history_button_frame.pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(history_button_frame, text="Load Selected", command=self.load_selected_history).pack(side=tk.LEFT, padx=2)
    ttk.Button(history_button_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=2)
    
    # Right panel - show current expression and let user do operations.
    right_frame = ttk.Frame(paned, width=500)
    paned.add(right_frame, weight=2)
    
    expr_frame = ttk.LabelFrame(right_frame, text="Current Expression")
    expr_frame.pack(fill=tk.X, padx=5, pady=5)
    self.expr_display = tk.Text(expr_frame, height=3, width=60, wrap=tk.WORD)
    self.expr_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    self.expr_display.config(state=tk.DISABLED)
    
    info_frame = ttk.LabelFrame(right_frame, text="Expression Info")
    info_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(info_frame, text="Degree:").pack(side=tk.LEFT, padx=5)
    self.degree_var = tk.StringVar(value="N/A")
    ttk.Label(info_frame, textvariable=self.degree_var).pack(side=tk.LEFT, padx=5)
    
    ttk.Label(info_frame, text="Terms:").pack(side=tk.LEFT, padx=5)
    self.coeff_frame = ttk.Frame(info_frame)
    self.coeff_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
    self.coeff_var = tk.StringVar(value="N/A")
    self.coeff_label = ttk.Label(self.coeff_frame, textvariable=self.coeff_var, wraplength=300, justify=tk.LEFT)
    self.coeff_label.pack()
    
    ops_frame = ttk.LabelFrame(right_frame, text="Operations")
    ops_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    ttk.Label(ops_frame, text="Second Expression:").pack(padx=5, pady=5)
    self.second_expr_var = tk.StringVar()
    ttk.Entry(ops_frame, textvariable=self.second_expr_var, width=50).pack(padx=5, pady=5, fill=tk.X)
    
    button_frame = ttk.Frame(ops_frame)
    button_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Button(button_frame, text="Add (+)", command=lambda: self.perform_operation('add')).pack(side=tk.LEFT, padx=2)
    ttk.Button(button_frame, text="Subtract (-)", command=lambda: self.perform_operation('sub')).pack(side=tk.LEFT, padx=2)
    ttk.Button(button_frame, text="Multiply (*)", command=lambda: self.perform_operation('mul')).pack(side=tk.LEFT, padx=2)
    ttk.Button(button_frame, text="Divide (/)", command=lambda: self.perform_operation('div')).pack(side=tk.LEFT, padx=2)
    
    log_frame = ttk.LabelFrame(right_frame, text="Operation Log")
    log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    self.log_text = tk.Text(log_frame, height=8, width=60, wrap=tk.WORD)
    self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    self.log_text.config(state=tk.DISABLED)
  
  def load_expression(self):
    """Load the expression from the input box and show it."""
    expr_str = self.input_var.get().strip()
    if not expr_str:
      messagebox.showerror("Error", "Please enter a polynomial expression")
      return
    
    try:
      self.expression = Expression(expr_str, prompt=False, gui=self)
      self.update_display()
      self.log_message(f"Loaded expression: {expr_str}")
    except Exception as e:
      messagebox.showerror("Error", f"Invalid expression: {str(e)}")
  
  def perform_operation(self, operation):
    """Do add, subtract, multiply, or divide with the second expression."""
    if self.expression is None:
      messagebox.showerror("Error", "Please load an expression first")
      return
    
    second_expr_str = self.second_expr_var.get().strip()
    if not second_expr_str:
      messagebox.showerror("Error", "Please enter a second expression")
      return
    
    try:
      second_expr = Expression(second_expr_str, prompt=False, gui=self)
      
      if operation == 'add':
        result = self.expression + second_expr
      elif operation == 'sub':
        result = self.expression - second_expr
      elif operation == 'mul':
        result = self.expression * second_expr
      elif operation == 'div':
        result = self.expression / second_expr
      else:
        return
      
      self.expression = result
      self.update_display()
      self.second_expr_var.set("")
    except Exception as e:
      messagebox.showerror("Error", f"Operation failed: {str(e)}")
  
  def update_display(self):
    """Refresh the text boxes to show the current expression and info."""
    if self.expression is None:
      return
    
    # Show the expression string in the read-only text box.
    self.expr_display.config(state=tk.NORMAL)
    self.expr_display.delete(1.0, tk.END)
    self.expr_display.insert(1.0, self.expression.expression)
    self.expr_display.config(state=tk.DISABLED)
    
    # Show the degree of the polynomial if we can.
    try:
      degree = self.expression.get_degree()
      self.degree_var.set(str(degree))
    except:
      self.degree_var.set("N/A")
    
    # Show the coefficient terms as a readable list.
    try:
      coeffs = self.expression.get_coefficients()
      if isinstance(coeffs, list) and all(isinstance(c, str) for c in coeffs):
        coeff_str = '\n'.join(coeffs) if coeffs else "N/A"
      else:
        coeff_str = str(coeffs) if coeffs else "N/A"
      self.coeff_var.set(coeff_str)
    except:
      self.coeff_var.set("N/A")
    
    self.update_history()
  
  def update_history(self):
    """Refresh the history list to show all saved steps."""
    if self.expression is None:
      return
    
    self.history_listbox.delete(0, tk.END)
    history = self.expression.get_history()
    
    for i, entry in enumerate(history):
      label = f"[{entry.timestamp}] {entry.operation}: {entry.expression}"
      self.history_listbox.insert(tk.END, label)
    
    # Keep the most recent item visible and selected.
    if history:
      self.history_listbox.see(tk.END)
      self.history_listbox.selection_set(len(history) - 1)
  
  def on_history_select(self, event):
    """When the user clicks a history item, show its details."""
    selection = self.history_listbox.curselection()
    if selection:
      selected_index = selection[0]
      history = self.expression.get_history()
      if selected_index < len(history):
        entry = history[selected_index]
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(1.0, 
          f"Index: {selected_index}\n"
          f"Time: {entry.timestamp}\n"
          f"Operation: {entry.operation}\n"
          f"Expression: {entry.expression}")
        self.log_text.config(state=tk.DISABLED)
  
  def load_selected_history(self):
    """Load the expression from the selected history entry."""
    if self.expression is None:
      messagebox.showerror("Error", "Please load an expression first")
      return
    
    selection = self.history_listbox.curselection()
    if not selection:
      messagebox.showerror("Error", "Please select a history entry")
      return
    
    selected_index = selection[0]
    if self.expression.load_history_state(selected_index):
      self.update_display()
      self.log_message(f"Loaded history state at index {selected_index}")
    else:
      messagebox.showerror("Error", "Failed to load selected state")
  
  def clear_history(self):
    """Erase all saved history steps after confirmation."""
    if messagebox.askyesno("Confirm", "Clear all history?"):
      if self.expression:
        self.expression.history = []
        self.expression.history_index = -1
        self.update_history()
        self.log_message("History cleared")
  
  def log_message(self, message):
    """Show a new message at the top of the log box."""
    self.log_text.config(state=tk.NORMAL)
    current = self.log_text.get(1.0, tk.END)
    timestamp = datetime.now().strftime("%H:%M:%S")
    new_log = f"[{timestamp}] {message}\n" + current
    self.log_text.delete(1.0, tk.END)
    self.log_text.insert(1.0, new_log)
    self.log_text.config(state=tk.DISABLED)

if __name__ == '__main__':
    root = tk.Tk()
    app = PolynomialGUI(root)
    root.mainloop()
