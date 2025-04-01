# Operations


## Defining Optimization Variables

- **Decision variable**: Use `sosopt.define_variable` to create a decision variable for the SOS Problem. Any variables created with `polymat.define_variable` are treated as polynomial variables.
- **Polynomial variable**: Define a polynomial matrix variable with entries that are parametrized polynomials, where the coefficients are decision variables, using `sosopt.define_polynomial`.
- **Matrix variable**: Create a symmetric $n \times n$ polynomial matrix variable using `sosopt.define_symmetric_matrix`.
- **Multipliers***: Given a reference polynomial, create a polynomial variable intended for multiplication with the reference polynomial, ensuring that the resulting polynomial does not exceed a specified degree using `sosopt.define_multiplier`. 


## Operations on Polynomial Expressions

- **SOS Monomial Basis**: Construct a monomial vector $Z(x)$ for the quadratic form of the polynomial $p(x) = Z(x)^\top Q Z(x)$.
    ``` python
    p_monom = sosopt.sos_monomial_basis(r, x)
    # Matrix([[1], [x], [x**2]])
    ```
- **SOS Monomial Basis**: Construct a sparse monomial vector $Z(x)$ for the quadratic form of the polynomial $p(x) = Z(x)^\top Q Z(x)$.
    ``` python
    p_monom = sosopt.sos_monomial_basis_sparse(r, x)
    # Matrix([[1], [x], [x**2]])
    ```
`sosopt.sos_monomial_basis`
`sosopt.sos_monomial_basis_sparse`
- **Square Matricial Representation**: `sosopt.sos_smr`
`sosopt.sos_smr_sparse`


## Defining Sets

- **Semialgebraic set**: Define a semialgebraic set from a collection scalar polynomial expressions with `sosopt.set_`.


## Defining Constraints

- **Zero Polynomial***: Enforce a polynomial expression to be equal to zero using `sosopt.zero_polynomial_constraint`.
- **Sum-of-Sqaures (SOS)***: Define a scalar polynomial expression within the SOS Cone using `sosopt.sos_constraint`.
- **SOS Matrix***: Define a polynomial matrix expression within the SOS Matrix Cone using `sosopt.sos_matrix_constraint`.
- **Putinar's P-satz***: Encode a positivity condition for a polynomial matrix expression on a semialgebraic set using `sosopt.putinar_psatz_constraint`.

## Defining the SOS Optimization Problem

- **Solver Arguments***: Convert polynomial expression to their array representations, which are required for defining the SOS problem, using `sosopt.solver_args`.
- **SOS Problem**: Create an SOS Optimization problem using the solver arguments with `sosopt.sos_problem`.


\* These operations return a state monad object. To retrieve the actualy result, you need to call the `apply` method on the returned object, passing the state as an argument.
