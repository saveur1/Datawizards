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
import mxnet as mx

mpl.rcParams["figure.figsize"] = (10,8)
mpl.rcParams["axes.grid"] = False

# data_frame = pd.DataFrame(db_records)
# data_frame["sequence_year"] = data_frame["interview_year"].apply(app_logic.find_nearest_year)

# # creating estmator
# train_time = 2010
# prediction_length = 1

# estimator = DeepAREstimator(
#     freq="5y",
#     context_length=2,                      # Use the last 2 time steps (10 years)
#     prediction_length= prediction_length,  # Predict the next 5 years
#     num_cells=10,                          # Use 10 hidden units for better capacity
#     cell_type="lstm",                      # LSTM for long-term dependencies
#     trainer=Trainer(epochs=50)             # Train for 50 epochs for better performance
# )

# # Step 1: Aggregate the data (counts of currently pregnant by year)
# aggregated_data = (
#     data_frame[data_frame["currently_pregnant"].str.lower() == "yes"]
#     .groupby("sequence_year")
#     .agg({"weights": "sum"})  # Weighted count
#     .reset_index()
# )

# st.write(aggregated_data)

# # Prepare training data
# training_data = ListDataset(
#         [{ "start": data_frame.index[0], "target": data_frame.currently_pregnant[:train_time] }],
#         freq= "5y"
#     )


# # Predictor
# predictor = estimator.train(training_data= training_data)


def prepare_data(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Label encode survey_round
    le = LabelEncoder()
    df['survey_round_encoded'] = le.fit_transform(df['survey_round'])
    
    # Prepare features for time series
    features = ['survey_round_encoded', 'pregnancy_count', 
                'literacy_count', 'total_count']
    
    # Print debug information
    print("DataFrame Info:")
    print(df.info())
    print("\nUnique sequence years:", df['sequence_year'].unique())
    
    # Target variable (choose based on your prediction goal)
    df['target'] = df['pregnancy_count']
    
    return df, features

def create_gluonts_dataset(df, features):
    # Prepare data for GluonTS
    time_series_data = [{
        'start': df['sequence_year'].min(),
        'target': df['target'].values,
        'dynamic_feat': df[features].values.T
    }]
    
    print(f"Time series entries: {len(time_series_data)}")
    
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
        prediction_length=1,
        context_length=1,
        num_layers=1,
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

def create_visualization(ts_entry, forecast_entry):
    plot_length = 1
    prediction_intervals = (30, 60)
    legend = ["Observations", "Median prediction"]+[f"{k}% prediction interval" for k in prediction_intervals[::-1]] 

    fig, ax = plotly.subplots(1, 1, figsize=(10, 7))
    ts_entry[plot_length].plot(ax=ax)
    forecast_entry.plot(prediction_intervals= prediction_intervals, color="g")
    plotly.grid(which="both")
    plotly.legend(legend, loc="upper left")
    plotly.show()

# Example usage
def main():
    data = datas.get_pregnancy_counts_grouped()
    # [{'sequence_year': 2010, 'survey_round': '2010-11', 'pregnancy_count': 44.468354, 'literacy_count': 2638.216695, 'total_count': 2945.333568}, {'sequence_year': 2015, 'survey_round': '2014-15', 'pregnancy_count': 52.397633, 'literacy_count': 2513.726921, 'total_count': 2767.865233}, {'sequence_year': 2020, 'survey_round': '2019-20', 'pregnancy_count': 49.342285, 'literacy_count': 3024.508962, 'total_count': 3258.312762}]
    forecasts, true_values, predictor = train_predict_pregnancy(data)
    print(true_values)

    create_visualization(true_values[0], forecasts[0])


if __name__ == "__main__":
    main()