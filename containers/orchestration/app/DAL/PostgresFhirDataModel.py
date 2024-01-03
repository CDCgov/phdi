from sqlalchemy import Column, VARCHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PostgresFhirDataModel(Base):
    __tablename__ = "fhir"
    ecr_id = Column(VARCHAR, primary_key=True)
    data = Column(JSONB)
