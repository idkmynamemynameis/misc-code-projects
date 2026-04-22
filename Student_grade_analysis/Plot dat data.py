import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Read the CSV with headers (no need to skip rows)
data = pd.read_csv('StudentPerformanceFactors.csv')

# Extract Exam_Score as the dependent variable
exam_scores = data['Exam_Score']

# List of predictors to compare (select a few key ones)
predictors = ['Attendance', 'Hours_Studied', 'Previous_Scores', 'Sleep_Hours']
colors = ['red', 'blue', 'green', 'orange']

# Plotting multiple regression lines with standardized predictors
plt.figure(figsize=(10, 6))

for i, predictor in enumerate(predictors):
    x = data[predictor]
    # Standardize the predictor (mean=0, std=1) for scaling
    x_standardized = (x - x.mean()) / x.std()
    # Fit linear regression on standardized x
    coefficients = np.polyfit(x_standardized, exam_scores, 1)
    slope = coefficients[0]
    intercept = coefficients[1]
    # Generate predicted values over a common range (-3 to 3 for standardized scale)
    x_range = np.linspace(-3, 3, 100)
    predicted = slope * x_range + intercept
    # Plot the line
    plt.plot(x_range, predicted, color=colors[i], linewidth=2, label=f'{predictor}: slope = {slope:.2f}')

plt.title('Linear Regression Lines: Standardized Predictors vs Exam Scores')
plt.xlabel('Standardized Predictor Values (Mean=0, Std=1)')
plt.ylabel('Exam Scores')
plt.grid(True)
plt.legend()
plt.show()