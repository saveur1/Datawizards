import application_logic as app_logic
import data_injection as datas
import streamlit as st

# Predictive imports
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plotly

import numpy as np
np.bool = bool

from gluonts.mx.model.deepar import DeepAREstimator
from gluonts.mx.trainer import Trainer
from gluonts.dataset.common import ListDataset

mpl.rcParams["figure.figsize"] = (10,8)
mpl.rcParams["axes.grid"] = False

# load dataset
db_records = datas.get_table_data()
data_frame = pd.DataFrame(db_records)
data_frame["sequence_year"] = data_frame["interview_year"].apply(app_logic.find_nearest_year)
st.table(data_frame)

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

# Prepare training data
training_data = ListDataset(
        [{ "start": data_frame.index[0], "target": data_frame.currently_pregnant[:train_time] }],
        freq= "5y"
    )


# Predictor
predictor = estimator.train(training_data= training_data)