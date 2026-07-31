import numpy as np
from sklearn.linear_model import LinearRegression

# Sample training data
X = np.array([
    [20,60,165,1],
    [25,70,170,2],
    [30,80,175,2],
    [35,90,180,3],
    [28,65,168,1],
    [40,85,178,3]
])

y = np.array([
    1800,
    2200,
    2400,
    2800,
    2000,
    2600
])

model = LinearRegression()
model.fit(X, y)

def predict_calories(age, weight, height, activity):

    data = [[age, weight, height, activity]]

    calories = model.predict(data)

    return int(calories[0])
