import streamlit as st
# import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#Local Imports
import data_injection as datas
import application_logic as appl
from typing import List

def current_pregnancy_chart():
    # get data from session
    filtered_records = st.session_state.filtered_records

    # count pregnant teenagers
    pregnant_count = appl.count_frequency(filtered_records, "currently_pregnant", "yes")
    literate_count = appl.count_frequency(filtered_records, "literacy", ["able to read whole sentence", "able to read only parts of sentence"], array_values=True)

    trace_colors =  ['rgb(217, 217, 217)', 'rgb(216, 7, 7)']
    pie_chart_data = [len(filtered_records) - pregnant_count, pregnant_count]
    chart_title = f"Pregnancy chart for { st.session_state.session_district }"
    chart_labels = ['Not Pregnant', 'Pregnant Teenage']

    left, middle= st.columns(2)
    if left.button("Pregnancy", use_container_width=True, key="pie_chart_left"):
        pie_chart_data = [len(filtered_records) - pregnant_count, pregnant_count]
        chart_title = f"Pregnancy chart for { st.session_state.session_district }"
        chart_labels = ['Not Pregnant', 'Pregnant Teenage']
    
    if middle.button("Literacy", use_container_width=True, key="pie_chart_right"):
        pie_chart_data = [literate_count, len(filtered_records) - literate_count]
        chart_title = f"Literacy chart for { st.session_state.session_district }"
        chart_labels = ['Able to read', "can't read at all"]

    trace = go.Pie(labels= chart_labels, values = pie_chart_data, hole=0.5, marker_colors= trace_colors)

    # Create the layout for the chart
    layout = go.Layout(
        title=dict(
                text=f'<i>{ chart_title }<i>',
                x=0.5,
                xanchor="center"
            ),
        showlegend=False,  # Hide the legend
        margin=dict(l=0, r=0, b=0, t=40),
        width=300,  # Set the desired width
        height=200,  # Set the desired height
        annotations=[
            dict(
                text=f'{ "{:,} <br />Women".format(len(filtered_records)) }',
                x=0.5, y=0.5, font_size=20, showarrow=False
            )
        ]
    )

    # Create the figure and plot it using Streamlit
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)


def teenage_pregnancy_history(records: List):
    #state variable
    filtered_records = records
    district = st.session_state.session_district

    if district != "All Districts":
        filtered_records = [data for data in records if str(data["district"]).lower() == str(district).lower()]

    # Get pregnancy counts for the earliest and latest year
    summary = appl.create_upload_summary(filtered_records, "survey_round")

    # Sort them by interview year
    summary = sorted(summary, key=lambda x: x["year"])

    # Survey round array
    survey_rounds = ["R_"+data["survey_round"]  for data in summary ]

    # Survey round pregnancy
    survey_pregnancies = [ data["pregnant_count"]  for data in summary ]
    women_records = [ data["women_count"]  for data in summary ]

    survey_pregnacy_result = appl.calculate_preg_percentages(survey_pregnancies, women_records)
    percent_sign = "(%)"

    left, middle= st.columns(2)
    if left.button("Percent(%)", use_container_width=True):
        survey_pregnacy_result = appl.calculate_preg_percentages(survey_pregnancies, women_records)
        percent_sign = "(%)"

    
    if middle.button("Plain Data", use_container_width=True):
        survey_pregnacy_result = survey_pregnancies
        percent_sign = ""

    # Plot history chart
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        fill='tozeroy',
        x= survey_rounds,
        y= survey_pregnacy_result,
        mode='lines+markers+text',
        line_color='red'      
    ))

    fig.update_layout(
        width=300,
        height=340,
        title=dict(text=f"<i>Pregnancy History for { st.session_state.session_district }{ percent_sign }</i>", x=0.5,xanchor="center"),
        yaxis_title="Pregnant Teenage",
        legend=dict(yanchor="top", y=-1, xanchor="center", x=0.5))
    
    st.plotly_chart(fig, use_container_width=True, key="CHART1")


def district_country_chart():
    fig1=go.Figure()
    fig1.add_trace(go.Scatter(
        x=["Jan","Feb","Mar","Apr","May","Jun","Juy"],
        y=[12,13,14, 14,17, 17,20],
        name="Kicukiro",
        mode='lines+markers+text',
        line_color='red'      
    ))
    fig1.add_trace(go.Scatter(
        x=["Jan","Feb","Mar","Apr","May","Jun","Juy"],
        y=[10,8,10, 18,15, 12,7],
        name="A whole country",
        mode='lines+markers+text',
        line_color='black'      
    ))

    fig1.update_layout(
        width=300,
        height=300,
        title=dict(text="<i>Kicukiro vs Whole Country</i>", x=0.5,xanchor="center"),
        yaxis_title="Pregnant Teenage",
        legend=dict(yanchor="top", y=-1, xanchor="center", x=0.5))
    
    st.plotly_chart(fig1, use_container_width=True, key="CHART2")


def country_heatmap():
    # datas
    filtered_records = st.session_state.filtered_records
    grouped_records = appl.records_grouped_by_district(filtered_records)
    results = []

    for district, records in grouped_records.items():
        pregnant_count = appl.count_frequency(records, "currently_pregnant", "yes")

        # Geocode the district name to get latitude and longitude
        location = datas.coordinates_for_district(district)
        
        if location:
            lat, lon = location["latitude"], location["longitude"]
    
            generated_datas = np.random.randn(int(pregnant_count), 2) / [50, 50] + [round(lat,2), round(lon, 2)]

            # Append each coordinate pair individually to datas
            for point in generated_datas:
                results.append(point.tolist())

    
    df = pd.DataFrame(
        results,
        columns=["lat", "lon"],
    )
    st.map(
        df, use_container_width=True, 
        zoom=7 ,height=400, #zoom level 7 and 11 works well
    )
