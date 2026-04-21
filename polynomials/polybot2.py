import re
  # step one :
  # break into terms and store as a class
  #
class Expression:
  _term_pattern = re.compile(r'^[+-]?(?:\d*\.?\d*x(?:\^\d+)?|\d*\.?\d+)$')

  def __init__(self, expression=None, prompt=True):
    if expression is None:
      expression = input('Enter the expression: \n>')
    self.expression = expression
    self.terms = self.break_up_input(expression)
    self.combined = any(op in self.expression for op in '*/()')
    if not self.combined:
      self.validate()
      poly = {}
      for term in self.terms:
        if 'x' in term:
          if '^' in term:
            parts = term.split('^')
            coeff_str = parts[0].replace('x', '')
            degree = int(parts[1])
          else:
            coeff_str = term.replace('x', '')
            degree = term.count('x')
          if coeff_str == '' or coeff_str == '+':
            coeff = 1.0
          elif coeff_str == '-':
            coeff = -1.0
          else:
            coeff = float(coeff_str)
        else:
          coeff = float(term)
          degree = 0
        if degree in poly:
          poly[degree] += coeff
        else:
          poly[degree] = coeff
      self.poly = poly
    else:
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

    if prompt:
      self.get_next_step()

  @staticmethod
  def normalize_poly(poly):
    return {d: c for d, c in poly.items() if abs(c) > 1e-10}

  @staticmethod
  def add_polys(poly1, poly2):
    new_poly = poly1.copy()
    for d, c in poly2.items():
      new_poly[d] = new_poly.get(d, 0) + c
    return Expression.normalize_poly(new_poly)

  @staticmethod
  def sub_polys(poly1, poly2):
    new_poly = poly1.copy()
    for d, c in poly2.items():
      new_poly[d] = new_poly.get(d, 0) - c
    return Expression.normalize_poly(new_poly)

  @staticmethod
  def mul_polys(poly1, poly2):
    new_poly = {}
    for d1, c1 in poly1.items():
      for d2, c2 in poly2.items():
        d = d1 + d2
        new_poly[d] = new_poly.get(d, 0) + c1 * c2
    return Expression.normalize_poly(new_poly)

  @staticmethod
  def div_polys(poly1, poly2):
    if not poly2:
      raise ValueError("Division by zero")
    quotient = {}
    remainder = poly1.copy()
    while remainder:
      deg_r = max(remainder.keys())
      deg_d = max(poly2.keys())
      if deg_r < deg_d:
        break
      coeff_r = remainder[deg_r]
      coeff_d = poly2[deg_d]
      q_coeff = coeff_r / coeff_d
      q_deg = deg_r - deg_d
      quotient[q_deg] = q_coeff
      # subtract q * divisor shifted
      for d, c in poly2.items():
        deg = d + q_deg
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
    while b:
      q, r = Expression.div_polys(a, b)
      a, b = b, r
    return a

  @staticmethod
  def evaluate_expression(expr):
    expr = expr.replace(' ', '')
    tokens = Expression.tokenize(expr)
    pos = [0]  # use list to modify in nested functions
    poly = Expression.parse_expression(tokens, pos)
    if pos[0] != len(tokens):
      raise ValueError("Extra tokens in expression")
    return poly

  @staticmethod
  def tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
      if expr[i].isdigit() or (expr[i] == '-' and (i == 0 or expr[i-1] in '+-*/(')):
        num = ''
        if expr[i] == '-':
          num += '-'
          i += 1
        while i < len(expr) and expr[i].isdigit():
          num += expr[i]
          i += 1
        tokens.append(('NUM', int(num)))
        # Check for implicit *
        if i < len(expr) and expr[i] in '0123456789x(':
          tokens.append(('OP', '*'))
      elif expr[i] == 'x':
        tokens.append(('VAR', 'x'))
        i += 1
        # Check for implicit *
        if i < len(expr) and expr[i] in '0123456789x(':
          tokens.append(('OP', '*'))
      elif expr[i] in '+-*/^()':
        tokens.append(('OP', expr[i]))
        i += 1
        # After ), check for implicit *
        if expr[i-1] == ')' and i < len(expr) and expr[i] in '0123456789x(':
          tokens.append(('OP', '*'))
      else:
        raise ValueError(f"Invalid character '{expr[i]}' in expression")
    return tokens

  @staticmethod
  def parse_expression(tokens, pos):
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
    if tokens[pos[0]][0] == 'NUM':
      num = tokens[pos[0]][1]
      pos[0] += 1
      return {0: float(num)}
    elif tokens[pos[0]][0] == 'VAR':
      pos[0] += 1
      deg = 1
      if pos[0] < len(tokens) and tokens[pos[0]][0] == 'OP' and tokens[pos[0]][1] == '^':
        pos[0] += 1
        if tokens[pos[0]][0] == 'NUM':
          deg = tokens[pos[0]][1]
          pos[0] += 1
        else:
          raise ValueError("Expected number after ^")
      return {deg: 1.0}
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
    cleaned = input_string.replace(' ', '').replace('(', '').replace(')', '')
    terms = [term for term in re.split(r'(?=[+-])', cleaned) if term]
    return terms
    
  def validate(self):
    for term in self.terms:
      if not Expression._term_pattern.match(term):
        raise ValueError(f"Invalid term '{term}' in expression '{self.expression}'. Expression must be a valid polynomial (e.g., 3x + 2, x^2 - 1).")
    
  def get_poly(self):
    if self.poly is not None:
      return self.poly
    else:
      raise ValueError("Coefficients cannot be extracted from combined expressions.")
  
  @staticmethod
  def poly_to_expr(poly):
    terms = []
    for d in sorted(poly.keys(), reverse=True):
      c = poly[d]
      if abs(c) < 1e-10:
        continue
      # Round to int if close
      if abs(c - round(c)) < 1e-10:
        c = int(round(c))
      if d == 0:
        terms.append(str(c))
      else:
        if d == 1:
          x_part = 'x'
        else:
          x_part = f'x^{d}'
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
    poly = self.get_poly()
    if poly:
      return max(poly.keys())
    else:
      return 0
  
  def get_coefficients(self):
    try:
      poly = self.get_poly()
      coeffs = []
      max_deg = max(poly.keys()) if poly else 0
      for d in range(max_deg + 1):
        coeffs.append(poly.get(d, 0))
      return coeffs
    except ValueError:
      print("Coefficients cannot be extracted from combined expressions.")
      return []
  def __add__(self, other):
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
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only add another Expression object.")
  def __sub__(self, other):
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
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only subtract another Expression object.")
  def __mul__(self, other):
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
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only multiply by another Expression object.")
  def __truediv__(self, other):
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
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only divide by another Expression object.")
  def get_next_step(self):
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

if __name__ == '__main__':
    math=Expression()
