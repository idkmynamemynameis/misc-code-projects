import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_PATH = 'StudentPerformanceFactors.csv'


def plot_regression_lines(data):
    predictors = ['Attendance', 'Hours_Studied', 'Previous_Scores', 'Sleep_Hours']
    colors = ['red', 'blue', 'green', 'orange']
    exam_scores = data['Exam_Score']

    plt.figure(figsize=(11, 7))
    for i, predictor in enumerate(predictors):
        x = data[predictor]
        x_standardized = (x - x.mean()) / x.std()
        coefficients = np.polyfit(x_standardized, exam_scores, 1)
        slope, intercept = coefficients
        x_range = np.linspace(-3, 3, 100)
        predicted = slope * x_range + intercept
        plt.plot(x_range, predicted, color=colors[i], linewidth=2,
                 label=f'{predictor} (slope = {slope:.2f})')

    plt.title('Standardized Predictors vs Exam Scores')
    plt.xlabel('Standardized Predictor Value')
    plt.ylabel('Exam Score')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_scatter_with_regression(data):
    exam_scores = data['Exam_Score']
    predictors = ['Hours_Studied', 'Attendance']
    colors = ['tab:blue', 'tab:orange']

    plt.figure(figsize=(11, 7))
    for predictor, color in zip(predictors, colors):
        x = data[predictor]
        coefficients = np.polyfit(x, exam_scores, 1)
        slope, intercept = coefficients
        x_range = np.linspace(x.min(), x.max(), 100)
        predicted = slope * x_range + intercept
        plt.scatter(x, exam_scores, alpha=0.5, color=color, label=f'{predictor} data')
        plt.plot(x_range, predicted, color=color, linewidth=2,
                 label=f'{predictor} regression (slope={slope:.2f})')

    plt.title('Exam Score vs Hours Studied and Attendance')
    plt.xlabel('Predictor Value')
    plt.ylabel('Exam Score')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_exam_score_histogram(data):
    plt.figure(figsize=(10, 6))
    plt.hist(data['Exam_Score'], bins=12, color='skyblue', edgecolor='black')
    plt.title('Distribution of Exam Scores')
    plt.xlabel('Exam Score')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.65)
    plt.tight_layout()
    plt.show()


def plot_boxplot_by_gender(data):
    categories = ['Male', 'Female']
    scores_by_gender = [data.loc[data['Gender'] == gender, 'Exam_Score'] for gender in categories]

    plt.figure(figsize=(8, 6))
    plt.boxplot(scores_by_gender, labels=categories, patch_artist=True,
                boxprops=dict(facecolor='lightgreen', color='black'),
                medianprops=dict(color='firebrick'))
    plt.title('Exam Score Distribution by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Exam Score')
    plt.grid(axis='y', alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_average_score_by_parental_education(data):9
    group = data.groupby('Parental_Education_Level')['Exam_Score'].mean().sort_values()
    plt.figure(figsize=(10, 6))
    plt.bar(group.index, group.values, color='mediumpurple', edgecolor='black')
    plt.title('Average Exam Score by Parental Education Level')
    plt.xlabel('Parental Education Level')
    plt.ylabel('Average Exam Score')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.5)
    plt.tight_layout()
    plt.show()


def plot_numeric_correlation_heatmap(data):
    numeric_cols = ['Hours_Studied', 'Attendance', 'Sleep_Hours', 'Previous_Scores', 'Exam_Score']
    corr = data[numeric_cols].corr()

    plt.figure(figsize=(8, 6))
    im = plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.xticks(range(len(numeric_cols)), numeric_cols, rotation=45, ha='right')
    plt.yticks(range(len(numeric_cols)), numeric_cols)

    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            plt.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', color='black')

    plt.title('Correlation Matrix for Numeric Features')
    plt.tight_layout()
    plt.show()


def main():
    data = pd.read_csv(DATA_PATH)
    graph_menu = {
        '1': ('Standardized regression lines for key predictors', plot_regression_lines),
        '2': ('Scatter plots with regression for Hours Studied and Attendance', plot_scatter_with_regression),
        '3': ('Histogram of Exam Scores', plot_exam_score_histogram),
        '4': ('Boxplot of Exam Scores by Gender', plot_boxplot_by_gender),
        '5': ('Average Exam Score by Parental Education Level', plot_average_score_by_parental_education),
        '6': ('Correlation heatmap for numeric features', plot_numeric_correlation_heatmap),
    }

    while True:
        print('\nSelect a graph to display:')
        for key, (description, _) in graph_menu.items():
            print(f'  {key}. {description}')
        print('  q. Quit')

        choice = input('Enter choice: ').strip().lower()
        if choice == 'q':
            print('Exiting.')
            break
        if choice in graph_menu:
            _, plot_function = graph_menu[choice]
            plot_function(data)
        else:
            print('Invalid selection. Please choose a valid option.')


if __name__ == '__main__':
    main()
