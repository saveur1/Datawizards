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

    trace_colors =  ['rgb(217, 217, 217)', '005cab']
    pie_chart_data = [total_women - pregnant_count, pregnant_count]
    chart_title = f"Pregnancies for { st.session_state.session_district } in { st.session_state.session_survey }"
    chart_labels = ['Not Pregnant cases', 'Pregnant cases']

    trace = go.Pie(
        labels=chart_labels, 
        values=pie_chart_data, 
        hole=0.5, 
        marker_colors=trace_colors
    )

    # Create the layout for the chart
    layout = go.Layout(
        title=dict(
            text=f'<i>{chart_title}<i>',
            x=0.5,
            xanchor="center"
        ),
        showlegend=True,  # Show the legend
        margin=dict(l=0, r=10, b=10, t=40),
        width=300,  # Set the desired width
        height=260,  # Set the desired height
        legend=dict(
            orientation="h",  # Horizontal orientation
            x=0.5,  # Center the legend horizontally
            xanchor="center",
            y=-0.1,  # Place the legend below the chart
        ),
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



def teenage_pregnancy_history(records):
    #state variable
    filtered_records = records
    district = st.session_state.session_district
    survey_name = st.session_state.session_survey

    countries = list({record["country"] for record in st.session_state.filtered_records })


    if district != "All Districts":
        filtered_records = [data for data in records if str(data["district"]).lower() == str(district).lower()]
    
    # filter out ages and countries
    selsected_ages = list({ record["current_age"] for record in st.session_state.filtered_records})
    filtered_records = [record for record in records if ( record["current_age"] in selsected_ages and record["country"] in countries ) ]
    
    # Get pregnancy counts for the earliest and latest year
    summary = app_logic.create_upload_summary(filtered_records, "survey_round")

    # Sort them by interview year
    summary = sorted(summary, key=lambda x: x["year"])

    # Find the current entry index
    current_index = next((i for i, entry in enumerate(summary) if entry["survey_round"] == survey_name), None)
    
    # Redefine summary data to stop at currently selected survey period
    summary = summary[:current_index+1]

    # Survey round array
    survey_rounds: list[str] = ["R-"+data["survey_round"]  for data in summary ]

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
        yaxis_title="Currently pregnant Teenager",
        xaxis_title="Survey Periods",
        legend=dict(yanchor="top", y=-1, xanchor="center", x=0.5))
    
    st.plotly_chart(fig, use_container_width=True, key="CHART1")

def education_statistics():
        # Description of Chat
    st.info(
        "This chart shows the education levels of young women aged 15-19 who have had one or more children, or are currently pregnant for the first time."
    )
        
    # Assume `records` contains the data as a list of dictionaries
    records = st.session_state.filtered_records  # Example: [{'education_level': 'High School', 'currently_pregnant': 1}, ...]

    # Group data by education level
    education_groups = defaultdict(list)
    for record in records:
        education_groups[record["education_level"]].append(record)

    # Calculate statistics
    education_levels = defaultdict(list)
    total_women = len(records)  # Total number of women in the dataset

    for level, group in education_groups.items():
        total_in_group = len(group)
        currently_pregnant = sum(1 for record in group if record["living_current_pregnancy"] >= 1)
        percentage_pregnant = (currently_pregnant / total_women * 100) if total_women > 0 else 0

        education_levels["Education Level"].append(str(level).capitalize())
        education_levels["Total Women"].append(total_in_group)
        education_levels["Pregnant Women"].append(currently_pregnant)
        education_levels["Percentage Pregnant"].append(percentage_pregnant)

    # Create the DataFrame
    default_ed = {
        "Education Level": [],
        "Total Women": [],
        "Pregnant Women": [],
        "Percentage Pregnant": []
    }

    df_education = pd.DataFrame(dict(education_levels) or default_ed)
    df_education = df_education.sort_values(by="Percentage Pregnant", ascending=True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_education["Percentage Pregnant"],
        y=df_education["Education Level"],
        text=[f'{x:.2f}%' for x in df_education["Percentage Pregnant"]],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(text=f"<i>Childbearing Rates by Education Level in {st.session_state.session_district}</i>", 
        x=0.5, xanchor="center"),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            title="Percentage of Women",
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Education Level",
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

def wealth_quantile_chart():
        # Description of Chat
    st.info(
        "This chart shows the wealth quintile of young women aged 15-19 who have had one or more children, or are currently pregnant for the first time."
    )
        
    # Assume `records` contains the data as a list of dictionaries
    records = st.session_state.filtered_records  # Example: [{'education_level': 'High School', 'currently_pregnant': 1}, ...]

    # Group data by wealth_category
    regions_groups = defaultdict(list)
    for record in records:
        regions_groups[record["wealth_quintile"]].append(record)

    # Calculate statistics
    regions = defaultdict(list)
    total_women = len(records)  # Total number of women in the dataset

    for level, group in regions_groups.items():
        total_in_group = len(group)
        currently_pregnant = sum(1 for record in group if record["living_current_pregnancy"] >= 1)
        percentage_pregnant = (currently_pregnant / total_women * 100) if total_women > 0 else 0

        regions["wealth_category"].append(str(level).capitalize())
        regions["Total Women"].append(total_in_group)
        regions["Pregnant Women"].append(currently_pregnant)
        regions["Percentage Pregnant"].append(percentage_pregnant)

    # Create the DataFrame
    default_ed = {
        "wealth_category": [],
        "Total Women": [],
        "Pregnant Women": [],
        "Percentage Pregnant": []
    }

    df_wealth = pd.DataFrame(dict(regions) or default_ed)
    df_wealth = df_wealth.sort_values(by="Percentage Pregnant", ascending=True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_wealth["Percentage Pregnant"],
        y=df_wealth["wealth_category"],
        text=[f'{x:.2f}%' for x in df_wealth["Percentage Pregnant"]],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(text=f"<i>Pregnancy and Childbearing Rates by wealth_category in {st.session_state.session_district}</i>", 
        x=0.5, xanchor="center"),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            title="Percentage of Women",
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Wealth category",
            tickmode='array',
            ticktext=df_wealth["wealth_category"],
            tickvals=df_wealth["wealth_category"],
            showgrid=False
        ),
        plot_bgcolor='white',
        showlegend=False
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True, key="wealthQ")

