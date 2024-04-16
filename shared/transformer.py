import abc
from typing import Type, TypeVar, Any

from shared.connector import APIConnector

# This should be a dataclass per transformer to define how the transformed data should look like.
TransformerModel = TypeVar("TransformerModel")


class BaseTransformer(abc.ABC):
    """
    Base class to define the skeleton of the transformations classes.

    This is an abstract class as we do not implement any of the methods below, we just want to give a guideline for how the child classes should look like
    """
    CONNECTOR: Type["APIConnector"] = None

    def __init__(self, connector: Type["APIConnector"]):
        self.connector: Type["APIConnector"] = connector

    @abc.abstractmethod
    def transform(self, *args, **kwargs) -> Any:
        """
        base function to transform the data received by the connector class.

        :return: transformed data into desired form -> child object of the class TransformerModel
        """
        # self.get_data()
        raise NotImplementedError()

    @abc.abstractmethod
    def get_data(self, *args, **kwargs):
        """
        Function to get the needed data form the API in order to receive the response.

        Must be implemented by child classes.
        :return:
        """
        raise NotImplementedError()
        # eg: self.connector.get_forecast(location)
