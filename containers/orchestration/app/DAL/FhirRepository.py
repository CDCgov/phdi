import abc

from app.DAL.FhirDataModel import FhirDataModel


class FhirRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def persist(self, entity: FhirDataModel):
        raise NotImplementedError()
