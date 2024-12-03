import streamlit as st
from typing import List
from collections import defaultdict
from streamlit_extras.metric_cards import style_metric_cards

# Define custom styles for metrics
def custom_metric(label, value, color):
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px;margin-bottom:15px">
        <p style="margin: 0; font-size: 14px; color: #666;font-weight: bold">{label}</p>
        <p style="margin: 0; font-size: 24px; font-weight: bold; color: {color};">{value}</p>
    </div>
    """, unsafe_allow_html=True)


def calculate_increate(datas: List, attr1:str):
    try:
        # Get pregnancy counts for the earliest and latest year
        summary = create_upload_summary(datas, "survey_round")

        # Sort them by interview year
        summary = sorted(summary, key=lambda x: x["year"])

        earliest_data = summary[0][attr1]
        latest_data = summary[-1][attr1]

        # Calculate absolute and percentage increase
        absolute_increase = latest_data - earliest_data
        percentage_increase = (absolute_increase / earliest_data) * 100

        return percentage_increase
    
    except:
        return 0


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
    

def records_based_onyears(records:List, years: List, key_name: str)->List:
    return [data for data in records if data[key_name] in years] # return array of data for particular year


def records_grouped_by_district(records: List, attr: str = "district"):      
        # Use defaultdict to group by district
        grouped_data = defaultdict(list)
        for record in records:
            grouped_data[str(record[attr]).lower()].append(record)
        
        # Convert defaultdict to a regular dict
        return dict(grouped_data)

# COUNT PARTICULAR VALUES IN TABLE COLUMN
def count_frequency(table_datas: List, column: str, value):
    return int(round(sum(data["weights"] for data in table_datas if str(data[column]).lower() == value), 0))

def total_weights(table_datas: List):
    return int(round(sum(data["weights"] for data in table_datas), 0))

# Custom function to find the nearest year divisible by 5
def find_nearest_year(year):
    if year % 5 == 0:
        return year
    else:
        next_year = (year // 5 + 1) * 5  # Next closest year divisible by 5
        prev_year = (year // 5) * 5      # Previous closest year divisible by 5
        return next_year if abs(next_year - year) < abs(prev_year - year) else prev_year


#CREATE UPLOAD SUMMARY
def create_upload_summary(arr_records: List, group_name: str):
        
    # Initialize a defaultdict with default values
    result = defaultdict(lambda: {
                "ages": 0, 
                "pregnant_count": 0, 
                "women_count": 0,
                "literacy_count": 0,
                "survey_round": "",
                "year": 0,
                "district": ""
            })

    for record in arr_records:
        if record["age_range"] != "15-19":
            continue

        filter_name = str(record[group_name]).lower()

        #Survey Round
        if group_name == "survey_round":
            result[filter_name]["survey_round"] = record["survey_round"]

        #District
        result[filter_name]["district"] = filter_name

        #Year
        result[filter_name]["year"] = record["interview_year"]

        #Ages
        result[filter_name]["ages"] = record["current_age"]

        #Pregnant count
        if record["currently_pregnant"].lower() == "yes":
            result[filter_name]["pregnant_count"] += record["weights"]

        #Women count
        result[filter_name]["women_count"] += record["weights"]

        #Female educated count
        if str(record["literacy"]).lower() != "no":
            result[filter_name]["literacy_count"] += record["weights"]

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
    

#METRICS CARDS
def metric_cards():
    filtered_records = st.session_state.filtered_records
    pregnant_teenagers = count_frequency(filtered_records, "currently_pregnant", "yes")

    #totoal teenagers and total educated teenagers
    total_educated = count_frequency(filtered_records, "literacy", "yes")
    total_teenager = total_weights(filtered_records)


    percentage_educated = (total_educated * 100) // (total_teenager or 1)

    #Pregnancy increase
    pregnancy_increase = calculate_increate(filtered_records, "pregnant_count")
    educated_increase = calculate_increate(filtered_records, "literacy_count")
    teenage_increase = calculate_increate(filtered_records, "women_count")

    # Create columns
    col1, col2, col3 = st.columns(3)

    # Metrics cards over different columns
    col1.metric("Teenage Pregnancy", "{:,}".format(int(pregnant_teenagers)), "{:,.2f}%".format(pregnancy_increase))
    col2.metric("Literate Teenagers", "{:,}%".format(int(percentage_educated)), "{:,.2f}%".format(educated_increase))
    col3.metric("Female Teenagers", "{:,}".format(int(total_teenager)), "{:,.2f}%".format(teenage_increase))

    style_metric_cards(background_color="auto")


def filter_records_basedon_periods(years_records: List):
    # Get data for District in View
    district = st.session_state.session_district
    
    if district == "All Districts":
        st.session_state.filtered_records = years_records
    
    else:
        district_data = records_grouped_by_district(years_records)[str(district).lower()]
        st.session_state.filtered_records = district_data


# PROJECT SIDEBAR
def project_sidebar(db_records, theme):
    # Needed data
    years = list({entry["survey_round"] for entry in db_records})
    ages = list({entry["current_age"] for entry in db_records})
    

    # Display logo
    if theme:
        st.logo(f"{'./static/data_wizards_light.png' if theme["base"] == "light" else './static/data_wizards_dark.png'}")
    
    # Sub Title
    st.markdown("<p style='text-align: center;'>Teenage Pregnancy</p>", unsafe_allow_html=True)

    #Years Filter
    years_options = st.multiselect(
        "Select Survey period",
        years,
        years[:2],
    )

    #Ages Filter
    ages_filter = st.multiselect(
        "Select Ages",
        ages,
        ages,
    )

    search_district = st.text_input("Search District", placeholder="Kicukiro")

    # Filter records by Years Options
    filtered_records = records_based_onyears(db_records, years_options, "survey_round")

    #Filter records by age Options
    filtered_records = records_based_onyears(filtered_records, ages_filter, "current_age")
    st.session_state.years_age_filter = filtered_records

    # Group districts
    districts_groups = records_grouped_by_district(filtered_records)

    if search_district:  #Search Functionality
        districts_groups = search_surveys_district(districts_groups, search_district.lower())
        if isinstance(districts_groups, str):
            st.error(districts_groups)
            return
    else:
        districts_groups = records_grouped_by_district(filtered_records)

    

    if years_options:
        # update session state
        filter_records_basedon_periods(filtered_records)

        st.markdown(f"""
            <div style="margin:0; border-bottom:1px solid rgba(0,0,0,0.2); padding-bottom:5px;margin-top:10px;margin-bottom:5px">
                <p style="margin:0; padding:0;font-weight:bold"> All Districts</p>
                <p style="margin:0; padding:0; margin-top:0">{min(years_options)} - {max(years_options)}: <span style="color: #ff4b4b;font-weight: bold">{"{:,.0f}".format(count_frequency(filtered_records, "currently_pregnant", "yes"))} Pregnancy</span></p>
                <p style="margin:0; padding:0; margin-top:0">Total: { "{:,.0f}".format(len(filtered_records)) } Female Teenagers</p>
            </div>
            """, unsafe_allow_html=True)

        if st.button("View Details", key = "All Districts"):
            st.session_state.filtered_records = filtered_records
            st.session_state.session_district = "All Districts"


        for district, records in districts_groups.items():
            pregnancy_count = count_frequency(records, "currently_pregnant", "yes")
            total_teenagers = total_weights(records)
            
            st.markdown(f"""
            <div style="margin:0; border-bottom:1px solid rgba(0,0,0,0.2); padding-bottom:5px;margin-top:10px;margin-bottom:5px">
                <p style="margin:0; padding:0;font-weight:bold">{ district.capitalize() }</p>
                <p style="margin:0; padding:0; margin-top:0">{min(years_options)} - {max(years_options)}: <span style="color: #ff4b4b;font-weight: bold">{ "{:,.0f}".format(pregnancy_count) } Pregnancy</span></p>
                <p style="margin:0; padding:0; margin-top:0">Total Female: { "{:,.0f}".format(total_teenagers) } Teenagers</p>
            """, unsafe_allow_html=True)

            if st.button("View Details", key = district):
                st.session_state.filtered_records = records
                st.session_state.session_district = str(district).capitalize()


def calculate_preg_percentages(pregnancy_records, women_records):
    percentage = []
    for i in range(min(len(pregnancy_records), len(women_records))):
        percentage.append(round((pregnancy_records[i] * 100) / (women_records[i] or 1), 1))
    
    return percentage