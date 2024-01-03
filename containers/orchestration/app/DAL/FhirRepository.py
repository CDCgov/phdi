import abc

from app.DAL.PostgresFhirDataModel import PostgresFhirDataModel


class FhirRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def persist(self, entity: PostgresFhirDataModel):
        raise NotImplementedError()
