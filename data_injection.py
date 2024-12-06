import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import TypedDict
from typing import List
import streamlit as st
import pandas as pd
from time import sleep
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case

#Local Imports
import application_logic as app_logic
import project_assistant as assistant

# DEFINING TEENAGE PREGNANCY TYPES
class TeenageProps(TypedDict):
    tbl_id: int 
    district: str 
    interview_year: int
    age_range: str
    currently_pregnant: str
    literacy: str
    current_age: str
    education_level: str
    survey_round: str
    regions: str
    wealth_quintile: str
    weights: float


# DEFINE METADATA AND BASE
metadata = sa.MetaData()
Base = declarative_base()


# DEFINE THE TABLE
class TeenagePregnancy(Base):
    __tablename__       = "teenage_pregnancy"
    tbl_id              = sa.Column("tbl_id", sa.Integer, primary_key=True, autoincrement=True)
    district            = sa.Column("district", sa.String)
    interview_year      = sa.Column("interview_year", sa.Integer)
    age_range           = sa.Column("age_range", sa.String)
    currently_pregnant  = sa.Column("currently_pregnant", sa.String)
    literacy            = sa.Column("literacy", sa.String, nullable= True)
    current_age         = sa.Column("current_age", sa.Integer)
    education_level     = sa.Column("education_level", sa.String)
    survey_round        = sa.Column("survey_round", sa.String)
    regions             = sa.Column("regions", sa.String)
    wealth_quintile     = sa.Column("wealth_quintile", sa.String, nullable=True)
    weights             = sa.Column("weights", sa.Float)
    
    # Newly added columns
    country             = sa.Column("country", sa.String)
    living_current_pregnancy = sa.Column("living_current_pregnancy", sa.Float)

    def __init__(
            self, 
            district: str, 
            interview_year: int, 
            age_range: str, 
            currently_pregnant: str,
            current_age: int, 
            education_level: str,
            survey_round: str,
            regions: str,
            weights: float,
            country: str,
            living_current_pregnancy: float,
            literacy: str = None, 
            wealth_quintile: str = None
        ):
        self.currently_pregnant = currently_pregnant
        self.interview_year     = interview_year
        self.district           = district
        self.age_range          = age_range
        self.literacy           = literacy
        self.current_age        = current_age
        self.education_level    = education_level
        self.survey_round       = survey_round
        self.regions            = regions
        self.wealth_quintile    = wealth_quintile
        self.weights            = weights
        self.country            = country
        self.living_current_pregnancy = living_current_pregnancy

    def __repr__(self):
        return (f"TeenagePregnancy(district='{self.district}', interview_year={self.interview_year}, "
                f"age_range='{self.age_range}', currently_pregnant='{self.currently_pregnant}', "
                f"literacy='{self.literacy}', current_age={self.current_age}, "
                f"education_level='{self.education_level}', survey_round='{self.survey_round}, "
                f"regions='{self.regions}', wealth_quintile='{self.wealth_quintile}', weights='{self.weights}', "
                f"country='{self.country}', living_current_pregnancy='{self.living_current_pregnancy}', ")

    def to_dict(self):
        return {
            "district": self.district,
            "interview_year": self.interview_year,
            "age_range": self.age_range,
            "currently_pregnant": self.currently_pregnant,
            "literacy": self.literacy,
            "current_age": self.current_age,
            "education_level": self.education_level,
            "survey_round": self.survey_round,
            "regions": self.regions,
            "wealth_quintile": self.wealth_quintile,
            "weights": self.weights,
            "country": self.country,
            "living_current_pregnancy": self.living_current_pregnancy,
        }

    @classmethod
    def get_all_as_dict(cls, session):
        records = session.query(cls).all()
        return [record.to_dict() for record in records]



# BASIC CONFIGURATIONS
engine = sa.create_engine("sqlite:///datawizards.db")
Session = sessionmaker(bind= engine)
session = Session()


# FUNCTION TO INSERT MULTIPLE RECORDS
def insert_multiple_data(records: List[TeenageProps]):
    for data in records:
        record = TeenagePregnancy(**data)
        session.add(record)
    session.commit()


# FUNCTION TO RETRIEVE ALL TEENAGE PREGNANCY DATA
def get_table_data()-> List[TeenageProps]:
    result = TeenagePregnancy.get_all_as_dict(session)
    return result

