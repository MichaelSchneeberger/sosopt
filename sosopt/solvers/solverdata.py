from abc import ABC, abstractmethod
import numpy as np


class SolverData(ABC):
    @property
    @abstractmethod
    def cost(self) -> float: ...
    
    @property
    @abstractmethod
    def iterations(self) -> int: ...

    @property
    @abstractmethod
    def solution(self) -> np.ndarray: ...

    @property
    @abstractmethod
    def status(self) -> str: ...
