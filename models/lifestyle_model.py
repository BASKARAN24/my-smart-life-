def lifestyle_advice(sleep, stress, water):

    advice = []

    if sleep < 6:
        advice.append("You need more sleep. Try to sleep at least 7-8 hours.")

    if stress > 7:
        advice.append("High stress detected. Try meditation or yoga.")

    if water < 2:
        advice.append("Drink more water. Aim for at least 2-3 liters daily.")

    if sleep >= 7 and stress <= 5 and water >= 2:
        advice.append("Great lifestyle! Keep maintaining your healthy habits.")

    return advice