def get_pregnancy_counts_grouped() -> List[dict]:
    """
    Retrieve counts of pregnancies where 'currently_pregnant' is 'Yes' or 'yes',
    grouped by 'district' and 'survey_round'.

    :return: List of dictionaries with grouped pregnancy counts.
    """
    results = (
        session.query(
            TeenagePregnancy.interview_year,
            TeenagePregnancy.survey_round,
            func.sum(
                case(
                    (   TeenagePregnancy.currently_pregnant.in_(["Yes", "yes"]),
                        TeenagePregnancy.weights  
                    ),
                    else_=0
                )
            ).label("pregnancy_count"),
            func.sum(
                case(
                    (   TeenagePregnancy.literacy.in_(["Yes", "yes"]),
                        TeenagePregnancy.weights  
                    ),
                    else_=0
                )
            ).label("literacy_count"),

            func.sum(TeenagePregnancy.weights).label("total_count"),
        )
        .group_by(TeenagePregnancy.survey_round)
        .all()
    )
    
    # Convert the result to a list of dictionaries
    return [
        {
            "sequence_year": app_logic.find_nearest_year(row.interview_year),
            "survey_round": row.survey_round,
            "pregnancy_count": row.pregnancy_count,
            "literacy_count": row.literacy_count,
            "total_count": row.total_count
        }
        for row in results
    ]


def clean_district(district: str):
    if "rural" in district.lower() or "urban" in district.lower():
        cleaned = district.lower()
        cleaned = cleaned.replace("rural", "").replace("urban", "").replace("-", "")
        return " ".join(cleaned.split()).strip()
    
    return district


def clean_regions(region: str):
    if "city" in region.lower():
        return region.lower().replace("city", "").strip()
    
    return str(region).lower()

# Define a transformation function
def transform_pregnancy_status(value):
    if value.lower() == "yes":
        return "yes"
    else:
        return "no"
    
def transform_literacy(value):
    if value != None and str(value).lower() != "cannot read at all":
        return "yes"
    else:
        return "no"
    
def round_nearest(value):
    return int(round(value, 0))


# FILTER DATA AND REMOVE UNWANTED
def filter_incoming_data(records: List):
    result = []
    for record in records:
        if int(str(record["current_age"]).strip() or "30") < 20:    
            if int(record["interview_year"]) > 2009:
                district = clean_district(record["district"])
                record["district"] = district
            
            region = clean_regions(record["regions"])
            record["regions"] = region
            result.append(record)

    return result

# UPLOADED FILE PREVIEW MODAL
@st.dialog("Review Uploaded File", width="large")
def upload_xlsx_file(xlsx_file, data_frame: type[pd.DataFrame]):
    if xlsx_file is not None:
        columns_map = {
                'v007' : "interview_year",
                'v005' : "weights",
                'v023' : "district", 
                'v213' : "currently_pregnant", 
                'v155' : "literacy", 
                'v012' : "current_age", 
                'v149' : "education_level", 
                'v013' : "age_range",
                'v024' : "regions",
                'v219' : "living_current_pregnancy",
                'v190' : "wealth_quintile",
        }
        # data table
        data_frame = data_frame.rename(columns=lambda col: str(col).strip().lower())
        
        # Validate required columns
        required_columns = ['v007', 'v005', 'v023', 'v213', 'v012', 'v149', 'v013', "v024", 'v219']
        columns_valid, missing_columns = app_logic.validate_required_columns(data_frame, required_columns)
        

        if not columns_valid:
            st.error(f"Invalid file uploaded. Missing required columns: {', '.join(missing_columns)}")
            st.write(columns_map)
            return
        
        else:
            #Rename Columns to match what's in database
            sampling_decimals_offset = 1000000
            data_frame = data_frame.rename(columns= columns_map )

            # Transformations on Columns
            data_frame["weights"] = data_frame["weights"] / sampling_decimals_offset
            data_frame["currently_pregnant"] = data_frame["currently_pregnant"].apply(transform_pregnancy_status)

            # Filter columns_map to include only columns present in the DataFrame
            available_columns = [new_name for _, new_name in columns_map.items() if new_name in data_frame.columns]
            
            # Convert to array of dictionaries
            array_data = data_frame[available_columns].to_dict(orient="records")

            #Remove unwanted records
            array_data = filter_incoming_data(array_data)

            # create data summary
            summary = app_logic.create_upload_summary(array_data, "current_age")
            
            df = pd.DataFrame(summary)

            df = df.rename(columns={
                "ages": "Ages", 
                "pregnant_count": "Currently Pregnant", 
                "women_count": "Total Cases",
                "child_bearing": "Begun Child Bearing"
            })


            columns_to_display = ["Ages", "Currently Pregnant", "Begun Child Bearing","Total Cases"]
            filtered_df = df[columns_to_display]

            # Remove extra decimal points
            filtered_df["Currently Pregnant"] = filtered_df["Currently Pregnant"] / filtered_df["Total Cases"] * 100
            filtered_df["Currently Pregnant"] = filtered_df["Currently Pregnant"].apply(lambda x: str(round(x,1)) +"%")
            filtered_df["Total Cases"] = filtered_df["Total Cases"].apply(round_nearest)

            #Child bearing percentage
            filtered_df["Begun Child Bearing"] = filtered_df["Begun Child Bearing"] / filtered_df["Total Cases"] * 100
            filtered_df["Begun Child Bearing"] = filtered_df["Begun Child Bearing"].apply(lambda x: str(round(x,1)) +"%")

            st.table(filtered_df)

            #Input Survey round name
            country_name = st.text_input("Enter Country name", placeholder="Rwanda")
            
            # Extract unique years from the data
            years_range = list({arr["interview_year"] for arr in array_data})

            # Sort the years (optional but often helpful)
            years_range.sort()

            # Join the years into a string with a hyphen
            survey_wave_name = "-".join(map(str, years_range))
            if len(survey_wave_name) < 3:
                survey_wave_name = "19"+survey_wave_name
            
            
            cols1, cols2 = st.columns(2)

            if cols1.button("Submit"):
                upload_data_into_database(country_name, array_data, xlsx_file, survey_wave_name)

            cols2.markdown(f"**Survey Period**: { survey_wave_name }")

