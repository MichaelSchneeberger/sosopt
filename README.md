# SOSOpt

**SOSOpt** is a Python library designed for solving sums-of-squares (SOS) optimization problems.


## Features

* *PolyMat* integration: Extends the [*PolyMat*](https://github.com/MichaelSchneeberger/polymat) ecosystem by introducing a new variable type for decision variables.
Native *PolyMat* variables are interpretated as polynomial variables, enabling seamless creation of expressions that mix both polnyomial and decision variables.
* High-performance: While languages like *Matlab* (via *SOSTOOLS*) and *Julia* (via *SumOfSqaures.jl*) offer powerful SOS solvers, Python lack a comparable native implementation. **SOSOpt** fills this gap by providing a high-performance SOS optimization library.
* Multiple Evaluations: Supports advanced workflows, including multiple evaluations of SOS problems and efficient substitutions of decision variables in a bilinear SOS formulations.
<!-- * Data-oriented design: Key components such as decision variables, SOS constraints, and SOS problems are implemented as structured data types, facilitating efficient inspection and debugging. -->
<!-- * Stateful Computation: The sparse internal structures are computed based on a state object. This eliminates any dependency on global variables and provides control over the sparse intermediate structures stored in memory for reuse. -->
<!-- * Pythonic code structure: Designed with a programming-oriented syntax, avoiding unnatural adaptations of Python dunder methods to match mathematical notation. -->
<!-- * Stateful computation: Built on the [`statemonad`](https://github.com/MichaelSchneeberger/state-monad) framework, ensuring that data objects requiring evaluation of `polymat` expressions are handled in a functional, state-aware manner. -->


## Installation

You can install **SOSOpt** using pip:

```
pip install sosopt
```

## Basic Usage

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

### Variables

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

Alternatively, the construction of a fully parametrized polynomial -- involving the specificatioin of a decision variable for each coefficient of the polynomial -- is automated using the `sosopt.define_polynomial` function:

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
    rows=n, cols=m,
)
```

### Polynomial Constraints

The polynomial constraints in the SOS problem can be defined in **SOSOpt** as follows:

- **Equality Constraint**: This constraint enforces a polynomial expression to be equal to zero.
    The following constraint:
    ``` python
    r_zero_constraint = sosopt.zero_polynomial_constraint(
        name='r_zero',
        equal_to_zero=r,
    )
    ```
    enforces the equality constraint:

    $$r(x) = 0.$$
- **SOS Constraint**: This constraint ensures that a scalar polynomial expression belongs to the SOS Cone.
    The following constraint:
    ``` python
    r_sos_constraint = sosopt.sos_constraint(
        name='r_sos',
        greater_than_zero=r,
    )
    ```
    enforces the SOS constraint:

    $$r(x) \in \Sigma[x].$$
- **SOS Matrix Constraint**: This constraint ensures a polynomial matrix expression belongs to the SOS Matrix Cone.
    The following constraint:
    ``` python
    q_sos_constraint = sosopt.sos_matrix_constraint(
        name='q_sos',
        greater_than_zero=q,
    )
    ```
    enforces the SOS constraint:

    $$v^\top q(x) v \in \Sigma[x, v].$$
- **Quadratic Module Constraint**: This constraint defines a non-negativity condition on a subset of the states space using a quadratic module construction following Putinar's Positivstellensatz.
    The following constraint:
    ``` python
    r_qm_constraint = sosopt.quadratic_module_constraint(
        name='r_qm',
        greater_than_zero=r,
        domain=sosopt.set_(
            smaller_than_zero={'w': w},
        )
    )
    ```
    enforces the SOS constraints:

    $$\gamma_w(x) \in \Sigma[x]$$

    $$r(x) + \gamma_w(x) w(x) \in \Sigma[x].$$

### Defining an SOS Problem

An SOS problem is defined using the `sosopt.sos_problem` function taking as arguments:
- `lin_cost`: Scalar expression $c(\theta)$ defining the linear cost.
- `quad_cost`: Vector expression $q(\theta)$ defining the quadratic cost $q(\theta)^\top q(\theta)$.
- `constraints`: SOS and equality constraints
- `solver`: SDP solver selection (*CVXOPT* or *MOSEK*)

Compared to other SOS libraries, **SOSOpt** defines standalone constraints, not requiring a link to a concrete SOS problem.
In *SOSTOOLS*, a `Program` object is used to define the SOS constraint `sosineq(Program, r);`.
In *SumOfSqaures.jl*, a `model` object is used to define the SOS constraint `@constraint(model, r >= 0)`.
The `context` object takes a comparable role of such an object as a container of shared data.
However, in \textit{SOSOpt}, the usage of an SOS constraint returned by the function `sosopt.sos_constraint` is not restricted to a single SOS program, making this approach more modular when working with different SOS problems.

``` python
problem = sosopt.sos_problem(
    lin_cost=Q.trace(),
    quad_cost=Q.diag(),
    constraints=(r_sos_constraint,),
    solver=polymat.cvxopt_solver,
)

# solve SOS problem
context, result = problem.solve().apply(context)
```

The `solve` method converts the SOS problem to an SDP, solves the SDP using the provided solver, and maps the result to a dictionary `result.symbol_values`.

### Handling bilinear SOS Problems

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
```

### SOS Decomposition and SDP Conversion

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
This heuristic is enabled by default and can be disabled as follows:

``` python
problem = sosopt.sos_problem(
    lin_cost=Q.trace(),
    quad_cost=Q.diag(),
    constraints=(r_sos_constraint,),
    solver=solver,
    sparse_gram =False,
)
```


## Operations


### Defining Optimization Variables

- **Decision variable**: Use `sosopt.define_variable` to create a decision variable for the SOS Problem. Any variables created with `polymat.define_variable` are treated as polynomial variables.
- **Polynomial variable**: Define a polynomial matrix variable with entries that are parametrized polynomials, where the coefficients are decision variables, using `sosopt.define_polynomial`.
- **Matrix variable**: Create a symmetric $n \times n$ polynomial matrix variable using `sosopt.define_symmetric_matrix`.
- **Multipliers***: Given a reference polynomial, create a polynomial variable intended for multiplication with the reference polynomial, ensuring that the resulting polynomial does not exceed a specified degree using `sosopt.define_multiplier`. 


### Defining Sets

- **Semialgebraic set**: Define a semialgebraic set from a collection scalar polynomial expressions with `sosopt.set_`.


### Defining Constraint

- **Zero Polynomial***: Enforce a polynomial expression to be equal to zero using `sosopt.zero_polynomial_constraint`.
- **Sum-of-Sqaures (SOS)***: Define a scalar polynomial expression within the SOS Cone using `sosopt.sos_constraint`.
- **SOS Matrix***: Define a polynomial matrix expression within the SOS Matrix Cone using `sosopt.sos_matrix_constraint`.
- **Putinar's P-satz***: Encode a positivity condition for a polynomial matrix expression on a semialgebraic set using `sosopt.putinar_psatz_constraint`.

### Defining the SOS Optimization Problem

- **Solver Arguments***: Convert polynomial expression to their array representations, which are required for defining the SOS problem, using `sosopt.solver_args`.
- **SOS Problem**: Create an SOS Optimization problem using the solver arguments with `sosopt.sos_problem`.


\* These operations return a state monad object. To retrieve the actualy result, you need to call the `apply` method on the returned object, passing the state as an argument.



## Example

This example illustrates how to define and solve a simple SOS optimization problem using **SOSOpt**.

In this example, we aim to compute the coefficients of a polynomial $r(x)$ whose zero-sublevel set contains the box-like set defined by the intersection of the zero-sublevel sets of polynomials $w_1(x)$ and $w_2(x)$:

$$\mathcal X_\text{Box} := \lbrace x \mid w_1(x) \leq 0, w_2(x) \leq 0 \rbrace$$

The polynomial $r(x)$ is parameterized by the symmetric matrix $Q_r$, and is expressed as:

$$r(x) := Z(x)^\top Q_r Z(x)$$

where $Z(x)$ is a vector of monomials in $x$.

The SOS optimization problem is formulated to find $r(x)$ that maximizes the surrogate for the volume of the zero-sublevel set of $r(x)$, represented by the trace of $Q_r$. 
The resulting SOS problem is defined as:

$$\begin{array}{ll}
    \text{find} & Q_r \in \mathbb R^{m \times m} \\
    \text{minimize} & \text{tr}( Q_r ) + \text{diag}( Q_r )^\top \text{diag}( Q_r ) \\
    \text{subject to} & r(x) < 0 \quad \forall x \in \mathcal X_\text{Box} \\
\end{array}$$

This formulation seeks to minimize the trace of $Q_r$ while ensuring that $r(x)$ is negative within the box-like set $\mathcal X_\text{Box}$.

``` python
import polymat
import sosopt

# Initialize the state object, which is passed through all operations related to solving
# the SOS problem
state = polymat.init_state()

# Define polynomial variables and stack them into a vector
variable_names = ("x_1", "x_2", "x_3")
x1, x2, x3 = tuple(polymat.define_variable(name) for name in variable_names)
x = polymat.v_stack((x1, x2, x3))

# Define the box-like set as the intersection of the zero-sublevel sets of two
# polynomials w1 and w2.
w1 = ((x1 + 0.3) / 0.5) ** 2 + (x2 / 20) ** 2 + (x3 / 20) ** 2 - 1
w2 = ((x1 + 0.3) / 20) ** 2 + (x2 / 1.3) ** 2 + (x3 / 1.3) ** 2 - 1

# Define a polynomial where the coefficients are decision variables in the SOS problem
r_var = sosopt.define_polynomial(
    name='r',
    monomials=x.combinations(degrees=(1, 2)),
)
# Fix the constant part of the polynomial to -1 to ensure numerical stability
r = r_var - 1

# Prints the symbol representation of the polynomial:
# r(x) = r_0*x_1 + r_1*x_2 + ... + r_8*x_3**2 - 1
state, sympy_repr = polymat.to_sympy(r).apply(state)
print(f'r={sympy_repr}')

# Apply Putinar's Positivstellensatz to ensure the box-like set, encoded by w1 and w2, 
# is contained within the zero sublevel set of r(x).
state, constraint = sosopt.putinar_psatz_constraint(
    name="rpos",
    smaller_than_zero=r,
    domain=sosopt.set_(
        smaller_than_zero={
            "w1": w1,
            "w2": w2,
        },
    ),
).apply(state)

# Minimize the volume surrogate of the zero-sublevel set of r(x)
Qr_diag = sosopt.gram_matrix(r, x).diag()

# Define the SOS problem
problem = sosopt.sos_problem(
    lin_cost=-Qr_diag.sum(),
    quad_cost=Qr_diag,
    constraints=(constraint,),
    solver=sosopt.cvxopt_solver,   # choose solver
    # solver=sosopt.mosek_solver,
)

# Solve the SOS problem
state, sos_result = problem.solve().apply(state)

# Output the result
# Prints the mapping of symbols to their correspoindg vlaues found by the solver
print(f'{sos_result.symbol_values=}')

# Display solver data such as status, iterations, and final cost.
print(f'{sos_result.solver_data.status}')      # Expected output: 'optimal'
print(f'{sos_result.solver_data.iterations}')  # Expected output: 6
print(f'{sos_result.solver_data.cost}')        # Expected output: -1.2523582776230828
print(f'{sos_result.solver_data.solution}')    # Expected output: array([ 5.44293046e-01, ...])
```

This figure illustrates the contour of the zero-sublevel sets of the resulting polynomial $r(x)$:

![sos problem result](docs/images/readmeexample_plot.png)



## Reference

Below are some references related to this project:

* [PolyMat](https://github.com/MichaelSchneeberger/polymat) is a Python library designed for the representation and manipulation of multivariate polynomial matrices.
* [Advanced safety filter](https://github.com/MichaelSchneeberger/advanced-safety-filter) includes Jupyter notebooks that model and simulate the concept of an advanced safety filter using **SOSOpt**.
* [SumOfSqaures.py](https://github.com/yuanchenyang/SumOfSquares.py) is a simple sum-of-squares Python library built on *sympy*, leading to increased computation time when converting an SOS problem into a SDP.
* [SOSTOOLS](https://github.com/oxfordcontrol/SOSTOOLS) powerful SOS solver written in $MATLAB$.
* [SumOfSqaures.jl](https://github.com/jump-dev/SumOfSquares.jl) powerful SOS solver written in $Julia$.
