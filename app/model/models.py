from datetime import date
from typing import Optional, Union

from pydantic import BaseModel, Field, validator

from ..classes.classes import (
    Affiliates,
    Poligrafs,
    Regions,
    Conclusions,
    Relations,
    Roles
)


class QueryModel(BaseModel):
    id: Optional[str | int] = None

    class Config:
        use_enum_values = True


class User(QueryModel):
    fullname: str
    username: str
    region: Optional[Regions] = None
    role: Optional[Roles] = None


class Name(QueryModel):
    surname: str
    firstname: str
    patronymic: Optional[str] = None

    @validator("surname", "firstname", "patronymic")
    def check_names(cls, v):
        return v.upper().strip() if v else None


class Person(Name):
    birthday: date
    birthplace: Optional[str] = None
    citizenship: str = None
    dual: Optional[str] = None
    snils: Optional[str] = None
    inn: Optional[str] = None
    marital: Optional[str] = None
    addition: Optional[str] = None
    destination: Optional[str] = None
    region: Optional[Regions] = None


class Prev(Name):
    changed: Optional[str] = None
    reason: Optional[str] = None


class Education(QueryModel):
    view: str
    institution: str
    finished: Union[str, int] = None
    specialty: Optional[str] = None


class Staff(QueryModel):
    position: str
    department: str = "Прямое подчинение"


class Document(QueryModel):
    view: str
    series: Optional[str] = None
    digits: str
    agency: Optional[str] = None
    issue: Optional[date] = None


class Address(QueryModel):
    view: str
    addresses: str


class Contact(QueryModel):
    view: str
    contact: str


class Workplace(QueryModel):
    now_work: Optional[bool] = False
    starts: date
    finished: Optional[date] = None
    workplace: str
    addresses: Optional[str] = None
    position: str
    reason: Optional[str] = None


class Affilation(QueryModel):
    view: Affiliates
    organization: str
    inn: Optional[str] = None


class Relation(QueryModel):
    relation: Relations
    relation_id: Union[int, str]


class Check(QueryModel):
    workplace: Optional[str] = None
    document: Optional[str] = None
    inn: Optional[str] = None
    debt: Optional[str] = None
    bankruptcy: Optional[str] = None
    bki: Optional[str] = None
    courts: Optional[str] = None
    affilation: Optional[str] = None
    terrorist: Optional[str] = None
    mvd: Optional[str] = None
    internet: Optional[str] = None
    cronos: Optional[str] = None
    cros: Optional[str] = None
    addition: Optional[str] = None
    comment: Optional[str] = None
    conclusion: Optional[Conclusions] = None


class Poligraf(QueryModel):
    theme: Poligrafs
    results: str


class Investigation(QueryModel):
    theme: str
    info: str


class Inquiry(QueryModel):
    info: str
    origins: str


models_tables = {
    "persons": Person,
    "previous": Prev,
    "educations": Education,
    "staffs": Staff,
    "documents": Document,
    "addresses": Address,
    "contacts": Contact,
    "relations": Relation,
    "workplaces": Workplace,
    "affilations": Affilation,
    "checks": Check,
    "poligrafs": Poligraf,
    "investigations": Investigation,
    "inquiries": Inquiry,
}


class NameWasChangedJson(BaseModel):
    firstname: Optional[str] = Field(
        alias="firstNameBeforeChange", default=None, max_length=255
    )
    surname: Optional[str] = Field(
        alias="lastNameBeforeChange", default=None, max_length=255
    )
    patronymic: Optional[str] = Field(
        alias="midNameBeforeChange", default=None, max_length=255
    )
    changed: Union[str, int] = Field(alias="yearOfChange", default=None)
    reason: Optional[str] = None


class EducationJson(BaseModel):
    view: Optional[str] = Field(alias="educationType", default=None, max_length=255)
    institution: Optional[str] = Field(alias="institutionName", default=None)
    finished: Union[str, int] = Field(alias="endYear", default=None)
    specialty: Optional[str] = None


class ExperienceJson(BaseModel):
    starts: Optional[date] = Field(alias="beginDate", default=None)
    finished: Optional[date] = Field(alias="endDate", default=None)
    now_work: Optional[bool] = Field(alias="currentJob", default=False)
    workplace: Optional[str] = Field(alias="name", default=None, max_length=255)
    addresses: Optional[str] = Field(alias="address", default=None, max_length=255)
    position: Optional[str] = None
    reason: Optional[str] = Field(alias="fireReason", default=None)


class OrganizationsJson(BaseModel):
    view: str = "Участвует в деятельности коммерческих организаций"
    organization: Optional[str] = Field(alias="name", default=None)
    inn: Optional[str] = None


class RelatedPersonsOrganizationsJson(BaseModel):
    view: str = "Связанные лица работают в государственных организациях"
    organization: Optional[str] = Field(alias="name", default=None)
    inn: Optional[str] = None


class StateOrganizationsJson(BaseModel):
    view: str = "Являлся государственным должностным лицом"
    organization: Optional[str] = Field(alias="name", default=None)


class PublicOfficeOrganizationsJson(BaseModel):
    view: str = "Являлся государственным или муниципальным служащим"
    organization: Optional[str] = Field(alias="name", default=None)


class AnketaSchemaJson(BaseModel):
    surname: str = Field(alias="lastName", max_length=255)
    firstname: str = Field(alias="firstName", max_length=255)
    patronymic: Optional[str] = Field(alias="midName", default=None, max_length=255)
    birthday: date
    birthplace: Optional[str] = None
    citizenship: Optional[str] = Field(alias="citizen", default=None, max_length=255)
    dual: Optional[str] = Field(
        alias="additionalCitizenship", default=None, max_length=255
    )
    marital: Optional[str] = Field(alias="maritalStatus", default=None, max_length=255)
    inn: Optional[str] = None
    snils: Optional[str] = None
    positionName: Optional[str] = None
    department: Optional[str] = None
    passportSerial: Optional[str] = None
    passportNumber: Optional[str] = None
    passportIssueDate: Optional[date] = None
    passportIssuedBy: Optional[str] = None
    validAddress: Optional[str] = None
    regAddress: Optional[str] = None
    email: Optional[str] = None
    contactPhone: Optional[str] = None
    educations: Optional[list[EducationJson]] = Field(
        alias="education",
        default=None,
    )
    workplaces: Optional[list[ExperienceJson]] = Field(
        alias="experience",
        default=None,
    )
    previous: Optional[list[NameWasChangedJson]] = Field(
        alias="nameWasChanged", default=None
    )
    organizations: Optional[list[OrganizationsJson]] = []
    relatedPersonsOrganizations: Optional[list[RelatedPersonsOrganizationsJson]] = []
    stateOrganizations: Optional[list[StateOrganizationsJson]] = []
    publicOfficeOrganizations: Optional[list[PublicOfficeOrganizationsJson]] = []
    staffs: list = []
    addresses: list = []
    contacts: list = []
    affilations: list = []
    documents: list = []
