from pydantic import BaseModel, Field
from typing import Optional

class BusinessDetails(BaseModel):
    business_name: str = Field(alias='Business Name')
    id: str or int = Field(alias='Business ID')
    entity_type: str = Field(alias='Entity Type')
    status: str = Field(alias='Business Status')
    office_address: Optional[str] = Field(alias='Principal Office Address')
    jurisdiction: Optional[str] = Field(alias='Jurisdiction of Formation')
    creation_date: Optional[str] = Field(alias='Creation Date')

class GoverningPerson(BaseModel):
    title: Optional[str] = Field(alias='Title')
    name: Optional[str] = Field(alias='Name')
    address: Optional[str] = Field(alias='Address')

class RegisteredAgent(BaseModel):
    type: Optional[str] = Field(alias='Type')
    name: Optional[str] = Field(alias='Name')
    address: Optional[str] = Field(alias='Address')
    
class Business(BaseModel):
    business_name: str
    business_details: BusinessDetails
    governing_persons: Optional[list[GoverningPerson]]
    registered_agent: Optional[RegisteredAgent]
    
class BusinessList(BaseModel):
    name: str
    city: Optional[str]
    business_list: list[Business]