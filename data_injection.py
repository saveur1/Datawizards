import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint
from typing import TypedDict
from typing import List

import streamlit as st
import pandas as pd
from time import sleep
from sqlalchemy.exc import IntegrityError
from st_aggrid import AgGrid

#Local Imports
import application_logic as appl

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
    literacy            = sa.Column("literacy", sa.String)
    current_age         = sa.Column("current_age", sa.Integer)
    education_level     = sa.Column("education_level", sa.String)
    survey_round        = sa.Column("survey_round", sa.String)

    # Define a unique constraint for (district, year)
    # __table_args__ = (
    #     UniqueConstraint("district", "year", name="uix_district_year"),
    # )

    def __init__(
            self, 
            district: str, 
            interview_year: int, 
            age_range: str, 
            currently_pregnant: str,
            literacy: str, 
            current_age: int, 
            education_level: str,
            survey_round: str
        ):
        self.currently_pregnant = currently_pregnant
        self.interview_year     = interview_year
        self.district           = district
        self.age_range          = age_range
        self.literacy           = literacy
        self.current_age        = current_age
        self.education_level    = education_level
        self.survey_round       = survey_round

    def __repr__(self):
        return (f"TeenagePregnancy(district='{self.district}', interview_year={self.interview_year}, "
                f"age_range='{self.age_range}', currently_pregnant='{self.currently_pregnant}', "
                f"literacy='{self.literacy}', current_age={self.current_age}, "
                f"education_level='{self.education_level}', survey_round='{self.survey_round}')")

    def to_dict(self):
        return {
            "district": self.district,
            "interview_year": self.interview_year,
            "age_range": self.age_range,
            "currently_pregnant": self.currently_pregnant,
            "literacy": self.literacy,
            "current_age": self.current_age,
            "education_level": self.education_level,
            "survey_round": self.survey_round
        }
    
    @classmethod
    def get_all_as_dict(self, session):
        records = session.query(self).all()
        return [record.to_dict() for record in records]


# DEFINE THE REGIONS TABLE
class Regions(Base):
    __tablename__ = "regions"
    region_id =   sa.Column("region_id", sa.Integer, primary_key=True, autoincrement=True)
    district = sa.Column("district", sa.String)
    longitude =     sa.Column("longitude", sa.Double)
    latitude = sa.Column("latitude", sa.Double)

    # Define a unique constraint for (district, year)
    __table_args__ = (
        UniqueConstraint("district", name="uix_district"),
    )

    def __init__(
            self, 
            district: str, 
            longitude: float, 
            latitude: float,
        ):
        self.district  = district
        self.longitude = longitude
        self.latitude  = latitude

    def __repr__(self):
        return f"Regions(region_id={self.region_id}, district='{self.district}', latitude={self.latitude}, longitude={self.longitude})"

    # Return Dictionary data
    def to_dict(self):
        return {
            "region_id": self.region_id,
            "district": self.district,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
    
    @classmethod
    def get_district_coordinates(self, session, district):
        record = session.query(self).filter(self.district == district).first()
        return record.to_dict()


# BASIC CONFIGURATIONS
engine = sa.create_engine("sqlite:///datawizards.db")
Session = sessionmaker(bind= engine)
session = Session()


# FUNCTION TO INSERT ONE DATA
def insert_single_data( 
            district: str, 
            interview_year: int, 
            age_range: str, 
            currently_pregnant: str,
            literacy: str, 
            current_age: int, 
            education_level: str,
            survey_round: str
        ):
    # Create a new instance of TeenagePregnancy with the provided attributes
    record = TeenagePregnancy(
        district           = district,
        interview_year     = interview_year,
        age_range          = age_range,
        currently_pregnant = currently_pregnant,
        literacy           = literacy,
        current_age        = current_age,
        education_level    = education_level,
        survey_round       = survey_round
    )
    
    # Add the new record to the session and commit it to the database
    session.add(record)
    session.commit()



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

# FUNCTION TO RETRIEVE COORDINATES BASED ON DISTRICT
def coordinates_for_district(district: str):
    result = Regions.get_district_coordinates(session, district.capitalize())
    return result

# INSERT INTO REGIONS
def insert_regions(records: List[TeenageProps]):
    for data in records:
        record = Regions(**data)
        session.add(record)
    session.commit()

def clean_district(district: str):
    if "rural" in district.lower() or "urban" in district.lower():
        cleaned = district.lower()
        cleaned = cleaned.replace("rural", "").replace("urban", "").replace("-", "")
        return " ".join(cleaned.split()).strip()
    
    return district

# FILTER DATA AND REMOVE UNWANTED
def filter_incoming_data(records: List):
    result = []
    for record in records:
        if int(str(record["current_age"]).strip() or "30") < 20:
            district = clean_district(record["district"])
            record["district"] = district
            result.append(record)

    return result

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
            array_data = filter_incoming_data(array_data)

            # create data summary
            summary = appl.create_upload_summary(array_data, "current_age")
            df = pd.DataFrame(summary)

            df = df.rename(columns={
                "ages": "Ages", 
                "pregnant_count": "Pregnancy Count", 
                "women_count": "Total Women",
                "literacy_count": "Literate Count"
            })

            AgGrid(df, fit_columns_on_grid_load= True, height=180)

            #Input Survey round name
            survey_wave_name = st.text_input("Enter Survey Wave name", placeholder="2019-20")
            
            if st.button("Submit"):
                if not survey_wave_name:
                    st.error("Survey wave name is required to identify different surveys periods!")
                    return;    
                
                try:
                    # Check for existing record with the same Survey wave name
                    exists = session.query(TeenagePregnancy).filter_by(survey_round= survey_wave_name).first()
                    
                    if exists:
                        st.error(f"This survey wave name already exists.")
                        return
                    
                    for data in array_data:
                        data["survey_round"] = survey_wave_name
        
                    insert_multiple_data(array_data)
                    st.success("All records was added in database successfully!")
                    sleep(3)
                    st.rerun()
                
                except IntegrityError:
                    st.error("Error: Some entries for district and year Already exists. Each district-year combination must be unique.")
                    session.rollback()
                
                except Exception as e:
                    session.rollback()
                    raise e  # Re-raise other exceptions