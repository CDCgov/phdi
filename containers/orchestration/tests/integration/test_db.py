import uuid

import pytest
from app.DAL.PostgresFhirDataModel import PostgresFhirDataModel
from app.DAL.SqlFhirRepository import SqlAlchemyFhirRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.mark.integration
def test_db_connection(setup):
    engine = create_engine("postgresql://postgres:pw@localhost:5432/ecr_viewer_db")
    ecr_id = uuid.uuid4()
    expected = PostgresFhirDataModel(ecr_id=str(ecr_id), data={"something": "here"})
    with Session(engine, expire_on_commit=False) as session:
        repo = SqlAlchemyFhirRepository(session)
        repo.persist(expected)

    with Session(engine) as session:
        actual = session.get(PostgresFhirDataModel, str(ecr_id))
        assert expected.ecr_id == actual.ecr_id
        assert expected.data == actual.data
