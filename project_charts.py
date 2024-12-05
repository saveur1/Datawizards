import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import numpy as np

#Local Imports
import application_logic as app_logic
from collections import defaultdict

def current_pregnancy_chart():
    # get data from session
    filtered_records = st.session_state.filtered_records
    total_women = app_logic.total_weights(filtered_records)

    # count pregnant teenagers
    pregnant_count = app_logic.count_frequency(filtered_records, "currently_pregnant", "yes")
    literate_count = app_logic.count_frequency(filtered_records, "literacy", "yes")

    trace_colors =  ['rgb(217, 217, 217)', 'rgb(216, 7, 7)']
    pie_chart_data = [total_women - pregnant_count, pregnant_count]
    chart_title = f"Pregnancy chart for { st.session_state.session_district }"
    chart_labels = ['Not Pregnant', 'Pregnant Teenage']

    # left, middle= st.columns(2)
    # if left.button("Pregnancy", use_container_width=True, key="pie_chart_left"):
    #     pie_chart_data = [total_women - pregnant_count, pregnant_count]
    #     chart_title = f"Pregnancy chart for { st.session_state.session_district }"
    #     chart_labels = ['Not Pregnant', 'Pregnant Teenage']
    
    # if middle.button("Literacy", use_container_width=True, key="pie_chart_right"):
    #     pie_chart_data = [literate_count, total_women - literate_count]
    #     chart_title = f"Literacy chart for { st.session_state.session_district }"
    #     chart_labels = ['Able to read', "can't read at all"]

    trace = go.Pie(labels= chart_labels, values = pie_chart_data, hole=0.5, marker_colors= trace_colors)

    # Create the layout for the chart
    layout = go.Layout(
        title=dict(
                text=f'<i>{ chart_title }<i>',
                x=0.5,
                xanchor="center"
            ),
        showlegend= True,
        margin=dict(l=0, r=10, b=10, t=40),
        width=300,  # Set the desired width
        height=260,  # Set the desired height
        annotations=[
            dict(
                text=f'{ "{:,.0f} <br />Total cases".format(total_women) }',
                x=0.5, y=0.5, font_size=20, showarrow=False
            )
        ]
    )

    # Create the figure and plot it using Streamlit
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)


def teenage_pregnancy_history():
    records = st.session_state.years_age_filter
    #state variable
    filtered_records = records
    district = st.session_state.session_district

    if district != "All Districts":
        filtered_records = [data for data in records if str(data["district"]).lower() == str(district).lower()]

    # Get pregnancy counts for the earliest and latest year
    summary = app_logic.create_upload_summary(filtered_records, "survey_round")

    # Sort them by interview year
    summary = sorted(summary, key=lambda x: x["year"])

    # Survey round array
    survey_rounds = ["R_"+data["survey_round"]  for data in summary ]

    # Survey round pregnancy
    survey_pregnancies = [ data["pregnant_count"]  for data in summary ]
    women_records = [ data["women_count"]  for data in summary ]

    survey_pregnacy_result = app_logic.calculate_preg_percentages(survey_pregnancies, women_records)

    # Plot history chart
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        fill='tozeroy',
        x= survey_rounds,
        y= survey_pregnacy_result,
        mode='lines+markers+text',
        line_color='#005cab'      
    ))

    fig.update_layout(
        height=400,
        title=dict(text=f"<i>Pregnancy History for { st.session_state.session_district }(%)</i>", x=0.5,xanchor="center"),
        yaxis_title="Pregnant Teenage",
        legend=dict(yanchor="top", y=-1, xanchor="center", x=0.5))
    
    st.plotly_chart(fig, use_container_width=True, key="CHART1")


