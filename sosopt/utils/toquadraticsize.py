import numpy as np

def to_quadratic_size(n):
    n_sqrt = np.sqrt(n)
    assert n_sqrt.is_integer(), f'{n=}'
    return int(n_sqrt)
