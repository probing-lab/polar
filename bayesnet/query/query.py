from abc import ABC, abstractmethod


class Query(ABC):
    @abstractmethod
    def generate_init_code(self, network, polar_variable_mapping):
        pass

    @abstractmethod
    def generate_loop_code(self, network, polar_variable_mapping):
        pass

    @abstractmethod
    def generate_query(self, network, polar_variable_mapping):
        pass
