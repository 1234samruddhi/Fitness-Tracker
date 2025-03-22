import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import time
import warnings

warnings.filterwarnings('ignore')

st.write("## Personal Fitness Tracker")
st.write("This WebApp allows you to estimate the calories burned based on your personal health data. By entering parameters such as age, gender, BMI, height, weight, and activity level, the system will predict the number of kilocalories burned using machine learning models.")

st.sidebar.header("User Input Parameters")

def user_input_features():
    age = st.sidebar.slider("Age (years):", 10, 100, 30)
    bmi = st.sidebar.slider("BMI (kg/m²):", 15, 40, 20)
    duration = st.sidebar.slider("Duration (minutes):", 0, 35, 15)
    heart_rate = st.sidebar.slider("Heart Rate (bpm):", 60, 130, 80)
    body_temp = st.sidebar.slider("Body Temperature (°C):", 36, 42, 38)
    gender = st.sidebar.radio("Gender:", ("Male", "Female"))
    gender_encoded = 1 if gender == "Male" else 0

    return pd.DataFrame({
        "Age": [age],
        "BMI": [bmi],
        "Duration": [duration],
        "Heart_Rate": [heart_rate],
        "Body_Temp": [body_temp],
        "Gender_male": [gender_encoded]
    })

df = user_input_features()

st.write("---")
st.header("Your Input Parameters")
st.dataframe(df)

# Load dataset
calories = pd.read_csv("calories.csv")
exercise = pd.read_csv("exercise.csv")

# Merge datasets and preprocess
data = exercise.merge(calories, on="User_ID").drop(columns=["User_ID"])
data["BMI"] = round(data["Weight"] / ((data["Height"] / 100) ** 2), 2)
data = pd.get_dummies(data, drop_first=True)

# Split dataset
train_data, test_data = train_test_split(data, test_size=0.2, random_state=1)
X_train, y_train = train_data.drop("Calories", axis=1), train_data["Calories"]
X_test, y_test = test_data.drop("Calories", axis=1), test_data["Calories"]

# Train model
model = RandomForestRegressor(n_estimators=1000, max_features=3, max_depth=6, random_state=1)
model.fit(X_train, y_train)

# Ensure input data columns match training data
input_data = df.reindex(columns=X_train.columns, fill_value=0)

# Make prediction
with st.spinner("Predicting calories burned..."):
    prediction = model.predict(input_data)

st.write("---")
st.header("Predicted Calories Burned")
st.success(f"{round(prediction[0], 2)} kilocalories")

# Find similar results
st.write("---")
st.header("Similar Results")
calorie_range = [prediction[0] - 10, prediction[0] + 10]
similar_data = data[(data["Calories"] >= calorie_range[0]) & (data["Calories"] <= calorie_range[1])]
if not similar_data.empty:
    st.dataframe(similar_data.sample(min(5, len(similar_data))))
else:
    st.warning("No similar results found.")

# General statistics
st.write("---")
st.header("General Information")
st.write(f"You are older than {round((data['Age'] < df['Age'].values[0]).mean() * 100, 2)}% of others.")
st.write(f"Your exercise duration is higher than {round((data['Duration'] < df['Duration'].values[0]).mean() * 100, 2)}% of others.")
st.write(f"Your heart rate is higher than {round((data['Heart_Rate'] < df['Heart_Rate'].values[0]).mean() * 100, 2)}% of others.")
st.write(f"Your body temperature is higher than {round((data['Body_Temp'] < df['Body_Temp'].values[0]).mean() * 100, 2)}% of others.")
