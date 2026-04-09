from turtle import pd
from datetime import date, datetime
from typing import Annotated, Optional, Union
from enum import Enum
from pydantic import (
    BaseModel,
    Field,
    BeforeValidator,
    AliasChoices,
    field_validator,
    model_validator,
)

THIS_YEAR = datetime.now().year


def none_to_zero(v: Optional[int]) -> int:
    if v is None:
        return 0
    return v


NullableInt = Annotated[int, BeforeValidator(none_to_zero)]


class LakeEnum(str, Enum):
    HU = "Lake Huron"
    SU = "Lake Superior"
    ON = "Lake Ontario"
    SC = "Lake St. Clair"
    ER = "Lake Erie"
    MI = "Lake Michigan"


lake_aliases = {
    "HU": LakeEnum.HU,
    "SU": LakeEnum.SU,
    "ON": LakeEnum.ON,
    "SC": LakeEnum.SC,
    "ER": LakeEnum.ER,
    "MI": LakeEnum.MI,
    "Huron": LakeEnum.HU,
    "Superior": LakeEnum.SU,
    "Ontario": LakeEnum.ON,
    "St. Clair": LakeEnum.SC,
    "Erie": LakeEnum.ER,
    "Michigan": LakeEnum.MI,
    "Lake Huron": LakeEnum.HU,
    "Lake Superior": LakeEnum.SU,
    "Lake Ontario": LakeEnum.ON,
    "Lake St. Clair": LakeEnum.SC,
    "Lake Erie": LakeEnum.ER,
    "Lake Michigan": LakeEnum.MI,
}


class WeightTypeEnum(str, Enum):
    round = "R"
    dressed = "D"


class SexEnum(str, Enum):
    male = "M"
    female = "F"
    unknown = "U"


class MaturityEnum(str, Enum):
    mature = "M"
    immature = "I"
    unknown = "U"


class MeshMaterialEnum(str, Enum):
    nylon = "N"
    mono = "M"
    other = "O"


class Gear(BaseModel):

    liftid: str = Field(validation_alias=AliasChoices("LIFTID", "LiftID"))
    lake: LakeEnum = Field(alias="Lake")
    agency: str = Field(alias="Agency")

    location: Optional[str] = Field(alias="Location")
    # constrain lat-lon
    latitude: Optional[float] = Field(alias="Latitude")
    longitude: Optional[float] = Field(alias="Longitude")

    management_unit: Optional[str] = Field(alias="MU")
    grid10: Optional[int] = Field(alias="GRID")

    # veify that day-month-year form a legit date - no May 31'st.
    year: int = Field(alias="Year", ge=1950, le=THIS_YEAR)
    day: Optional[int] = Field(alias="Day", ge=1, le=31)
    month: Optional[int] = Field(alias="Month", ge=1, le=12)
    survey_type: Optional[str] = Field(alias="SurveyType")
    survey_description: Optional[str] = Field(alias="SurveyDescription")
    gear: Optional[str] = Field(alias="Gear")
    nights: Optional[int] = Field(alias="Nights", ge=0, le=10)
    net_length: Optional[float] = Field(alias="NetLength(km)", gt=0)
    depth1: Optional[float] = Field(alias="Depth1(m)", gt=0, le=500)
    depth2: Optional[float] = Field(alias="Depth2(m)", gt=0, le=500)
    avgdepth: Optional[float] = Field(alias="AvgDepth(m)", gt=0, le=500)
    surface_temp: Optional[float] = Field(alias="SurfaceTemp(C)", gte=-5, lt=30)
    bottom_temp: Optional[float] = Field(alias="BottomTemp(C)", gte=-5, lt=30)
    net_material: Optional[MeshMaterialEnum] = Field(alias="NetMaterial")
    min_mesh: Optional[int] = Field(alias="MinMesh(mm)", gt=0, le=500)
    max_mesh: Optional[int] = Field(alias="MaxMesh(mm)", gt=0, le=500)
    comments: Optional[str] = Field(alias="Comments", default="")

    @field_validator("lake", mode="before")
    @classmethod
    def preprocess_lake(cls, v):
        return lake_aliases.get(v)

    @field_validator("month", mode="before")
    @classmethod
    def check_month_if_day(cls, v, values):
        # If 'day is populated, month must be populated too:
        if values.data.get("day") and v is None:
            raise ValueError("Month cannot be empty if Day is provided")
        return v

    @model_validator(mode="after")
    def validate_date_exists(self):
        if self.year and self.month and self.day:
            try:
                date(self.year, self.month, self.day)
            except ValueError as e:
                # Raises error if combination is invalid (e.g., Feb 30)
                raise ValueError(f"Invalid date: {e}")
        return self


class BioData(BaseModel):
    """A pydantic model to validate, parse and report tag data
    exported from the webforms application.  Methods have been added
    to report webform attrbitues, report attributes, reporter, and
    tags associated with each record.

    """

    # Field Names:

    # lift id must exist
    liftid: str = Field(validation_alias=AliasChoices("LIFTID", "LiftID"))
    lake: str = Field(alias="Lake")

    # agency could be an enum too:
    agency: str = Field(alias="Agency")
    fishid: str = Field(validation_alias=AliasChoices("FISHID", "FishID"))
    mesh_size: Optional[int] = Field(alias="MeshSize(mm)", gt=0, le=500)
    species_name: str = Field(alias="SpeciesName")
    species_number: int = Field(alias="SpeciesNumber")
    species_abbrev: Optional[str] = Field(alias="SpeciesAbbrev")
    length_mm: Optional[float] = Field(alias="Length(mm)", gt=0)
    weight_g: Optional[float] = Field(alias="Weight(g)", gt=0)
    weight_type: Optional[WeightTypeEnum] = Field(alias="R/D", default="R")
    # 6 digits, strip out dashes (or add them in)
    cwt_agency: Optional[str] = Field(alias="CWTAgency")
    age: Optional[int] = Field(alias="Age", ge=0, le=40)
    age_structure: Optional[str] = Field(alias="AgeStructure")
    sex: Optional[SexEnum] = Field(alias="SexAgency")
    maturity: Optional[MaturityEnum] = Field(alias="MaturityAgency")
    finclip: Optional[str] = Field(alias="FinClipAgency", coerce_numbers_to_str=True)
    # wound counds shouls all be gte=0
    a1_a3: NullableInt = Field(default=0, alias="A1-A3")
    a1: NullableInt = Field(default=0, alias="A1")
    a2: NullableInt = Field(default=0, alias="A2")
    a3: NullableInt = Field(default=0, alias="A3")
    a4: NullableInt = Field(default=0, alias="A4")
    b1: NullableInt = Field(default=0, alias="B1")
    b2: NullableInt = Field(default=0, alias="B2")
    b3: NullableInt = Field(default=0, alias="B3")
    b4: NullableInt = Field(default=0, alias="B4")
    comments: Optional[str] = Field(
        alias="Comments", default="", coerce_numbers_to_str=True
    )

    @field_validator("lake", mode="before")
    @classmethod
    def preprocess_lake(cls, v):
        return lake_aliases.get(v)
