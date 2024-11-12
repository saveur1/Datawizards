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


def calculate_increate(data: List, attr1:str, attr2:str = None):
    # Sort data by year
    data_sorted = sorted(data, key=lambda x: x["year"])

    # Get pregnancy counts for the earliest and latest year
    earliest_data = data_sorted[0][attr1]
    latest_data = data_sorted[-1][attr1]

    if attr2:
        earliest_data += data_sorted[0][attr2]
        latest_data += data_sorted[-1][attr2]

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
    return [data for data in records if data["year"] in years]


def records_grouped_by_district(records: List):      
        # Use defaultdict to group by district
        grouped_data = defaultdict(list)
        for record in records:
            grouped_data[record["district"]].append(record)
        
        # Convert defaultdict to a regular dict
        return dict(grouped_data)

def fill_records_database(arr_records: List):
        
        # Initialize a defaultdict with two levels of nesting
        result = defaultdict(lambda: defaultdict(lambda: {
            "district": None, 
            "year": 0, 
            "pregnant_count": 0, 
            "male_educated": 0,
            "female_educated": 0
        }))
    
        for record in arr_records:
            if record["age-range"] != "15-19":
                continue

            district = record["districts"]  #v023 contains districts
            years = record["years"]  #v007 contains years

            #Districts
            result[years][district]["district"] = district

            #Years
            result[years][district]["year"] = record["years"] #v007 contains years

            #Pregnant count
            if record["currently-pregnant"] == "yes":
                result[years][district]["pregnant_count"] += 1



        print([result for data in dict(result).values() for result in list(dict(data).values())])
