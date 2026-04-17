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
    if '*' in self.expression:
      return  # Skip validation for combined expressions with multiplication
    for term in self.terms:
      if not re.match(r'^[+-]?\d*x*$', term):
        raise ValueError(f"Invalid term '{term}' in expression '{self.expression}'. Expression must be a valid polynomial (e.g., 3x + 2, x^2 - 1).")
    
  def get_degree(self):
    max_degree = 0
    for term in self.terms:
      if 'x' in term:
        degree = term.count('x')
        if degree > max_degree:
          max_degree = degree
    if max_degree > 0:
      print(f'The degree of the expression is {max_degree}')
    else:
      print(f'The expression is a constant and has degree 0')
  def __str__(self):
    return self.expression
  def __repr__(self):
    return self.expression
  def get_num_coefficients(self):
    coefficients = []
    for term in self.terms:
      if 'x' in term:
        coeff = term.replace('x', '')
        if coeff == '' or coeff == '+':
          coefficients.append(1)
        elif coeff == '-':
          coefficients.append(-1)
        else:
          coefficients.append(int(coeff))
      else:
        coefficients.append(int(term))
    return coefficients
  def get_coefficients(self):
    if '*' in self.expression:
      print("Coefficients cannot be extracted from multiplied expressions.")
      return []
    coefficients = []
    for term in self.terms:
      if 'x' in term:
        coeff = term.replace('x', '')
        if coeff == '' or coeff == '+':
          coefficients.append(1)
        elif coeff == '-':
          coefficients.append(-1)
        else:
          coefficients.append(int(coeff))
      else:
        coefficients.append(int(term))
    return coefficients
  def __add__(self, other):
    if isinstance(other, Expression):
      new_expression = f'({self.expression}) + ({other.expression})'
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only add another Expression object.")
  def __sub__(self, other):
    if isinstance(other, Expression):
      new_expression = f'({self.expression}) - ({other.expression})'
      return Expression(new_expression, prompt=False)
    else:
      raise ValueError("Can only subtract another Expression object.")
  def __mul__(self, other):
    if isinstance(other, Expression):
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
      print(f'The coefficients of the expression are: {self.get_coefficients()}')
      return self.get_next_step()
    elif choice == '3':
      self.get_degree()
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

