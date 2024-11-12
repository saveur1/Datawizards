import streamlit as st
from typing import List
from collections import defaultdict
import pandas as pd

# Define custom styles for metrics
def custom_metric(label, value, color):
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px;margin-bottom:15px">
        <p style="margin: 0; font-size: 14px; color: #666;font-weight: bold">{label}</p>
        <p style="margin: 0; font-size: 24px; font-weight: bold; color: {color};">{value}</p>
    </div>
    """, unsafe_allow_html=True)


def calculate_increate(data: List, attr1:str):
    # Sort data by year
    data_sorted = sorted(data, key=lambda x: x["interview_year"])

    # Get pregnancy counts for the earliest and latest year
    summary = create_upload_summary(data_sorted, "survey_round")
    earliest_data = summary[0][attr1]
    latest_data = summary[-1][attr1]

    # Calculate absolute and percentage increase
    absolute_increase = latest_data - earliest_data
    percentage_increase = (absolute_increase / earliest_data) * 100

    return percentage_increase


def validate_required_columns(df, required_columns):
    """Check if all required columns exist in the DataFrame"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns


#GET VALUES OF ONE ATTRIBUTE IN OBJECT INTO ARRAY OF VALUES
def object_values(arr: List, attr1: str, attr2: str=""):
    if attr2:
        return [data[attr2]+ data[attr1] for data in arr]
    else:
        return [data[attr1] for data in arr]
    

def records_based_onyears(records:List, years: List)->List:
    return [data for data in records if data["survey_round"] in years]


def records_grouped_by_district(records: List):      
        # Use defaultdict to group by district
        grouped_data = defaultdict(list)
        for record in records:
            grouped_data[record["district"]].append(record)
        
        # Convert defaultdict to a regular dict
        return dict(grouped_data)

# COUNT PARTICULAR VALUES IN TABLE COLUMN
def count_frequency(table_datas: List, column: str, value, reverse: bool = False):
    if reverse:
        return sum(1 for data in table_datas if data[column] != value) 
    return sum(1 for data in table_datas if data[column] == value)


#CREATE UPLOAD SUMMARY
def create_upload_summary(arr_records: List, group_name: str):
        
    # Initialize a defaultdict with two levels of nesting
    result = defaultdict(lambda: {
        "ages": 0, 
        "pregnant_count": 0, 
        "women_count": 0,
        "literacy_count": 0
    })

    for record in arr_records:
        if record["age_range"] != "15-19":
            continue

        filter_name = record[group_name]

        #Ages
        result[filter_name]["ages"] = record["current_age"]

        #Pregnant count
        if record["currently_pregnant"] == "yes":
            result[filter_name]["pregnant_count"] += 1

        #Women count
        result[filter_name]["women_count"] += 1

        #Female educated count
        if record["literacy"] and record["literacy"] != "cannot read at all":
            result[filter_name]["literacy_count"] += 1

    return list(dict(result).values())

# Function to search by partial district name
def search_surveys_district(surveys: List, query:str):
    # Convert query to lowercase for case-insensitive matching
    query = query.lower()
    # Find all districts that contain the query string
    matching_surveys = {district: samples for district, samples in surveys.items() if query in district.lower()}
    
    if matching_surveys:
        return matching_surveys
    else:
        return f"No districts found containing '{query}'"