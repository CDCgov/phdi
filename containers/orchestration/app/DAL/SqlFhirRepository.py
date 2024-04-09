from app.DAL.FhirRepository import FhirRepository
from sqlalchemy.orm import Session


class SqlAlchemyFhirRepository(FhirRepository):
    def __init__(self, session: Session):
        self.session = session

    def persist(self, entity):
        """
        Merges and commits an entity to the database session.

        Parameters:
            entity: The entity to be merged and committed.

        Returns:
            The merged and committed entity.
        """
        self.session.merge(entity)
        self.session.commit()
        return entity
