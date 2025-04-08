# SOS Decomposition

This example finds the SOS decomposition of the polynomial

$$
p(x) = 1 + x_1^2 - x_1 x_2^2 + x_2^4.
$$

This includes finding a sequence of polynomials $q_k(x)$ such that $p(x) = \sum_k q_k(x)$.
This conversion involves decomposing SOS polynomials into their Square Matricial Representation (SMR):

$$
p(x) = Z(x)^\top Q_p Z(x), \quad Q_p≽0,
$$

where the monomial basis is given by monomial vector $Z(x) = [1 \quad x_1 \quad x_2 \quad x_1 x_2 \quad x_2^2]^\top$, and the Gram matrix is a symmetric matrix $Q_p \in \mathbb R^{5 \times 5}$.
Once such a Gram matrix is found, we can decompose using Cholesky decomposition, that is $Q_p = L L^\top$.
The sequence of polynomials $q_k(x)$ can be derived by:

$$
q(x) = \begin{bmatrix} q_1(x) \\ \vdots \\ q_5(x) \end{bmatrix} = L^\top Z(x)
$$

The resulting SOS problem to find the SOS decomposition is defined as:

$$\begin{array}{ll}
    \text{find} & Q_p \in \mathbb R^{5 \times 5} \\
    % \text{minimize} & \text{tr}( Q_p ) \\
    \text{subject to} & p(x) > 0 \quad \forall x \in \mathbb R^n \\
\end{array}$$

``` python
--8<-- "examples/sosdecomposition.py"
```

<!-- The sequence of polynomials $q_k(x)$ are given by:

$$
q(x) = \left[\begin{matrix}- 0.842703953878416 x_{1} + 0.870844362622798 x_{2}^{2} - 0.21959041424796\\0.967734447386914 - 0.252170655193548 x_{1}\\- 0.475773062264921 x_{1} - 0.491660549656053 x_{2}^{2} - 0.123976164286335\\0.000107491873298444 x_{1} x_{2} - 0.510538706180748 x_{2}\\0.00999942225816946 x_{1} x_{2} + 2.10533817988768 \cdot 10^{-6} x_{2}\end{matrix}\right].
$$ -->