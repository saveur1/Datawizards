import data_injection as datas
import streamlit as st

# Predictive imports
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np
np.bool = bool

from sklearn.preprocessing import LabelEncoder
from gluonts.mx.model.deepar import DeepAREstimator
from gluonts.mx.trainer import Trainer
from gluonts.dataset.common import ListDataset
from gluonts.evaluation.backtest import make_evaluation_predictions
import mxnet as mx

# mpl.rcParams["figure.figsize"] = (10,8)
# mpl.rcParams["axes.grid"] = False


def prepare_data(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Label encode survey_round
    le = LabelEncoder()
    df['survey_round_encoded'] = le.fit_transform(df['survey_round'])
    
    # Prepare features for time series
    features = ['survey_round_encoded', 'pregnancy_count', 
                'literacy_count', 'total_count']
    
    # Target variable
    df['target'] = df['pregnancy_count']
    
    return df, features

def create_gluonts_dataset(df: type[pd.DataFrame], features):
    # Prepare data for GluonTS
    start = pd.Period(2010, freq="5Y")

    time_series_data = [{
        'start': start,
        'target': df['target'].values,
        'dynamic_feat': df[features].values.T
    }]
    
    return ListDataset(time_series_data, freq='5YE')

def train_predict_pregnancy(data):
    # Set MXNet context
    mx.context.default_ctx = mx.cpu()
    
    # Prepare data
    df, features = prepare_data(data)
    
    # Create GluonTS dataset
    dataset = create_gluonts_dataset(df, features)
    
    # Define model
    estimator = DeepAREstimator(
        freq='5YE',
        prediction_length=2,
        context_length=2,
        num_cells=10,
        trainer=Trainer(epochs=10)
    )
    
    # Train predictor
    try:
        predictor = estimator.train(dataset)
        
        # Forecast
        forecast_it, ts_it = make_evaluation_predictions(
            dataset=dataset,
            predictor=predictor
        )
        
        # Collect forecasts
        forecasts = list(forecast_it)
        true_values = list(ts_it)
        
        return forecasts, true_values, predictor
    
    except Exception as e:
        print(f"Training error: {e}")
        return None, None, None


def gemini_chart(ts_entry, forecast_entry):
    # Extract the true time series data
    true_series = ts_entry[-100:].to_timestamp()

    # Extract the predicted mean values
    predicted_series = forecast_entry.mean

    # Generate a range of future timestamps for the predicted series
    prediction_timestamps = pd.date_range(
        start= forecast_entry.start_date.to_timestamp(),
        periods= len(predicted_series),
        freq= forecast_entry.freq
    )

    print(prediction_timestamps)

    # Plot the true values
    plt.plot(true_series.index, true_series.values, label="True Values", color="blue", marker="o", linestyle="--")

    # Plot the predicted values
    plt.plot(prediction_timestamps, predicted_series, label="Predicted Values", color="orange", marker="x", linestyle="-")

    # Add labels, legend, and grid
    plt.title("True vs Predicted Values")
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)


# Example usage
def main():
    data = datas.get_pregnancy_counts_grouped()
    # [{'sequence_year': 2010, 'survey_round': '2010-11', 'pregnancy_count': 44.468354, 'literacy_count': 2638.216695, 'total_count': 2945.333568}, {'sequence_year': 2015, 'survey_round': '2014-15', 'pregnancy_count': 52.397633, 'literacy_count': 2513.726921, 'total_count': 2767.865233}, {'sequence_year': 2020, 'survey_round': '2019-20', 'pregnancy_count': 49.342285, 'literacy_count': 3024.508962, 'total_count': 3258.312762}]
    forecasts, true_values, _ = train_predict_pregnancy(data)
    # np.array(true_values[:5]).reshape(-1)

    # first entry of the forecast list
    forecast_entry = forecasts[0]
    # first entry of the time series list
    ts_entry = true_values[0]

    print(f"Number of sample paths: {forecast_entry.num_samples}")
    print(f"Dimension of samples: {forecast_entry.samples.shape}")
    print(f"Start date of the forecast window: {forecast_entry.start_date}")
    print(f"Frequency of the time series: {forecast_entry.freq}")

    print(f"Mean of the future window:\n {forecast_entry.mean}")
    print(f"0.5-quantile (median) of the future window:\n {forecast_entry.quantile(0.5)}")


    gemini_chart(ts_entry, forecast_entry)


if __name__ == "__main__":
    main()