import re
  # step one :
  # break into terms and store as a class
  #
class Expression:
  def __init__(self, expression=None, prompt=True):
    if expression is None:
      expression = input('Enter the expression: \n>')
    self.terms = self.break_up_input(expression)
    self.expression = expression
    self.validate()

    if prompt:
      self.get_next_step()

  def break_up_input(self,input_string):
    input_string = input_string.replace(' ', '')
    input_string = input_string.replace('(', '').replace(')', '')
    splitup = list(input_string)
    for i in range(len(splitup) - 1, -1, -1):  # Iterate backwards to avoid index shifts
      if splitup[i] == '-':
        splitup.insert(i, ';')
      input_string = ''.join(splitup)
    terms = [term for term in re.split(';|\+', input_string) if term]
    return terms
    
  def validate(self):
    if '*' in self.expression or '/' in self.expression:
      return  # Skip validation for combined expressions with multiplication or division
    for term in self.terms:
      if not re.match(r'^[+-]?\d*x*$', term):
        raise ValueError(f"Invalid term '{term}' in expression '{self.expression}'. Expression must be a valid polynomial (e.g., 3x + 2, x^2 - 1).")
    
  def get_poly(self):
    if '*' in self.expression or '/' in self.expression:
      raise ValueError("Cannot extract polynomial from combined expression")
    poly = {}
    for term in self.terms:
      if 'x' in term:
        coeff_str = term.replace('x', '')
        if coeff_str == '' or coeff_str == '+':
          coeff = 1
        elif coeff_str == '-':
          coeff = -1
        else:
          coeff = int(coeff_str)
        degree = term.count('x')
      else:
        coeff = int(term)
        degree = 0
      if degree in poly:
        poly[degree] += coeff
      else:
        poly[degree] = coeff
    return poly
  
  @staticmethod
  def poly_to_expr(poly):
    terms = []
    for d in sorted(poly.keys(), reverse=True):
      c = poly[d]
      if c == 0:
        continue
      if d == 0:
        terms.append(str(c))
      else:
        x_part = 'x' * d
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
    try:
      poly = self.get_poly()
      if poly:
        return max(poly.keys())
      else:
        return 0
    except ValueError:
      print("Degree cannot be determined for combined expressions.")
      return None
  
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
      try:
        poly1 = self.get_poly()
        poly2 = other.get_poly()
        new_poly = poly1.copy()
        for d, c in poly2.items():
          if d in new_poly:
            new_poly[d] += c
          else:
            new_poly[d] = c
        new_expression = Expression.poly_to_expr(new_poly)
        return Expression(new_expression, prompt=False)
      except ValueError:
        # Fallback to string combination
        new_expression = f'({self.expression}) + ({other.expression})'
        return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only add another Expression object.")
  def __sub__(self, other):
    if isinstance(other, Expression):
      try:
        poly1 = self.get_poly()
        poly2 = other.get_poly()
        new_poly = poly1.copy()
        for d, c in poly2.items():
          if d in new_poly:
            new_poly[d] -= c
          else:
            new_poly[d] = -c
        new_expression = Expression.poly_to_expr(new_poly)
        return Expression(new_expression, prompt=False)
      except ValueError:
        # Fallback to string combination
        new_expression = f'({self.expression}) - ({other.expression})'
        return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only subtract another Expression object.")
  def __mul__(self, other):
    if isinstance(other, Expression):
      try:
        poly1 = self.get_poly()
        poly2 = other.get_poly()
        new_poly = {}
        for d1, c1 in poly1.items():
          for d2, c2 in poly2.items():
            d = d1 + d2
            c = c1 * c2
            if d in new_poly:
              new_poly[d] += c
            else:
              new_poly[d] = c
        new_expression = Expression.poly_to_expr(new_poly)
        return Expression(new_expression, prompt=False)
      except ValueError:
        # Fallback to string combination
        new_expression = f'({self.expression}) * ({other.expression})'
        return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only multiply by another Expression object.")
  def __truediv__(self, other):
    if isinstance(other, Expression):
      new_expression = f'({self.expression}) / ({other.expression})'
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only divide by another Expression object.")
  def get_next_step(self):
    choice=input('What would you like to do next? (1: Combine with another expression, 2: Get coefficients, 3: Get degree, 4: Show current expression, 5: Exit)\n>')
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
        return self.get_next_step()
      self.expression = combined.expression
      self.terms = combined.terms
      print(f'New combined expression: {self.expression}')
      return self.get_next_step()
    elif choice == '2':
      coeffs = self.get_coefficients()
      print(f'The coefficients of the expression are: {coeffs}')
      return self.get_next_step()
    elif choice == '3':
      deg = self.get_degree()
      if deg is not None:
        print(f'The degree of the expression is {deg}')
      return self.get_next_step()
    elif choice == '4':
      print(f'Current expression: {self.expression}')
      return self.get_next_step()
    elif choice == '5':
      print('Exiting...')
      return
    else:
      print('Invalid choice. Please try again.')
      return self.get_next_step()

math=Expression()