def age_group_chart():
    st.info(
        "This graph shows the percentage of young women aged 15-19 who have begun childbearing, including those with children or pregnant for the first time. Percentages vary by age group based on data filters"
    )
    # Retrieve filtered records and survey year
    records = st.session_state.filtered_records  # Example: [{'current_age': 25, 'living_current_pregnancy': 1}, ...]
    
    # Group records by current age
    age_groups = defaultdict(list)
    for record in records:
        age_groups[record["current_age"]].append(record)

    # Calculate statistics for each age group
    age_data = defaultdict(list)
    for age, group in age_groups.items():
        total_in_group = len(group)  # Total women in this specific age group
        currently_pregnant = sum(record["weights"] for record in group if record["living_current_pregnancy"] >= 1)  # Pregnant women in this age group
        percentage_pregnant = round((currently_pregnant / total_in_group * 100)) if total_in_group > 0 else 0  # Percentage for this age group

        # Populate the data
        age_data["Age Group"].append(age)
        age_data["Total Women"].append(total_in_group)
        age_data["Pregnant Women"].append(currently_pregnant)
        age_data["Percentage Pregnant"].append(percentage_pregnant)

    # Create the DataFrame
    default_data = {
        "Age Group": [],
        "Total Women": [],
        "Pregnant Women": [],
        "Percentage Pregnant": []
    }

    df_age = pd.DataFrame(dict(age_data) or default_data)
    df_age = df_age.sort_values(by="Percentage Pregnant", ascending=True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_age["Percentage Pregnant"],
        y=df_age["Age Group"],
        text=[f'{x:.2f}%' for x in df_age["Percentage Pregnant"]],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"<i>Pregnancy Rates by Age Group</i>", 
            x=0.5, 
            xanchor="center"
        ),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            title="Percentage of Women",
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Age Group",
            tickmode='array',
            ticktext=df_age["Age Group"],
            tickvals=df_age["Age Group"],
            showgrid=False
        ),
        plot_bgcolor='white',
        showlegend=False
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True, key="age_group")
def province_chart():
    st.info(
        "This graph shows the percentage of young women aged 15-19 who have started childbearing, including those with children or pregnant for the first time. Percentages vary by province based on data filters"
    )
    # Retrieve filtered records and survey year
    records = st.session_state.filtered_records  # Example: [{'province': 'Kigali', 'living_current_pregnancy': 1}, ...]

    # Group records by province
    province_groups = defaultdict(list)
    for record in records:
        province_groups[record["regions"]].append(record)

    # Calculate statistics for each province
    province_data = defaultdict(list)
    for province, group in province_groups.items():
        total_in_group = len(group)  # Total women in this specific province
        currently_pregnant = sum(record["weights"] for record in group if record["living_current_pregnancy"] >= 1)  # Pregnant women in this province
        percentage_pregnant = round((currently_pregnant / total_in_group * 100), 2) if total_in_group > 0 else 0  # Rounded percentage for this province

        # Populate the data
        province_data["Province"].append(province)
        province_data["Total Women"].append(total_in_group)
        province_data["Pregnant Women"].append(currently_pregnant)
        province_data["Percentage Pregnant"].append(percentage_pregnant)

    # Create the DataFrame
    default_data = {
        "Province": [],
        "Total Women": [],
        "Pregnant Women": [],
        "Percentage Pregnant": []
    }

    df_province = pd.DataFrame(dict(province_data) or default_data)
    df_province = df_province.sort_values(by="Percentage Pregnant", ascending=True)

    # Create the bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_province["Percentage Pregnant"],
        y=df_province["Province"],
        text=[f'{x:.2f}%' for x in df_province["Percentage Pregnant"]],
        textposition='inside',
        orientation='h',
        marker_color='#005cab',
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"<i>Pregnancy Rates by Province</i>",
            x=0.5,
            xanchor="center"
        ),
        height=300,
        margin=dict(t=60, b=50, l=0, r=30),
        xaxis=dict(
            title="Percentage of Women",
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Province",
            tickmode='array',
            ticktext=df_province["Province"],
            tickvals=df_province["Province"],
            showgrid=False
        ),
        plot_bgcolor='white',
        showlegend=False
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True, key="province_group")



