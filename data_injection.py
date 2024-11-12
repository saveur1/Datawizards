import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint
from collections import defaultdict
from typing import TypedDict
from typing import List
from functools import reduce

# DEFINING TEENAGE PREGNANCY TYPES
class TeenageProps(TypedDict):
    tbl_id: int 
    district: str 
    year: int
    pregnant_count: int
    male_educated: int
    female_educated: int
    female_teenager: int
    male_teenager: int


# DEFINE METADATA AND BASE
metadata = sa.MetaData()
Base = declarative_base()


# DEFINE THE TABLE
class TeenagePregnancy(Base):
    __tablename__ = "teenage_pregnancy"
    tbl_id =   sa.Column("tbl_id", sa.Integer, primary_key=True, autoincrement=True)
    district = sa.Column("district", sa.String)
    year =     sa.Column("year", sa.Integer)
    pregnant_count = sa.Column("pregnant_count", sa.Integer)
    male_educated  = sa.Column("male_educated", sa.Integer)
    female_educated  = sa.Column("female_educated", sa.Integer)
    female_teenager  = sa.Column("female_teenager", sa.Integer)
    male_teenager  = sa.Column("male_teenager", sa.Integer)

    # Define a unique constraint for (district, year)
    __table_args__ = (
        UniqueConstraint("district", "year", name="uix_district_year"),
    )

    def __init__(
            self, 
            district: str, 
            year: int, 
            pregnant_count: int, 
            male_educated: int,
            female_educated:int, 
            female_teenager:int, 
            male_teenager:int
        ):
        self.district       = district
        self.year           = year
        self.pregnant_count = pregnant_count
        self.male_educated  = male_educated
        self.female_educated= female_educated
        self.male_teenager  = male_teenager
        self.female_teenager= female_teenager

    def __repr__(self):
        return f"TeenagePregnancy(tbl_id={self.tbl_id}, district='{self.district}', year={self.year}, pregnant_count={self.pregnant_count}, male_educated={self.male_educated}, female_educated={self.female_educated}, female_teenager={self.female_teenager}, male_teenager={self.male_teenager})"

    # Return Dictionary data
    def to_dict(self):
        return {
            "tbl_id": self.tbl_id,
            "district": self.district,
            "year": self.year,
            "pregnant_count": self.pregnant_count,
            "male_educated": self.male_educated,
            "female_educated": self.female_educated,
            "female_teenager": self.female_teenager,
            "male_teenager": self.male_teenager
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
            year: int, 
            pregnant_count: int, 
            male_educated: int,
            female_educated:int, 
            female_teenager:int, 
            male_teenager:int
        ):
    region = TeenagePregnancy(None, district, year, pregnant_count, male_educated, female_educated, female_teenager, male_teenager)
    session.add(region)
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
    result = Regions.get_district_coordinates(session, district)
    return result

# INSERT INTO REGIONS
def insert_regions(records: List[TeenageProps]):
    for data in records:
        record = Regions(**data)
        session.add(record)
    session.commit()

# FUNCTION TO FILTER DATA BEFORE INSERTION
def filter_incoming_data(raw_records: List)-> List:
    result = defaultdict(lambda: {
            "district": None, 
            "year": 0, 
            "pregnant_count": 0, 
            "male_educated": 0,
            "female_educated":0, 
            "female_teenager":0, 
            "male_teenager":0
        })
    
    for record in raw_records:
        district = record["districts"]  #v023 contains districts
        years = record["years"]  #v007 contains years
        result[years][district]["district"] = district
        result[years][district]["year"] = record["years"] #v007 contains years

        # Male Teenagers Count
        if 14 <= record["age"] <= 18 and record["gender"] == "male":
            result[district]["male_teenager"] += 1

        # # Female Teenagers Count
        # if 14 <= record["age"] <= 18 and record["gender"] == "female":
        #     result[district]["female_teenager"] += 1

        # # Female Educated Count
        # if 14 <= record["age"] <= 18 and record["gender"] == "female":
        #     result[district]["female_teenager"] += 1

        # # Male Educated Count
        # if 14 <= record["age"] <= 18 and record["gender"] == "female":
        #     result[district]["female_teenager"] += 1

        # # Pregnant count
        # if record["current_pregnant"] == "yes":
        #     result[district]["pregnant_count"] += 1

    return list(result.values())