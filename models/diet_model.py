import pandas as pd

data = pd.read_csv("dataset/nutrients_csvfile.csv")

# convert columns to numbers
data["Calories"] = pd.to_numeric(data["Calories"], errors="coerce")
data["Protein"] = pd.to_numeric(data["Protein"], errors="coerce")
data["Carbs"] = pd.to_numeric(data["Carbs"], errors="coerce")
data["Fat"] = pd.to_numeric(data["Fat"], errors="coerce")

data = data.dropna()

def recommend_diet(goal):

    if goal == "weight_loss":
        foods = data[data["Calories"] < 200]

    elif goal == "muscle_gain":
        foods = data[data["Protein"] > 10]

    else:
        foods = data

    meal_plan = {
        "breakfast": foods.sample(2).to_dict(orient="records"),
        "brunch": foods.sample(2).to_dict(orient="records"),
        "lunch": foods.sample(2).to_dict(orient="records"),
        "snacks": foods.sample(2).to_dict(orient="records"),
        "dinner": foods.sample(2).to_dict(orient="records")
    }

    return meal_plan
