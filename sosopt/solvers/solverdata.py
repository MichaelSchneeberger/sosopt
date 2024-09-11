from abc import ABC, abstractmethod
import numpy as np


class SolverData(ABC):
    @property
    @abstractmethod
    def status(self) -> str: ...
    """ Solver dependent status message """

    @property
    @abstractmethod
    def is_successful(self) -> bool: ...


class SolutionNotFound(SolverData):
    @property
    def is_successful(self) -> bool:
        return False


class SolutionFound(SolverData):
    @property
    @abstractmethod
    def cost(self) -> float: ...
    """ Primary cost """
    
    @property
    @abstractmethod
    def iterations(self) -> int: ...
    """ Number of iterations """

    @property
    @abstractmethod
    def solution(self) -> np.ndarray: ...
    """ Primal solution """

    @property
    def is_successful(self) -> bool:
        return True
