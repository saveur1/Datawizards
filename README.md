# Rwanda Teenage Pregnancy Trends

A Streamlit dashboard visualizing teenage pregnancy trends in Rwanda, based on data from the **Rwanda Demographic and Health Surveys (Individual Records)** conducted in 1992, 2000, 2005, 2010-2011, 2014-2015, and 2019-2020. These datasets are sourced from the National Institute of Statistics of Rwanda (NISR).

The dashboard provides an overview of teenage pregnancy trends over time, highlighting changes in rates and patterns. Additionally, it integrates external datasets from the **[DHS Program](https://dhsprogram.com/)** website, including data from Kenya, Uganda and Tanzania (2022), to demonstrate the compatibility of the dashboard with international data sources.

District boundaries are visualized using GeoJSON data, ensuring precise geographic representation of trends across Rwanda.

## Live Demo

The dashboard is hosted and accessible [https://datawizards-nisr.streamlit.app](https://datawizards-nisr.streamlit.app).

## Features

- **Trend Visualization**: See changes in teenage pregnancy rates across the Rwanda Demographic and Health Survey periods of 1992, 2000, 2005, 2010-2011, 2014-2015, and 2019-2020.
- **Comparative Analysis**: Gain insights into how teenage pregnancy rates have evolved across the survey periods, highlighting key patterns and trends.
- **Interactive Filtering**: Adjust filters to focus on specific demographics, such as age groups, or geographic regions for detailed insights.
- **Map Visualization**: Provides an interactive map to visualize district-wise teenage pregnancy rates and regional variations, powered by GeoJSON data for precise boundary mapping.
- **AI Assistant**: Leverage our built-in AI assistant to:
  - Provide quick summaries of the data.
  - Answer user-specific questions about trends and statistics.
  - Offer recommendations based on comparative analyses.
  - Help navigate and interpret the dashboard’s features more effectively.
- **Excel Template**: Easily upload data using our pre-formatted Excel template, ensuring consistency and simplifying the data input process.  
  - Download the template from [here](https://github.com/saveur1/Datawizards/raw/refs/heads/main/template/file.xlsx).  

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/saveur1/Datawizards.git
   cd Datawizards
   ```
2. **Install Dependencies**
   Ensure you have Python 3.8+ and install the required packages:

   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Dashboard Locally**

   ```bash
   streamlit run app.py
   ```

## Project Structure

- **`app.py`**: Main file for the Streamlit dashboard.
  ![Project Structure](https://github.com/saveur1/Datawizards/blob/main/static/project%20structure.png)
- **`data_injection.py`**: Script responsible for importing, cleaning, and processing Excel data files into a structured format for analysis.
- **`project_charts.py`**: Module dedicated to generating project-specific visualizations, including charts and maps, for data presentation.
- **`datawizards.db`**: SQLite database used to store processed and imported data for efficient querying and analysis.

## Usage

1. Run the application with `streamlit run app.py`.
2. Explore data for each survey period, observing trends and differences.
3. Use filters to refine the data based on specific demographics or regions.

# Data Sources for Dashboard

The data used in this dashboard is primarily derived from the **Rwanda Demographic and Health Surveys (Individual Records)** from the National Institute of Statistics of Rwanda (NISR). Additionally, external datasets are sourced from the DHS Program website to demonstrate the dashboard's compatibility with data from other countries.

## Microdata Datasets

The following microdata datasets from the **Rwanda Demographic and Health Surveys (Individual Records)** are used:

- **1992**: [RWANDA - Demographic Health Survey 1992 (Individual Records)](https://microdata.statistics.gov.rw/index.php/catalog/6)
- **2000**: [RWANDA - Demographic Health Survey 2000 (Individual Records)](https://microdata.statistics.gov.rw/index.php/catalog/11)
- **2005**: [RWANDA - Demographic Health Survey 2005 (Individual Records)](https://microdata.statistics.gov.rw/index.php/catalog/14)
- **2010-2011**: [RWANDA - Demographic and Health Survey 2010-2011 (Individual Records)](https://microdata.statistics.gov.rw/index.php/catalog/4/data_dictionary)
- **2014-2015**: [RWANDA - Demographic and Health Survey 2014-2015 (Individual Records)](https://microdata.statistics.gov.rw/index.php/catalog/68/data_dictionary)
- **2019-2020**: [RWANDA - Demographic and Health Survey 2019-2020 (Individual Records)](https://microdata.statistics.gov.rw/index.php/catalog/98/data_dictionary)

## District Boundaries

The geographic boundaries for Rwanda's districts are included in GeoJSON format, providing accurate district boundaries for mapping:

- **District Boundaries (GeoJSON)**: [Coordinates for Rwanda District Boundaries](https://rwanda.africageoportal.com/datasets/be7b39ac16094f1fba36f62c55b47986/explore?location=-2.125174%2C29.848264%2C9.17)

## External Datasets Used

In addition to the Rwanda datasets, external datasets from the **DHS Program** website are used to showcase the dashboard's flexibility in handling data from other countries. These datasets include:

- **Kenya Standard DHS 2022 data**: [Kenya Standard DHS 2022](https://dhsprogram.com/data/dataset/Kenya_Standard-DHS_2022.cfm?flag=1)*Used to demonstrate compatibility with data from Kenya.*
- **Uganda Standard DHS 2016 data**: [Uganda Standard DHS 2016](https://dhsprogram.com/data/dataset/Uganda_Standard-DHS_2016.cfm?flag=1)*Used to demonstrate compatibility with data from Uganda.*
- **Tanzania Standard DHS 2022 data**: [Tanzania Standard DHS 2022](https://dhsprogram.com/data/dataset/Tanzania_Standard-DHS_2022.cfm?flag=1)
  *Used to demonstrate compatibility with data from Tanzania.*

These external datasets help provide cross-country comparisons and validate the dashboard's ability to integrate and display international data.

---

1. **Data Extraction**

   - From each dataset, we extracted variables related to year of interview(v007), women's individual sample weight (6 decimals)(v005),respondent's current age (v012),age in 5 years group(v013) stratification for sampling(v023),region (v024),education level(v149),wealth index combined (v190),currently pregnant (v213), living children + current pregnancy (v219),
   - Example: In the 2019-2020 dataset, the "Individual Records (Women)" table was filtered to include only data for women aged 15-19.

#### **Export Data to CSV from Stata (Using GUI)**

Follow these steps to export the data from **Stata** into a CSV file using the GUI:

1. Open Stata and load the dataset containing the variables you want to export.
2. Go to the **File** menu in the top navigation bar.
3. Select **Export** and then choose **Data to Excel spreadsheet (*.xls; *.xlsx; *.csv)**.
4. In the **Export Data** dialog box:
   - Select the **Variables to Export** by clicking on the dropdown and choosing the variables needed (e.g., age, district, pregnancy status).
   - Choose **CSV file** as the export format.
   - Specify the file name and location where the CSV file will be saved.
5. Click **OK** to export the data.
6. Navigate to the saved location to verify the exported CSV file.

#### **Upload the CSV File to the Dashboard**

1. Navigate to the "Upload Data" section in the Streamlit dashboard.
2. Use the file upload interface to select the CSV file generated from Stata.
3. Confirm the upload to visualize and process the data within the system.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
