import application_logic as app_logic
import data_injection as datas
import streamlit as st

# Predictive imports
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plotly

import numpy as np
np.bool = bool

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from gluonts.mx.model.deepar import DeepAREstimator
from gluonts.mx.trainer import Trainer
from gluonts.dataset.common import ListDataset
from gluonts.evaluation.backtest import make_evaluation_predictions

mpl.rcParams["figure.figsize"] = (10,8)
mpl.rcParams["axes.grid"] = False

# load dataset
db_records = datas.get_table_data()
data_frame = pd.DataFrame(db_records)
data_frame["sequence_year"] = data_frame["interview_year"].apply(app_logic.find_nearest_year)

# creating estmator
train_time = 2010
prediction_length = 1

estimator = DeepAREstimator(
    freq="5y",
    context_length=2,                      # Use the last 2 time steps (10 years)
    prediction_length= prediction_length,  # Predict the next 5 years
    num_cells=10,                          # Use 10 hidden units for better capacity
    cell_type="lstm",                      # LSTM for long-term dependencies
    trainer=Trainer(epochs=50)             # Train for 50 epochs for better performance
)

# Step 1: Aggregate the data (counts of currently pregnant by year)
aggregated_data = (
    data_frame[data_frame["currently_pregnant"].str.lower() == "yes"]
    .groupby("sequence_year")
    .agg({"weights": "sum"})  # Weighted count
    .reset_index()
)

st.write(aggregated_data)

# Prepare training data
training_data = ListDataset(
        [{ "start": data_frame.index[0], "target": data_frame.currently_pregnant[:train_time] }],
        freq= "5y"
    )


# Predictor
predictor = estimator.train(training_data= training_data)


# Load and preprocess data
def prepare_data(data):
    # Convert data to DataFrame
    df = pd.DataFrame([x.split() for x in data.split('\n')], 
                      columns=['district', 'interview_year', 'age_range', 'currently_pregnant', 
                               'literacy', 'current_age', 'education_level', 'survey_round', 
                               'regions', 'wealth_quintile', 'weights', 'sequence_year'])
    
    # Encode categorical variables
    categorical_cols = ['district', 'age_range', 'literacy', 
                        'education_level', 'regions', 'wealth_quintile']
    
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Encode target variable
    df['currently_pregnant'] = df['currently_pregnant'].map({'yes': 1, 'no': 0})
    
    # Prepare features for time series
    features = ['district', 'age_range', 'literacy', 
                'current_age', 'education_level', 'regions', 
                'wealth_quintile', 'weights']
    
    return df, features, label_encoders


# Create GluonTS time series dataset
def create_gluonts_dataset(df, features):
    # Group by sequence year
    grouped = df.groupby('sequence_year')
    
    # Prepare data for GluonTS
    time_series_data = []
    for name, group in grouped:
        time_series_data.append({
            'start': name,
            'target': group['currently_pregnant'].values,
            'dynamic_feat': group[features].T
        })
    
    return ListDataset(time_series_data, freq='5Y')

# Train and predict
def train_predict_pregnancy(data):
    # Prepare data
    df, features, label_encoders = prepare_data(data)
    
    # Split data
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Create GluonTS datasets
    train_dataset = create_gluonts_dataset(train_df, features)
    test_dataset = create_gluonts_dataset(test_df, features)
    
    # Define model
    estimator = DeepAREstimator(
        freq='5Y',
        prediction_length=1,
        context_length=len(train_df),
        num_layers=2,
        num_cells=40,
        trainer=Trainer(epochs=50, learning_rate=1e-3)
    )
    
    # Train predictor
    predictor = estimator.train(train_dataset)
    
    # Forecast
    forecast_it, ts_it = make_evaluation_predictions(
        dataset=test_dataset,
        predictor=predictor
    )
    
    # Collect forecasts
    forecasts = list(forecast_it)
    true_values = list(ts_it)
    
    return forecasts, true_values, predictor

# Example usage
def main():
    # Paste your data here
    data = '''your_data_here'''
    
    forecasts, true_values, predictor = train_predict_pregnancy(data)
    
    # Interpret results
    for forecast, true_val in zip(forecasts, true_values):
        print(f"Predicted: {forecast.mean}, Actual: {true_val}")

if __name__ == "__main__":
    main()