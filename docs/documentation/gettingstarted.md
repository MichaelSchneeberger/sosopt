
# Gettings Started

**SOSOpt** is dedicated to solving the sums-of-squares (SOS) optimization problem, offering advanced support for multiple evaluations and substitutions of decision variables.
The SOS optimization problem under consideration is formulated as:

$$
    \begin{array}{ll}
        \text{find} & \theta, \\
        \text{minimize} & c(\theta) + q(\theta)^\top q(\theta) \\
        % c^\top \theta + (Q \theta)^\top Q \theta \\
        \text{subject to} & p_k(x; \theta) \in \Sigma[x] \quad \forall k \\
        & l(\theta) = 0. % & A \theta = b.
     \end{array}
$$

where $c(\theta)$, $q(\theta)$, $p_k(x; \theta)$, and $l(\theta)$ are polynomial expression in polynomial variable $x$ and decision variable $\theta$.
When solving the SOS problem, an exception is raised when one of these polynomial expression does not depend linearly on the decision variable $\theta$.



## Variables

The polynomial variable $x$ and decision variable $\theta$ are both build within the *PolyMat* ecosystem.
By convention, native *PolyMat* variables -- created via `polymat.define_variable` -- are interpretated as polynomial variables.
In contrast, decision variables are introduced by extending the *PolyMat* framework with a new variable type.
The following example defines a decision variable $\theta$ consisting of three components and uses it to construct a polynomial expression in the previously defined polynomial variable $x$.

``` python
import sosopt

# define three decision variables
theta_0 = sosopt.define_variable('theta_0')
theta_1 = sosopt.define_variable('theta_1')
theta_2 = sosopt.define_variable('theta_2')

# parametrized polynomial containing both polynomial and decision variable
r = theta_0 + theta_1 * x + theta_2 * x**2
```

Alternatively, the construction of a fully parametrized polynomial -- involving the specification of a decision variable for each coefficient of the polynomial -- is automated using the `sosopt.define_polynomial` function:

``` python
# creates a monomial vector [1 x x^2]
monomials = x.combinations(degrees=range(3))

# creates a parametrized polynomial r = r_0 + r_1 x + r_2 x^2
r = sosopt.define_polynomial(name='r', monomials=monomials)

# returns a polymat vector [r_0, r_1, r_2] containing the coefficients
r.coefficient
```

Furthermore, a parametrized polynomial matrix can be created by additionally specifying the `row` and `col` arguments:

``` python
Q = sosopt.define_polynomial(
    name='Q', 
    monomials=monomials,
    n_rows=n, n_cols=m,
)
```


## Polynomial Constraints

Compared to other SOS libraries, **SOSOpt** defines standalone constraints, not requiring a link to a concrete SOS problem.
In *SOSTOOLS*, a `Program` object is used to define the SOS constraint `sosineq(Program, r);`.
In *SumOfSqaures.jl*, a `model` object is used to define the SOS constraint `@constraint(model, r >= 0)`.
The `state` object takes a comparable role of such an object as a container of shared data.
However, in **SOSOpt**, the usage of an SOS constraint returned by the function `sosopt.sos_constraint` is not restricted to a single SOS program, making this approach more modular when working with different SOS problems.
The state object is created as follows.

``` python
state = sosopt.init_state()
```

The polynomial constraints in the SOS problem can be defined in **SOSOpt** as follows:

### **Zero Polynomial Constraint**

This polynomial constraint ensures that a polynomial expression is zero as a polynomial: All coefficients of the polynomials must be zero.

The following constraint:

``` python
state, r_zero_constraint = sosopt.zero_polynomial_constraint(
    name='r_zero',
    equal_to_zero=r,
).apply(state)
```

enforces the coefficients of $r(x)$ to be zero:

$$\text{Coeff}(r(x)) = 0.$$

### **SOS Constraint**

This polynomial constraint ensures that a scalar polynomial expression belongs to the SOS Cone.

The following constraint:
``` python
state, r_sos_constraint = sosopt.sos_constraint(
    name='r_sos',
    greater_than_zero=r,
).apply(state)
```
enforces the SOS constraint:

$$r(x) \in \Sigma[x].$$

### **SOS Matrix Constraint**

This polynomial constraint ensures a polynomial matrix expression belongs to the SOS Matrix Cone.

The following constraint:
``` python
state, q_sos_constraint = sosopt.sos_matrix_constraint(
    name='q_sos',
    greater_than_zero=q,
).apply(state)
```
enforces the SOS constraint:

$$v^\top q(x) v \in \Sigma[x, v].$$

### **Quadratic Module Constraint**

This polynomial constraint defines a non-negativity condition on a subset of the states space using a quadratic module construction following Putinar's Positivstellensatz.

The following constraint:
``` python
state, r_qm_constraint = sosopt.quadratic_module_constraint(
    name='r_qm',
    greater_than_zero=r,
    domain=sosopt.set_(
        smaller_than_zero={'w': w},
    )
).apply(state)
```
enforces the SOS constraints:

$$\gamma_w(x) \in \Sigma[x]$$

$$r(x) + \gamma_w(x) w(x) \in \Sigma[x].$$

<!-- ### **Equality Constraint**

This constraint enforces a polynomial expression to be equal to zero.

The following constraint:

``` python
state, e_eq_constraint = sosopt.equality_constraint(
    name='e_eq',
    equal_to_zero=e,
).apply(state)
```

enforces the expression $e$ to be zero:

$$e = 0.$$

### **Semi-definite Constraint**

This constraint enforces a symmetric matrix expression to be positive semidefinite.

The following constraint:

``` python
state, q_psd_constraint = sosopt.semidefinite_constraint(
    name='q_psd',
    greater_than_zero=q,
).apply(state)
```

enforces the expression $q$ to be positive semidefinite:

$$q ≽ 0.$$ -->



## Defining an SOS Problem

An SOS problem is defined using the `sosopt.sos_problem` function taking as arguments:
- `lin_cost`: Scalar expression $c(\theta)$ defining the linear cost.
- `quad_cost`: Vector expression $q(\theta)$ defining the quadratic cost $q(\theta)^\top q(\theta)$.
- `constraints`: SOS and equality constraints
- `solver`: SDP solver selection (*CVXOPT* or *MOSEK*)

``` python
problem = sosopt.sos_problem(
    lin_cost=Q.trace(),
    quad_cost=Q.diag(),
    constraints=(r_sos_constraint,),
    solver=polymat.cvxopt_solver,
)

# solve SOS problem
state, result = problem.solve().apply(state)
```

The `solve` method converts the SOS problem to an SDP, solves the SDP using the provided solver, and maps the result to a dictionary `result.symbol_values`.



<!-- ## Handling bilinear SOS Problems

The SOS problem returned by `sosopt.sos_problem` may include a cost function and constraints that do not depend linearly on the decision variables.
If such a non-linear SOS problem is passed to the solver, an exception is raised.
To solve a bilinear SOS Problem using the alternating algorithm, a set of decision variables -- that appear bilinearly -- must be substituted with the values obtained from the previous iteration.
This transformation is performed by calling the `eval` method on the SOS problem:

``` python
# defines decision variable substitutions
symbol_values = {
    r.symbol: (1, 0, 1)
}

# create an SOS problem that is linear in its decision variable
# by substituting a group of decision variables
problem = problem.eval(symbol_values)
``` -->



<!-- ## SOS Decomposition and SDP Conversion

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
``` -->