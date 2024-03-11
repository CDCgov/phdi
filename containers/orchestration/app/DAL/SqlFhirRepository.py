from app.DAL.FhirRepository import FhirRepository
from sqlalchemy.orm import Session


class SqlAlchemyFhirRepository(FhirRepository):
    def __init__(self, session: Session):
        self.session = session

    def persist(self, entity):
        self.session.merge(entity)
        self.session.commit()
        return entity