def pregnancy_choropleth_map():
    records = st.session_state.years_age_filter
    selected_district_name = st.session_state.session_district  # Selected district or "All Districts"
    
    rwanda_districts = json.load(open("./District_Boundaries.geojson", "r"))
    district_idmap = {}

    incoming_districts = list({str(record["district"]).capitalize() for record in records})

    # Add ID column and Map district to id
    for feature in rwanda_districts["features"]:
        if feature["properties"]["district"] not in incoming_districts:
            return "Not plotted"
        
        feature["id"] = feature["properties"]["objectid"]
        district_idmap[feature["properties"]["district"]] = feature["id"]

    # Description of map
    st.info(
        "This map provides insights into district-level pregnancy data. **Darker colors** indicate higher pregnancy rates, while **lighter colors** represent lower rates. **Hover for details.**"
    )
        
    grouped_districts_records = app_logic.create_upload_summary(records, "district")  # Group all data by districts
    df = pd.DataFrame(grouped_districts_records)
    
    df["women_count"] = df["women_count"].apply(lambda x: int(round(x, 0)))

    # Add ID to Pregnancy dataframe
    if grouped_districts_records:
        df["id"] = df["district"].apply(lambda x: district_idmap[str(x).capitalize()])
        df["district"] = df["district"].apply(lambda x: str(x).capitalize())
        df["pregnacy_percentage"] = round((df["pregnant_count"] / df["women_count"]) * 100, 1)
        df["childbearing_percentage"] = round((df["child_bearing"] / df["women_count"]) * 100, 1)
        
        # Format percentages as strings with %
        df["pregnacy_percentage_label"] = df["pregnacy_percentage"].apply(lambda x: f"{x}%")
        df["childbearing_percentage_label"] = df["childbearing_percentage"].apply(lambda x: f"{x}%")
        
        # Conditional logic for color scale or highlight map
        if selected_district_name == "All Districts":
            # Continuous color scale map
            color_col = "pregnacy_percentage"
            color_map = px.colors.sequential.Blues
            color_scale_flag = True
            hover_data = {
                "women_count": True,
                "pregnacy_percentage_label": True,
                "childbearing_percentage_label": True,
                "pregnacy_percentage": False,
                "id": False,
            }
        else:
            # Highlight specific district
            df["is_selected"] = df["district"].apply(lambda x: x == selected_district_name.capitalize())
            df["color"] = df["is_selected"].apply(lambda x: st.session_state.session_district if x else "Else")  # Highlight selected district
            color_col = "color"
            color_map = {"red": "red", "blue": "blue"}  # Discrete color map
            color_scale_flag = False
            hover_data = {
                "women_count": True,
                "pregnacy_percentage_label": True,
                "childbearing_percentage_label": True,
                "pregnacy_percentage": False,
                "id": False,
                "color": False,  # Exclude color from hover data
            }
        
        fig = px.choropleth_mapbox(
            df,
            locations="id",
            geojson=rwanda_districts,
            color=color_col,
            hover_name="district",
            hover_data=hover_data,
            center={"lat": -1.94, "lon": 29.87},
            color_continuous_scale=color_map if color_scale_flag else None,
            mapbox_style="carto-positron",
            labels={
                "women_count": "Total Cases",
                "pregnacy_percentage_label": "Pregnancy",
                "childbearing_percentage_label": "Child Bearing"
            },
            zoom=7
        )
        
        fig.update_layout(
            title=dict(
                text=f"<i>Pregnancy Rates by { st.session_state.session_district }: {st.session_state.session_survey} Survey</i>",
                x=0.5,
                xanchor="center"
            ),
            coloraxis_showscale=color_scale_flag,  # Show scale for continuous map
            height=400,
            showlegend=not color_scale_flag,  # Disable legend for discrete map
            margin=dict(t=50, b=0, l=0, r=0),
        )
        
        st.plotly_chart(fig, key="pregnancy_choropleth", use_container_width=True)



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
