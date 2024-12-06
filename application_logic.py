import streamlit as st
from typing import List
from collections import defaultdict
from streamlit_extras.metric_cards import style_metric_cards



def calculate_increate(db_records, attr1:str):
    survey_name = st.session_state.session_survey
    country = list({record["country"] for record in st.session_state.filtered_records})
    db_records = [record for record in db_records if record["country"] in country]
    
    try:
        # Get pregnancy counts for All data in database
        summary = create_upload_summary(db_records, "survey_round")

        # Sort them by interview year
        summary = sorted(summary, key=lambda x: x["survey_round"])
        
        # Find the current entry index
        current_index = next((i for i, entry in enumerate(summary) if entry["survey_round"] == survey_name), None)

        if current_index is None or current_index == 0:
            # No previous survey to compare or invalid entry
            return 0
        
        # Get the previous survey
        previous_entry = summary[current_index - 1]  
        current_entry = summary[current_index]
        
        # Calculate percentage change
        previous_attr = previous_entry[attr1]
        previous_total = previous_entry["women_count"]

        current_attr = current_entry[attr1]
        current_total = current_entry["women_count"]

        if attr1 == "women_count":
            return current_total - previous_total


        if previous_attr == 0:
            return 0  # Avoid division by zero

        # percentages
        previous_year_percent = (previous_attr / previous_total) * 100
        current_year_percent = (current_attr / current_total) * 100
        
        return current_year_percent - previous_year_percent
    
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
    

def records_based_onyears(records:List, options: List, key_name: str)->List:
    return [data for data in records if data[key_name] in options] # return array of data for particular year


def records_grouped_by(records: List, attr: str = "district"):      
        # Use defaultdict to group by district
        grouped_data = defaultdict(list)
        for record in records:
            grouped_data[str(record[attr]).lower()].append(record)
        
        # Convert defaultdict to a regular dict
        return dict(grouped_data)

# COUNT PARTICULAR VALUES IN TABLE COLUMN
def count_frequency(table_datas: List, column: str, value):
    return int(round(sum(data["weights"] for data in table_datas if str(data[column]).lower() == value), 1))

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
                "district": "",
                "child_bearing": 0,
                "country": ""
            })

    for record in arr_records:
        if record["age_range"] != "15-19":
            continue

        filter_name = str(record[group_name]).lower()

        #Survey Round
        if group_name == "survey_round" or group_name == "district":
            result[filter_name]["survey_round"] = record["survey_round"]

        #District
        result[filter_name]["district"] = filter_name

        # Year
        result[filter_name]["year"] = record["interview_year"]

        # Ages
        result[filter_name]["ages"] = record["current_age"]

        # Pregnant count
        if record["currently_pregnant"].lower() == "yes":
            result[filter_name]["pregnant_count"] += record["weights"]

        # Women count
        result[filter_name]["women_count"] += record["weights"]

         # Country
        if "country" in record:
            result[filter_name]["country"] = record["country"]

        # Childbearing count
        if "living_current_pregnancy" in record:
            if int(record["living_current_pregnancy"]) > 0:
                result[filter_name]["child_bearing"] += record["weights"]

        # Female educated count
        if "literacy" in record:
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
def metric_cards(db_records: List):
    filtered_records = st.session_state.filtered_records
    survey_name = st.session_state.session_survey

    #total teenagers and total child bearing
    total_child_bearing = sum([record["weights"] for record in filtered_records if int(record["living_current_pregnancy"])>0])
    total_teenager = total_weights(filtered_records)
    pregnant_teenagers = count_frequency(filtered_records, "currently_pregnant", "yes")

    # Precentages
    percentage_child_bearing = get_percentage(total_child_bearing, total_teenager)
    percentage_pregnancies = get_percentage(pregnant_teenagers, total_teenager)

    #Pregnancy increase
    pregnancy_increase = calculate_increate(db_records, "pregnant_count")
    educated_increase = calculate_increate(db_records, "child_bearing")
    teenage_increase = calculate_increate(db_records, "women_count")

    # Create columns
    col1, col2, col3 = st.columns(3)

    # Metrics cards over different columns
    col1.metric(f"Child bearing in { survey_name }", "{:,.1f}%".format(percentage_child_bearing), "{:,.2f}%".format(educated_increase))
    col2.metric(f"Teen Pregnancy in { survey_name }", "{:,.1f}%".format(percentage_pregnancies), "{:,.2f}%".format(pregnancy_increase))
    col3.metric("Female Teenagers", "{:,}".format(int(total_teenager)), "{:,.0f}".format(teenage_increase))

    style_metric_cards(background_color="auto")


