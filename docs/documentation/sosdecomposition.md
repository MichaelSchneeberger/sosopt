# SOS Decomposition and SDP Conversion

An SOS problem is solved by converting it to a Semi-definite Program (SDP).
This involves decomposing the SOS polynomials $p(x; \theta)$ into the Square Matricial Representation (SMR):

$$
p(x; \theta) = Z(x)^\top Q_p(\theta) Z(x),
$$

where the monomial vector $Z(x)$ are selected to contain all monomial up the degree $\lceil \text{deg}(p)/2 \rceil$.
Because multiple entries of $Q(\theta)$ can correspond to the same monomial, this decomposition is not unique.
To see this, consider the polynomial $p(x) = x_1^4 + x_1^2 x_2^2 + x_2^4$, which has -- given the monomial vector $Z(x) = [x_1^2 \quad x_1 x_2 \quad x_2^2]^\top$ -- a family of decompositions

$$
Q_p = \begin{bmatrix}
1 & 0 & -\alpha \\ 
0 & 1 + 2 \alpha & 0 \\ 
-\alpha & 0 & 1
\end{bmatrix}
$$

parametrized by $\alpha$.
To account for this, $\alpha$ can be selected as a decision variable of the optimization problem.
However, for a large matrix $Q_p$ many additional variables need to be introduced, resulting in a higher computational effort.
To account for this, a heuristic can be enabled that preselect a specific value for $\alpha$.
This heursitic constructs a gram matrix in a way that prioritizes nonzero entries corresponding to monomial in $Z(x)$ that involve multiple variables.
In the above example, $\alpha=0$ is selected for $Q_p$.
This heuristic is enabled by default and can be disabled when initializing the state object:

``` python
state = sosopt.init_state(sparse_smr=False)
```