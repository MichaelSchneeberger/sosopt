# SOS Decomposition and Conic Problem Conversion

## SOS Decomposition

SOS problems are solved by converting them into conic optimization problems.
This conversion involves decomposing SOS polynomials into their Square Matricial Representation (SMR).
For a given polynomial $p(x)$, the SMR is defined as:

$$
p(x) = Z(x)^\top Q_p Z(x), \quad Q_p≽0,
$$

where the monomial vector $Z(x)$ includes all monomials up to degree $\lceil \text{deg}(p)/2 \rceil$, and $Q_p$ is the *Gram matrix*.

This representation is not unqiue, as different entries in $Q_p$ may correspond to identical monomial products.
To illustrate this, consider the polynomial $p(x) = 1 + x_1^2 - x_1 x_2^2 + x_2^4$.
Given the monomial vector $Z(x) = [1 \quad x_1 \quad x_2 \quad x_1 x_2 \quad x_2^2]^\top$, the corresponding Gram matrix is parametrized by $\alpha_1$, $\alpha_2$, and $\alpha_3$:

$$
Q_p = \begin{bmatrix}
1 & 0 & 0 & \alpha_1 & \alpha_2 \\ 
0 & 1 & -\alpha_1 & 0 & \alpha_3 \\ 
0 & -\alpha_1 & -2\alpha_2 & -0.5 -\alpha_3 & 0 \\
\alpha_1 & 0 & -0.5 - \alpha_3 & 0 & 0 \\
\alpha_2 & \alpha_3 & 0 & 0 & 1 \\
\end{bmatrix}.
$$

To account for this non-uniqueness, the parameters $\alpha_k$ can be introduces as a decision variables of the resulting conic problem, thereby parametrizing the entire family of decompositions.
If there exists a parametrization $\alpha_1$, $\alpha_2$, and $\alpha_3$ such that $Q_p ≽ 0$, then $p(x)$ is proven to be an SOS polynomial.

For a large Gram matrix $Q_p$ many additional decision variables $\alpha_k$ can significantly increase computational effort.
To mitigate this, a heuristic can be applied to preselect specific values for $\alpha_k$, converting the problem without introducing new decision variables.

In the above example, this heuristic selects $\alpha_1=0$, $\alpha_2=0$, and $\alpha_3=0$.
However, this selection can make the SOS problem infeasible.
To disable this heuristic (enabled by default) set `sparse_smr` argument to `False` when initializing the state object:

<!-- This heuristic is enabled by default and can be disabled when initializing the state object: -->

``` python
state = sosopt.init_state(sparse_smr=False)
```

An SOS decomposition of $p(x)$ can be computed by solving the following feasibility problem, which involves a single SOS constraint.
The following code snipped also prints the symbol of the decision variables associated with the SOS problem.
Since the polynomial $p(x)$ does not contain any decision variables, and the SOS decomposition introduces new decision variables only during the conversion to a conic problem, the resulting SOS problem does not define any decision variables.  

``` python
# Define polynomial variables
state_variables = tuple(polymat.define_variable(name) for name in ('x1', 'x2'))
x1, x2 = state_variables

# Create polynomial and SOS constraint
p = x1**2 - x1*x2**2 + x2**4 + 1

state, sos_constraint = sosopt.sos_constraint(
    name="p",
    greater_than_zero=p,
).apply(state)

# Formulate SOS problem (feasibility formulation)
sos_problem = sosopt.sos_problem(
    constraints=(sos_constraint,),
    solver=sosopt.cvxopt_solver,
)

# No decision variables are defined so far
# Output: empty tuple
print(sos_problem.decision_variable_symbols)

# Solve SOS problem
context, sos_result = sos_problem.solve().apply(context)
```

The parametrized Gram matrix can be accessed through a field `gram_matrix` of the SOS constraint object `sos_constraint`.
Once the feasibility problem is solved, the Gram matrix can be extracted by evaluating its parameters with the solution of the SOS problem.

``` python
# Evaluate the decomposition variables with the results of the SOS problem
Qp = sos_constraint.gram_matrix.eval(sos_result.symbol_values)

# Convert the polynomial expression to sympy for printing
state, Qp_sympy = polymat.to_sympy(Qp).apply(state)
```

See [examples/sosdecomposition](../examples/sosdecomposition.md) for a full example on how to recover the SOS decomposition of a polynomial $p(x)$.

## Conic Problem Conversion


Solving the SOS problem using `sos_problem.solve()` involves two transformations:

1. Conversion of the SOS problem to a conic optimization problem
2. Representation of the conic problem in solver-specific array form

We can perform just the first conversion using `sos_problem.to_conic_problem()` method.
This step introduces decomposition variables associated with the SOS constraints.

``` python
# Convert to conic problem (introduces decomposition variables)
state, conic_problem = sos_problem.to_conic_problem().apply(state)

# SOS decomposition decision variables are defined
# Output: ('p')
print(conic_problem.decision_variable_symbols)
```

The conic problem defines a symbol *p*, which corresponds to the three decision variables $\alpha_1$, $\alpha_2$, and $\alpha_3$ introduced during the conversion.

The second transformation can be partially performed using the `cone_problem.to_solver_args()` method.

``` python
# Convert to argument provided to the conic solver
state, solver_args = conic_problem.to_solver_args().apply(state)

# Inspect conic problem after SOS decomposition
# Output:
# Number of decision variables: 3
# Quadratic cost: False
# Semidefinite constraints: 1
#   1. 5x5
# Equality constraints: 0
# Variables: {'p_0': 5, 'p_1': 6, 'p_2': 7}
print(solver_args.to_summary())

# Inspect semidefinite cone and equality arrays used by the conic solvers
print(solver_args.semidef_cone)
print(solver_args.equality)
```

The `to_summary()` method provides a high-level overview of the conic problem.
Additionally, the arrays corresponding to semidefinite and equality constraints can be accessed via the `semidef_cone` and `equality` attributes.

Finally, the conic problem can be solve, and the result printed:

``` python
# Solving the conic problem yields the same results
state, conic_result = conic_problem.solve().apply(state)

# Print the result
# Outputs: {'p': (1.483747804557867e-17, -0.26054977051314515, -0.9998902845804934)}
print(conic_result.symbol_values)
```



<!-- Finally, we can compute the SOS decomposition non-uniquely through the following procedure:

<!-- ``` python
# Retrieve monomial basis and SMR from the SOS constraint
Z = constraint.primitives[0].sos_monomial_basis
Qp = constraint.primitives[0].sos_smr

# Evaluate the decomposition variables with the results of the SOS problem
Qp_eval = Qp.eval(sos_result.symbol_values)

# Output matrix as nested tuples
state, Qp_np = polymat.to_tuple(Qp_eval).map(np.array).apply(state)

# Use SVD decomposition instead of Cholesky decomposition
_, S, V = np.linalg.svd(Qp_np)

# Vector of polynomials
q = polymat.from_(np.diag(np.sqrt(S)) @ V) @ Z
```

$$
\left[\begin{matrix}- 0.842676173311175 x_{1} + 0.87081565437922 x_{2}^{2} - 0.219583175233309\\0.967686064293247 - 0.252158047606349 x_{1}\\- 0.475723854731912 x_{1} - 0.491609698936151 x_{2}^{2} - 0.123963341868085\\- 0.00010747125133889 x_{1} x_{2} + 0.510440761022419 x_{2}\\0.000107471251338855 x_{1} x_{2} + 2.26276401618244 \cdot 10^{-8} x_{2}\end{matrix}\right]
$$

The original polynomial can be recoverd by $p(x) = q(x)^\top q(x)$. -->
