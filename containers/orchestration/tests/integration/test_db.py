import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from containers.orchestration.app.DAL.FhirDataModel import FhirDataModel
from containers.orchestration.app.DAL.SqlAlchemyFhirRepository import SqlAlchemyFhirRepository


@pytest.mark.integration
def test_db_connection(setup):
    engine = create_engine("postgresql://postgres:pw@localhost:5432/ecr_viewer_db")
    ecr_id = uuid.uuid4()
    expected = FhirDataModel(ecr_id=str(ecr_id),
                             data={"something": "here"})
    # create session and add objects
    with Session(engine) as session:
        repo = SqlAlchemyFhirRepository(session)
        repo.persist(expected)
        actual = session.query(FhirDataModel).get(str(ecr_id))
        assert expected.ecr_id == actual.ecr_id
        assert expected.data == actual.data
