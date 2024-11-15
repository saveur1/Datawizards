import streamlit as st
# import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

#Local Imports
import data_injection as datas
import application_logic as appl
from typing import List
from collections import defaultdict

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

    # left, middle= st.columns(2)
    # if left.button("Percent(%)", use_container_width=True):
    #     survey_pregnacy_result = appl.calculate_preg_percentages(survey_pregnancies, women_records)
    #     percent_sign = "(%)"

    
    # if middle.button("Plain Data", use_container_width=True):
    #     survey_pregnacy_result = survey_pregnancies
    #     percent_sign = ""

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
        height=400,
        title=dict(text=f"<i>Pregnancy History for { st.session_state.session_district }(%)</i>", x=0.5,xanchor="center"),
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

def education_statistics():
    records = st.session_state.filtered_records
    #education level grouping
    education_groups = appl.records_grouped_by_district(records, "education_level")
    education_levels = defaultdict(list)
    for level, records in education_groups.items():
        education_levels["Education Level"].append(str(level).capitalize()),
        education_levels["Number of Women"].append(len(records))
    
    default_ed = {
        "Education Level": [],
        "Number of Women": []
    }

    df_education = pd.DataFrame(dict(education_levels) or default_ed)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_education["Number of Women"],
        y=df_education["Education Level"],
        text=[f'{x:,} Women' for x in df_education["Number of Women"]],
        textposition='inside',
        orientation='h',
        marker_color='#ff4b4b',
        hovertemplate='%{y}: %{x:,.0f} Women<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(text=f"<i>Education level in { st.session_state.session_district }</i>", x=0.5,xanchor="center"),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels as they're redundant with the bar labels
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            tickmode='array',
            ticktext=df_education["Education Level"],
            tickvals=df_education["Education Level"],
            showgrid=False
        ),
        plot_bgcolor='white',
        showlegend=False
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True, key="education_summary")
    

def provinces_statistics(records: List):

    #education level grouping
    regions_groups = appl.records_grouped_by_district(records, "regions")
    regions = defaultdict(list)

    for region, records in regions_groups.items():
        regions["Region"].append(str(region).capitalize()),
        regions["Women Asked"].append(len(records))

    default_regions = {
        "Region": [],
        "Women Asked": []
    }

    df = pd.DataFrame(regions or default_regions)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['Women Asked'],
        y=df['Region'],
        text=[f'{x:,} Women' for x in df['Women Asked']],
        textposition='inside',
        orientation='h',
        marker_color='#ff4b4b',  # Blue color similar to the image
        hovertemplate='%{y}: %{x:,} Women<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(text="<i>Regions sample summary</i>", x=0.5,xanchor="center"),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels as they're redundant with the bar labels
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            tickmode='array',
            ticktext=df['Region'],
            tickvals=df['Region'],
            showgrid=False
        ),
        plot_bgcolor='white',
        showlegend=False
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True,  key="regions_summary")


def pregnancy_choropleth_map(records: List):
    rwanda_districts = json.load(open("./District_Boundaries.geojson", "r"))
    district_idmap = {}

    # Add ID column and Map district to id
    for feature in rwanda_districts["features"]:
        feature["id"] = feature["properties"]["objectid"]
        district_idmap[feature["properties"]["district"]] = feature["id"]

    grouped_districts_records = appl.create_upload_summary(records, "district")
    df = pd.DataFrame(grouped_districts_records)

    # Add ID to Pregnancy dataframe
    df["id"] = df["district"].apply(lambda x: district_idmap[x.capitalize()])
    df["district"] = df["district"].apply(lambda x: str(x).capitalize())
    df["pregnacy_percentage"] = round((df["pregnant_count"]/df["women_count"])* 100, 1)
    df["literacy_percentage"] = round((df["literacy_count"]/df["women_count"])* 100, 1)

    fig = px.choropleth_mapbox(
            df,
            locations= "id",
            geojson= rwanda_districts,
            color="pregnacy_percentage",
            hover_name= "district",
            hover_data= ["women_count", "literacy_percentage"],
            center={"lat":-1.94, "lon": 29.87},
            color_continuous_scale= [[0, '#d8acac'], [0.5, '#f89a9a'], [1.0, '#c61818']],
            color_continuous_midpoint=0,
            mapbox_style="carto-positron",
            labels= {
                "women_count": "Total Women", 
                "pregnacy_percentage": "Pregnancy(%)",
                "literacy_percentage": "Literacy(%)"
            },
            zoom = 7
        )
    
    fig.update_layout(
        title=dict(text="<i>Pregnancy and districts map</i>", x=0.5,xanchor="center"),
        coloraxis_showscale=False,  # This line removes the colorscale
        height = 400,
        showlegend = False,
        margin=dict(t=50, b=0, l=0, r=0),
    )
    
    fig.update_geos(
        fitbounds = "locations",
        visible = False,
    )
    st.plotly_chart(fig, key="pregnancy_choropleth", use_container_width= True)