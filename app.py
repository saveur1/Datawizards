import streamlit as st
# import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from time import sleep
from streamlit_extras.metric_cards import style_metric_cards
from sqlalchemy.exc import IntegrityError
from typing import List

#Local Imports
import data_injection as datas
import application_logic as appl


st.set_page_config(page_title="Teenage pregnacy prediction",layout="wide",page_icon="🌍")
st.markdown("<style>div.block-container{padding-top:1.4em;}</style>", unsafe_allow_html=True)

#EXTERNAL STYLES
with open("style.css") as t:
    st.markdown(f"<style>{ t.read() }</style>", unsafe_allow_html= True)


# PROJECT SIDEBAR
def project_sidebar(db_records):
    # Needed data
    years = list({entry["survey_round"] for entry in db_records})
    

    # Display logo
    st.logo("./data_wizards.png")
    
    # Sub Title
    st.markdown("<p style='text-align: center;'>Teenage Pregnancy</p>", unsafe_allow_html=True)

    #Years Filter
    years_options = st.multiselect(
        "Select Survey period",
        years,
        years[:2],
    )

    filtered_records = appl.records_based_onyears(db_records, years_options)
    districts_groups = appl.records_grouped_by_district(filtered_records)

    if years_options:
        st.markdown(f"""
            <div style="margin:0; border-bottom:1px solid rgba(0,0,0,0.2); padding-bottom:5px;margin-top:10px;margin-bottom:5px">
                <p style="margin:0; padding:0;font-weight:bold"> All Districts</p>
                <p style="margin:0; padding:0; margin-top:0">{min(years_options)} - {max(years_options)}: <span style="color: red">{"{:,.0f}".format(appl.count_frequency(filtered_records, "currently_pregnant", "yes"))} Pregnancy</span></p>
                <p style="margin:0; padding:0; margin-top:0">Total: { "{:,.0f}".format(len(filtered_records)) } Female Teenagers</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("View Details", key = "All districts"):
            st.session_state.filtered_records = filtered_records

        #District Filter
        for district, records in districts_groups.items():

            pregnancy_count = sum(list({data["pregnant_count"] for data in records}))
            total_teenagers = sum(list({data["female_teenager"] for data in records}))

            st.markdown(f"""
            <div style="margin:0; border-bottom:1px solid rgba(0,0,0,0.2); padding-bottom:5px;margin-top:10px;margin-bottom:5px">
                <p style="margin:0; padding:0;font-weight:bold">{ district }</p>
                <p style="margin:0; padding:0; margin-top:0">{min(years_options)} - {max(years_options)}: <span style="color: red">{ "{:,.0f}".format(pregnancy_count) } Pregnancy</span></p>
                <p style="margin:0; padding:0; margin-top:0">Total Female: { "{:,.0f}".format(total_teenagers) } Teenagers</p>
            """, unsafe_allow_html=True)

            if st.button("View Details", key = district):
                st.session_state.filtered_records = records
            

    #Ages Filter
    ages = st.multiselect(
        "Select Ages",
        ["13", "14", "15", "16", "17", "18"],
        ["13", "14"],
    )


#METRICS CARDS
def metric_cards():
    filtered_records = st.session_state.filtered_records
    pregnant_teenagers = sum(appl.object_values(filtered_records, "pregnant_count"))

    #totoal teenagers and total educated teenagers
    total_educated = sum(appl.object_values(filtered_records, "female_educated", "male_educated"))
    total_teenager = sum(appl.object_values(filtered_records, "female_teenager", "male_teenager"))


    percentage_educated = (total_educated * 100)//total_teenager

    #Pregnancy increase
    pregnancy_increase = appl.calculate_increate(filtered_records, "pregnant_count")
    educated_increase = appl.calculate_increate(filtered_records, "male_educated", "female_educated")
    teenage_increase = appl.calculate_increate(filtered_records, "male_teenager", "female_teenager")

    # Create columns
    col1, col2, col3 = st.columns(3)

    # Metrics cards over different columns
    col1.metric("Teenage Pregnancy", "{:,}".format(int(pregnant_teenagers)), "{:,.2f}%".format(pregnancy_increase))
    col2.metric("Literate Teenagers", "{:,}%".format(int(percentage_educated)), "{:,.2f}%".format(educated_increase))
    col3.metric("Teenage Population", "{:,}".format(int(total_teenager)), "{:,.2f}%".format(teenage_increase))

    style_metric_cards()


# UPLOADED FILE PREVIEW MODAL
@st.dialog("Review Uploaded File", width="large")
def upload_xlsx_file(xlsx_file):
    if xlsx_file is not None:
        # data table
        data_frame = pd.read_excel(xlsx_file)

        # Validate required columns
        required_columns = ['interview-year', 'districts', 'currently-pregnant', 'literacy', 'current-age', 'education-level', 'age-range']
        columns_valid, missing_columns = appl.validate_required_columns(data_frame, required_columns)

        if not columns_valid:
            st.error(f"Invalid file uploaded. Missing required columns: {', '.join(missing_columns)}")
            return
        
        else:
            #Rename Columns to match what's in database
            data_frame = data_frame.rename(columns={
                'interview-year'     : "interview_year", 
                'districts'          : "district", 
                'currently-pregnant' : "currently_pregnant", 
                'literacy'           : "literacy", 
                'current-age'        : "current_age", 
                'education-level'    : "education_level", 
                'age-range'          : "age_range"
            })

            array_data = data_frame.to_dict(orient="records")

            #Remove unwanted records
            array_data = [data for data in array_data if data["current_age"] < 20]

            # create data summary
            appl.create_upload_summary(array_data, "current_age")

            #Input Survey round name
            survey_wave_name = st.text_input("Enter Survey Wave name", placeholder="2019-20")
            
            if st.button("Submit"):
                if not survey_wave_name:
                    st.error("Survey wave name is required to identify different surveys periods!")
                    return;    
                
                try:
                    # Check for existing record with the same Survey wave name
                    exists = datas.session.query(datas.TeenagePregnancy).filter_by(survey_round= survey_wave_name).first()
                    
                    if exists:
                        st.error(f"This survey wave name already exists.")
                        return
                    
                    for data in array_data:
                        data["survey_round"] = survey_wave_name
        
                    datas.insert_multiple_data(array_data)
                    st.success("All records was added in database successfully!")
                    sleep(3)
                    st.rerun()
                
                except IntegrityError:
                    st.error("Error: Some entries for district and year Already exists. Each district-year combination must be unique.")
                    datas.session.rollback()
                
                except Exception as e:
                    datas.session.rollback()
                    raise e  # Re-raise other exceptions


def current_pregnancy_chart():
    trace_colors =  ['rgb(217, 217, 217)', 'rgb(216, 7, 7)']
    trace = go.Pie(labels=['Not Pregnant', 'Pregnant Teenage'], values=[12, 45], hole=0.5, marker_colors= trace_colors)

    # Create the layout for the chart
    layout = go.Layout(
        title=dict(
                text='<i>Current teenager status<i>',
                x=0.5,
                xanchor="center"
            ),
        showlegend=False,  # Hide the legend
        margin=dict(l=0, r=0, b=0, t=40),
        width=300,  # Set the desired width
        height=250,  # Set the desired height
        annotations=[
            dict(
                text=f'{ "{:,}".format(15500) }',
                x=0.5, y=0.5, font_size=20, showarrow=False
            )
        ]
    )

    # Create the figure and plot it using Streamlit
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig, use_container_width=True)


def teenage_pregnancy_history():
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        fill='tozeroy',
        x=["Jan","Feb","Mar","Apr","May","Jun","Juy"],
        y=[12,13,14, 14,17, 17,20],
        mode='lines+markers+text',
        line_color='red'      
    ))

    fig.update_layout(
        width=300,
        height=380,
        title=dict(text="<i>Pregnant teenage History</i>", x=0.5,xanchor="center"),
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
        pregnant_count = sum(appl.object_values(records, "pregnant_count"))

        # Geocode the district name to get latitude and longitude
        
        location = datas.coordinates_for_district(district)
        
        if location:
            lat, lon = location["latitude"], location["longitude"]
    
            generated_datas = np.random.randn(int(pregnant_count), 2) / [40, 40] + [round(lat,2), round(lon, 2)]

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

# PROGRAM STRUCTURE
def main():
    # database access
    db_records = datas.get_table_data()

    if "filtered_records" not in st.session_state:
            st.session_state.filtered_records = db_records

    # project sidebar
    with st.sidebar:
        project_sidebar(db_records)

    # project main content area
    #left side
    cols1, cols2 = st.columns([2,1])
    with cols1:
        #Data intry
        uploaded_file = st.file_uploader("***Upload File***", type=["xls", "xlsx"])

        if uploaded_file is not None:
            upload_xlsx_file(uploaded_file)

        #Metric cards
        metric_cards()

    with cols2:
        # PIE CHART
        current_pregnancy_chart()

        #LINE CHART
        # district_country_chart()

    #right side charts
    # cols3, cols4 = st.columns([2,1])
    # with cols3:
    #     #Heat Map
    #     country_heatmap()
    
    # with cols4:
    #     #LINE CHART
    #     teenage_pregnancy_history()


if __name__ == "__main__":
    #initialize database
    datas.Base.metadata.create_all(bind=datas.engine)

    main()