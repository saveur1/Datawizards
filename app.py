import streamlit as st

#Local Imports
import data_injection as datas
import application_logic as appl
import project_charts as pcharts
from streamlit_theme import st_theme
import project_assistant as assistant

st.set_page_config(page_title="Teenage pregnacy prediction",layout="wide",page_icon="🌍")
st.markdown("<style>div.block-container{padding-top:0em;}</style>", unsafe_allow_html=True)
theme = st_theme()

#EXTERNAL STYLES
with open("./static/style.css") as t:
    st.markdown(f"<style>{ t.read() }</style>", unsafe_allow_html= True)

# PROGRAM STRUCTURE
def main():
    # database access
    db_records = datas.get_table_data()
    chat_messages = [
        {
            "role": "ai",
            "prompt": "What can I help you with?"
        }
    ]

    if "filtered_records" not in st.session_state:
            st.session_state.filtered_records = db_records

    if "session_district" not in st.session_state:
            st.session_state.session_district = "All Districts"
    
    if "session_survey" not in st.session_state:
            st.session_state.session_survey = ""

    if "years_age_filter" not in st.session_state:
            st.session_state.years_age_filter = db_records

    if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = chat_messages

    # project sidebar
    with st.sidebar:
        appl.project_sidebar(db_records, theme)


     # Current district in View
    st.markdown(f"<h6 class='page_title' style='text-align:center;font-weight:normal;font-style: italic'>Displaying data for - <strong>{ st.session_state.session_district }</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Women between 15 and 19 years &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <strong>Weighted data</strong></h6>", unsafe_allow_html= True)

    # project main content area
    #introduce small space
    st.write("")

    #Metric cards, data entry and donut chart for pregnancies
    cols1, cols2 = st.columns([2,1])
    with cols1:
        #Data intry
        uploaded_file = st.file_uploader(f"{"**Upload File**"}", type=["xls", "xlsx", "csv","dta"]) 

        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            try:
                if file_extension in ['xls', 'xlsx']:
                # Process Excel file
                    datas.upload_xlsx_file(uploaded_file)
                    
                elif file_extension == 'csv':
                # Process CSV file
                    datas.upload_csv_file(uploaded_file)
                    
                elif file_extension == 'dta':
                # Process CSV file
                    datas.upload_dta_file(uploaded_file)
                    
                else:
                    st.error("Unsupported file type!")
            except Exception as e:
             st.error(f"An error occurred: {e}")

        #Metric cards
        appl.metric_cards()

    with cols2:
        # Pie chart
        pcharts.current_pregnancy_chart()

    #introduce small space
    st.write("")

    # If No data display Nothing
    if len(st.session_state.filtered_records) < 1:
         return st.error('There are no data found in database', icon="🚨")


    # Heat maps and pregnancy chart history
    cols3, cols4 = st.columns([2,1])
    with cols3:
        #Heat Map
        feedback = pcharts.pregnancy_choropleth_map()
        
        if feedback == "Not ploted":
            pcharts.districts_pregancy_barchat()
    
    with cols4:
        #LINE CHART
        pcharts.teenage_pregnancy_history()

    #introduce small space
    st.write("")

    # education level, provinces and wealth chart
    cols5, cols6 = st.columns([2,1])
    with cols5:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            pcharts.education_statistics()

        with sub_col2:
            pcharts.provinces_statistics()

    with cols6:
        pcharts.wealth_quantile_chart()


    st.button("Ask AI", icon="💬", key="ai_chart_button", type="primary", on_click= assistant.chat_with_assistant, help="Click to chat with datawizard assistant.")


if __name__ == "__main__":
    #initialize database
    datas.Base.metadata.create_all(bind=datas.engine)

    # Load dashboard
    main()