import streamlit as st

#Local Imports
import data_injection as datas
import application_logic as appl
import project_charts as pcharts
from streamlit_theme import st_theme

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

    if "filtered_records" not in st.session_state:
            st.session_state.filtered_records = db_records

    if "session_district" not in st.session_state:
            st.session_state.session_district = "All Districts"

    if "years_age_filter" not in st.session_state:
            st.session_state.years_age_filter = db_records

    # project sidebar
    with st.sidebar:
        appl.project_sidebar(db_records, theme)


     # Current district in View
    st.markdown(f"<h6 style='text-align:center;font-weight:normal;font-style: italic'>Displaying data for - <strong>{ st.session_state.session_district }</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Women between 15 and 19 years &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Un-weighted Counting</h6>", unsafe_allow_html= True)

    # project main content area
    #introduce small space
    st.write("")

    #left side
    cols1, cols2 = st.columns([2,1])
    with cols1:
        #Data intry
        uploaded_file = st.file_uploader(f"{"**Upload File**"}", type=["xls", "xlsx"]) 
        if uploaded_file is not None:
            datas.upload_xlsx_file(uploaded_file)

        #Metric cards
        appl.metric_cards()

    with cols2:
        # Pie chart
        pcharts.current_pregnancy_chart()

    #introduce small space
    st.write("")


    # right side charts
    cols3, cols4 = st.columns([2,1])
    with cols3:
        #Heat Map
        pcharts.pregnancy_choropleth_map()
    
    with cols4:
        #LINE CHART
        pcharts.teenage_pregnancy_history()

    #introduce small space
    st.write("")

    cols5, cols6 = st.columns([2,1])
    with cols5:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            pcharts.education_statistics()

        with sub_col2:
             pcharts.provinces_statistics()

    with cols6:
        pcharts.wealth_quantile_chart()


if __name__ == "__main__":
    #initialize database
    datas.Base.metadata.create_all(bind=datas.engine)

    main()