def filter_records_basedon_periods(years_records: List):
    # Get data for District in View
    district = st.session_state.session_district
    
    if district == "All Districts":
        st.session_state.filtered_records = years_records
    
    else:
        if str(district).lower() in records_grouped_by(years_records):
            district_data = records_grouped_by(years_records)[str(district).lower()]
            st.session_state.filtered_records = district_data
        else:
            st.session_state.session_district = "All Districts"
            st.session_state.filtered_records = years_records

def get_percentage(value: float, total: float):
    return ( value / (total or 1) ) * 100

# PROJECT SIDEBAR
def project_sidebar(db_records: List, theme):
    # Needed data
    ages = list({entry["current_age"] for entry in db_records})
    country_datas = list({entry["country"] for entry in db_records})
    

    # Display logo
    if theme:
        st.logo(f"{'./static/data_wizards_light.png' if theme["base"] == "light" else './static/data_wizards_dark.png'}")
    
    # Sub Title
    st.markdown("<p style='text-align: center;'>Teenage Pregnancy</p>", unsafe_allow_html=True)
    
    #Years Filter
    country_option = st.selectbox(
        "Select Country",
        country_datas,
    )

    # Filter records by Selected country
    filtered_records = records_based_onyears(db_records, country_option, "country")
    survey_round_datas = sorted(list({entry["survey_round"] for entry in filtered_records}), reverse=True)

    #Years Filter
    survey_options = st.selectbox(
        "Select Survey period",
        survey_round_datas,
    )
    st.session_state.session_survey = survey_options

    #Ages Filter
    ages_filter = st.multiselect(
        "Select Ages",
        ages,
        ages,
    )

    search_district = st.text_input("Search District", placeholder="Kicukiro")

    # Filter records by Selected Survey Options
    filtered_records = records_based_onyears(db_records, survey_options, "survey_round")

    #Filter records by age Options
    filtered_records = records_based_onyears(filtered_records, ages_filter, "current_age")
    
    # Update survey_and_age session state
    st.session_state.years_age_filter = filtered_records

    # Group districts
    districts_groups = records_grouped_by(filtered_records)

    if search_district:  #Search Functionality
        districts_groups = search_surveys_district(districts_groups, search_district.lower())
        if isinstance(districts_groups, str):
            st.error(districts_groups)
            return
    else:
        districts_groups = records_grouped_by(filtered_records)

    

    if survey_options:
        # update session state
        filter_records_basedon_periods(filtered_records)

        st.markdown(f"""
            <div style="margin:0; border-bottom:1px solid rgba(0,0,0,0.2); padding-bottom:5px;margin-top:10px;margin-bottom:5px">
                <p style="margin:0; padding:0;font-weight:bold"> All Districts</p>
                <p style="margin:0; padding:0; margin-top:0">{ survey_options }: <span style="color: #005cab;font-weight: bold">{"{:,.0f}".format(count_frequency(filtered_records, "currently_pregnant", "yes"))} Pregnancy</span></p>
                <p style="margin:0; padding:0; margin-top:0">Total: { "{:,.0f}".format(total_weights(filtered_records)) } Female Teenagers</p>
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
                <p style="margin:0; padding:0;font-weight:bold">{ str(district).capitalize() }</p>
                <p style="margin:0; padding:0; margin-top:0">{ survey_options }: <span style="color: #005cab ;font-weight: bold">{ "{:,.0f}".format(pregnancy_count) } Pregnancy</span></p>
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

def get_districts_string(records: List, survey_name: str):
    output = f"The following are data for { survey_name } Survey round in each district: \n\n"

    for record in records:
        # Stringify record
        output += (f"{record["district"]} District:\nPregnant Count={int(round(record["pregnant_count"], 0))},\n "
                   f"Total Women Teenager Count={int(round(record["women_count"], 0))}, \nTotal Female Who begun Child bearing={ int(round(record["child_bearing"], 0))}, \n"
                   f"Survey Round='{record["survey_round"]}',\nCountry='{record["country"]}'\n\n")
    
    return output

def get_country_string(records: List, country: str, survey: str):
    output = f"\nThe following are summary list of data where country is { country }, for { survey }  survey round:"

    for record in records:
        # Stringify record
        child_bearing_percentage = ( record["child_bearing"]/ (record["women_count"] or 1) ) * 100
        pregnant_percentage = ( record["pregnant_count"]/ (record["women_count"] or 1) ) * 100
        
        output += (f"\nPercentage Pregnant={int(round(pregnant_percentage, 0))}%, \n"
                   f"Total Women Teenager Count={int(round(record["women_count"], 0))}, \nPercentage Who begun Child bearing={ int(round(child_bearing_percentage, 0))}%'\n\n")
    
    return output