def upload_csv_file(xlsx_file):
    if xlsx_file is not None:
        columns_map = {
                'v007' : "interview_year",
                'v005' : "weights",
                'v023' : "district", 
                'v213' : "currently_pregnant", 
                'v155' : "literacy", 
                'v012' : "current_age", 
                'v106' : "education_level", 
                'v013' : "age_range",
                'v024' : "regions",
                'v190' : "wealth_quintile"
        }
        # data table
        data_frame = pd.read_csv(xlsx_file)
        data_frame = data_frame.rename(columns=lambda col: col.strip())

        # Validate required columns
        required_columns = ['v007', 'v005', 'v023', 'v213', 'v155', 'v012', 'v106', 'v013', "v024"]
        columns_valid, missing_columns = app_logic.validate_required_columns(data_frame, required_columns)
        

        if not columns_valid:
            st.error(f"Invalid file uploaded. Missing required columns: {', '.join(missing_columns)}")
            st.write(columns_map)
            return
        
        else:
            #Rename Columns to match what's in database
            sampling_decimals_offset = 1000000
            data_frame = data_frame.rename(columns= columns_map )

            # Transformations on Columns
            data_frame["weights"] = data_frame["weights"] / sampling_decimals_offset
            data_frame["currently_pregnant"] = data_frame["currently_pregnant"].apply(transform_pregnancy_status)
            data_frame["literacy"] = data_frame["literacy"].apply(transform_literacy)

            # Convert to array of dictionaries
            array_data = data_frame[list(columns_map.values())].to_dict(orient="records")

            #Remove unwanted records
            array_data = filter_incoming_data(array_data)

            # create data summary
            summary = app_logic.create_upload_summary(array_data, "current_age")
            
            df = pd.DataFrame(summary)

            df = df.rename(columns={
                "ages": "Ages", 
                "pregnant_count": "Pregnancy Count", 
                "women_count": "Total Women",
                "literacy_count": "Literate Count"
            })


            columns_to_display = ["Ages", "Pregnancy Count", "Literate Count","Total Women"]
            filtered_df = df[columns_to_display]

            # Remove extra decimal points
            filtered_df["Pregnancy Count"] = filtered_df["Pregnancy Count"].apply(round_nearest)
            filtered_df["Literate Count"] = filtered_df["Literate Count"].apply(round_nearest)
            filtered_df["Total Women"] = filtered_df["Total Women"].apply(round_nearest)

            st.table(filtered_df)

            #Input Survey round name
            survey_wave_name = st.text_input("Enter Survey Wave name", placeholder="2019-20")
            
            if st.button("Submit"):
                upload_data_into_database(survey_wave_name, array_data, xlsx_file)
