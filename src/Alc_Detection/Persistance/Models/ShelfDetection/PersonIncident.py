from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, ForeignKey, UUID
)

from Alc_Detection.Persistance.Models.BaseModel import BaseModel

class PersonIncident(BaseModel):
    __tablename__ = "person_incidents"

    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"))
    
    person = relationship("Person", back_populates="incidents", lazy='selectin')
    incident = relationship("Incident", back_populates="persons", lazy='selectin')