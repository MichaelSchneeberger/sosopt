# SOS Decomposition

This example demonstrates how to find an SOS decomposition for the polynomial:

$$
p(x) = 1 + x_1^2 - x_1 x_2^2 + x_2^4.
$$

An SOS decomposition represents $p(x)$ as $p(x) = \sum_k q_k(x)^2$, where $q_k(x)$ are polynomials.
This is achieved through Square Matricial Representation (SMR), where the polynomial is expressed in quadratic form:

$$
p(x) = Z(x)^\top Q_p Z(x), \quad Q_p≽0,
$$

where the monomial basis is given by monomial vector $Z(x) = [1 \quad x_1 \quad x_2 \quad x_1 x_2 \quad x_2^2]^\top$, and the Gram matrix is a symmetric matrix $Q_p \in \mathbb R^{5 \times 5}$.
Once such a Gram matrix $Q_p$ is found, we compute its Cholesky factorization $Q_p = L L^\top$.
The SOS terms are then obtained as:

$$
q(x) = \begin{bmatrix} q_1(x) \\ \vdots \\ q_5(x) \end{bmatrix} = L^\top Z(x)
$$

The SOS decomposition is found by solving:

$$\begin{array}{ll}
    \text{find} & Q_p \in \mathbb R^{5 \times 5} \\
    % \text{minimize} & \text{tr}( Q_p ) \\
    \text{subject to} & p(x) > 0 \quad \forall x \in \mathbb R^n \\
\end{array}$$

``` python
--8<-- "examples/sosdecomposition.py"
```

The resulting Gram matrix is given as:

$$
Q_p = \left[\begin{matrix}1 & 0 & 0 & 7.41873902278933 \cdot 10^{-18} & -0.130274885256573\\0 & 1 & -7.41873902278933 \cdot 10^{-18} & 0 & -0.499945142290247\\0 & -7.41873902278933 \cdot 10^{-18} & 0.260549770513145 & -5.48577097532754 \cdot 10^{-5} & 0\\7.41873902278933 \cdot 10^{-18} & 0 & -5.48577097532754 \cdot 10^{-5} & 0 & 0\\-0.130274885256573 & -0.499945142290247 & 0 & 0 & 1\end{matrix}\right]
$$

The recovered polynomial $p(x) = q(x)^\top q(x)$ is given as:

$$
p(x) = 1 \cdot 10^{-5} x_{1}^{2} x_{2}^{2} + 1.0001 x_{1}^{2} - x_{1} x_{2}^{2} + 1.0001 x_{2}^{4} + 1.0001
$$