def upload_dta_file(xlsx_file):
    if xlsx_file is not None:
        columns_map = {
                'v007' : "interview_year",
                'v005' : "weights",
                'v023' : "district", 
                'v213' : "currently_pregnant", 
                'v155' : "literacy", 
                'v012' : "current_age", 
                'v106' : "education_level", 
                'v013' : "age_range",
                'v024' : "regions",
                'v190' : "wealth_quintile"
        }
        # data table
        # Columns to be retained after conversion
        columns_to_keep = ['v007', 'v023', 'v213', 'v155', 'v012', 'v106', 'v013', 'v024', 'v190', 'v005']
        
        # Read the Stata file
        data_frame = pd.read_stata(xlsx_file)

        # Define specific data types for columns
        dtype_map = {
                'v007': 'int',         # Year: Integer
                'v005': 'float',       # Weights: Float
                'v023': 'string',      # District: String
                'v213': 'string',      # Currently Pregnant: String
                'v155': 'string',      # Literacy: String
                'v012': 'int',         # Current Age: Integer
                'v106': 'string',      # Education Level: String
                'v013': 'string',      # Age Range: String
                'v024': 'string',      # Regions: String
                'v190': 'string',      # Wealth Quintile: String
            }

            # Apply data type mapping
        for column, dtype in dtype_map.items():
                if column in data_frame.columns:
                    data_frame[column] = data_frame[column].astype(dtype)

        # Check if all required columns are present
        missing_columns = [col for col in columns_to_keep if col not in data_frame.columns]
        if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                return

            # Select only the required columns
        data_frame_filtered = data_frame[columns_to_keep]

            
        data_frame = data_frame.rename(columns=lambda col: col.strip())

        # Validate required columns
        required_columns = ['v007', 'v005', 'v023', 'v213', 'v155', 'v012', 'v106', 'v013', "v024"]
        columns_valid, missing_columns = app_logic.validate_required_columns(data_frame, required_columns)
        

        if not columns_valid:
            st.error(f"Invalid file uploaded. Missing required columns: {', '.join(missing_columns)}")
            st.write(columns_map)
            return
        
        else:
            #Rename Columns to match what's in database
            sampling_decimals_offset = 1000000
            data_frame = data_frame.rename(columns= columns_map )

            # Transformations on Columns
            data_frame["weights"] = data_frame["weights"] / sampling_decimals_offset
            data_frame["currently_pregnant"] = data_frame["currently_pregnant"].apply(transform_pregnancy_status)
            data_frame["literacy"] = data_frame["literacy"].apply(transform_literacy)

            # Convert to array of dictionaries
            array_data = data_frame[list(columns_map.values())].to_dict(orient="records")

            #Remove unwanted records
            array_data = filter_incoming_data(array_data)

            # create data summary
            summary = app_logic.create_upload_summary(array_data, "current_age")
            
            df = pd.DataFrame(summary)

            df = df.rename(columns={
                "ages": "Ages", 
                "pregnant_count": "Pregnancy Count", 
                "women_count": "Total Women",
                "literacy_count": "Literate Count"
            })


            columns_to_display = ["Ages", "Pregnancy Count", "Literate Count","Total Women"]
            filtered_df = df[columns_to_display]

            # Remove extra decimal points
            filtered_df["Pregnancy Count"] = filtered_df["Pregnancy Count"].apply(round_nearest)
            filtered_df["Literate Count"] = filtered_df["Literate Count"].apply(round_nearest)
            filtered_df["Total Women"] = filtered_df["Total Women"].apply(round_nearest)

            st.table(filtered_df)

            #Input Survey round name
            survey_wave_name = st.text_input("Enter Survey Wave name", placeholder="2019-20")
            
            if st.button("Submit"):
                upload_data_into_database(survey_wave_name, array_data, xlsx_file)


def upload_data_into_database(country_name, array_data, xlsx_file, survey_wave_name=""):
    if not survey_wave_name:
        st.error("Survey wave name is required to identify different surveys periods!")
        return;    
    
    try:
        # Check for existing record with the same Survey wave name
        exists = session.query(TeenagePregnancy).filter_by(survey_round= survey_wave_name, country= country_name).first()
        
        if exists:
            st.error(f"This survey period({ survey_wave_name }) data already exists in { country_name }.")
            return
        
        for data in array_data:
            data["survey_round"] = survey_wave_name
            data["country"] = country_name

        insert_multiple_data(array_data)
        st.success("All records was added in database successfully!")
        
        # Update Ai Model data
        assistant.main()
        st.rerun()
    
    except IntegrityError:
        st.error("Error: Some entries for district and year Already exists. Each district-year combination must be unique.")
        session.rollback()
    
    except Exception as e:
        session.rollback()
        raise e  # Re-raise other exceptions