def education_statistics():
    records = st.session_state.filtered_records
    #education level grouping
    education_groups = app_logic.records_grouped_by(records, "education_level")
    education_levels = defaultdict(list)
    for level, records in education_groups.items():
        education_levels["Education Level"].append(str(level).capitalize()),
        education_levels["Number of Women"].append(len(records))
    
    default_ed = {
        "Education Level": [],
        "Number of Women": []
    }

    df_education = pd.DataFrame(dict(education_levels) or default_ed)
    df_education = df_education.sort_values(by="Number of Women", ascending= True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_education["Number of Women"],
        y=df_education["Education Level"],
        text=[f'{x:,} Women' for x in df_education["Number of Women"]],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',
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
    

def provinces_statistics():
    records = st.session_state.years_age_filter
    #education level grouping
    regions_groups = app_logic.records_grouped_by(records, "regions")
    regions = defaultdict(list)

    for region, records in regions_groups.items():
        regions["Region"].append(str(region).capitalize()),
        regions["Women Asked"].append(len(records))

    default_regions = {
        "Region": [],
        "Women Asked": []
    }

    df = pd.DataFrame(regions or default_regions)
    df = df.sort_values(by="Women Asked", ascending= True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['Women Asked'],
        y=df['Region'],
        text=[f'{x:,} Women' for x in df['Women Asked']],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',  # Blue color similar to the image
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


def wealth_quantile_chart():
    #education level grouping
    records = st.session_state.filtered_records
    regions_groups = app_logic.records_grouped_by(records, "wealth_quintile")
    regions = defaultdict(list)

    for region, records in regions_groups.items():
        regions["wealth_category"].append(str(region).capitalize()),
        regions["total_women"].append(app_logic.total_weights(records))

    default_wealths = {
        "wealth_category": [],
        "total_women": []
    }

    df = pd.DataFrame(regions or default_wealths)
    df = df.sort_values(by="total_women", ascending=True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['total_women'],
        y=df['wealth_category'],
        text=[f'{x:,} Women' for x in df['total_women']],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',  # Blue color similar to the image
        hovertemplate='%{y}: %{x:,} Women<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(text=f"<i>Wealth Quintile for { st.session_state.session_district }</i>", x=0.5,xanchor="center"),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels as they're redundant with the bar labels
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            tickmode='array',
            ticktext=df['wealth_category'],
            tickvals=df['wealth_category'],
            showgrid=False
        ),
        plot_bgcolor='white',
        showlegend=False
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True,  key="wealth_quantile")



def pregnancy_choropleth_map():
    records = st.session_state.years_age_filter
    rwanda_districts = json.load(open("./District_Boundaries.geojson", "r"))
    district_idmap = {}

    incoming_districts = list({ str(record["district"]).capitalize() for record in records})

    # Add ID column and Map district to id
    for feature in rwanda_districts["features"]:
        if feature["properties"]["district"] not in incoming_districts:
            return "Not ploted"
        
        feature["id"] = feature["properties"]["objectid"]
        district_idmap[feature["properties"]["district"]] = feature["id"]
        
    grouped_districts_records = app_logic.create_upload_summary(records, "district")  #Group all data by districts
    df = pd.DataFrame(grouped_districts_records)
    
    df["women_count"] = df["women_count"].apply(lambda x: int(round(x, 0)))

    # Add ID to Pregnancy dataframe
    if grouped_districts_records:
        df["id"] = df["district"].apply(lambda x: district_idmap[x.capitalize()])
        df["district"] = df["district"].apply(lambda x: str(x).capitalize())
        df["pregnacy_percentage"] = round((df["pregnant_count"]/df["women_count"])* 100, 1)
        df["literacy_percentage"] = round((df["literacy_count"]/df["women_count"])* 100, 1)
    # [[0, '#46e800'], [0.5, '#f3ea00'], [1.0, '#005cab']]
        fig = px.choropleth_mapbox(
                df,
                locations= "id",
                geojson= rwanda_districts,
                color="pregnacy_percentage",
                hover_name= "district",
                hover_data= ["women_count", "literacy_percentage"],
                center={"lat":-1.94, "lon": 29.87},
                color_continuous_scale= px.colors.sequential.Tealgrn,
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
            coloraxis_showscale=True,  # This line removes or show the colorscale
            height = 400,
            showlegend = True,
            margin=dict(t=50, b=0, l=0, r=0),
        )
        
        st.plotly_chart(fig, key="pregnancy_choropleth", use_container_width= True)


def districts_pregancy_barchat():
    records = st.session_state.years_age_filter
    grouped_districts_records = app_logic.create_upload_summary(records, "district")  #Group all data by districts
    
    df = pd.DataFrame(grouped_districts_records)
    df["pregnacy_percentage"] = round((df["pregnant_count"]/df["women_count"])* 100, 1)
    df["district"] =  df["district"].apply(lambda x: str(x).capitalize())

    y_cp = df["pregnacy_percentage"]
    districts = df["district"]


    # Creating Figure Handle
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x= districts,
            y= y_cp,
            name='Percentage Pregnancy',
            marker_color='rgb(40,79,141)',
        ))

    fig.update_layout(
        title=dict(text='Pregnancy and districts chart', xanchor="center", x=0.5),
        xaxis_tickfont_size=14,
        height = 400,
        xaxis=dict(title="Districts"),
        yaxis=dict(
            title='Percentage Pregnancy',
            titlefont_size=20,
            tickfont_size=14,
        ),
        yaxis2=dict(
            title="Percentages(%)",
            overlaying="y",
            side="right"
            ),
        legend=dict(
            xanchor="left",
            yanchor="bottom",
            x=0,
            y=-0.4,
        ),
        template="gridon",
        bargap=0.3, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    st.plotly_chart(fig, use_container_width=True)