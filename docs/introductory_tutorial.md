# Introductory Tutorial

SOSOpt is a Python library designed for solving sums-of-squares (SOS) optimization problems.
It is build on top of the PolyMat Python library, which provides tools for representing and manipulating multivariate polynomial matrices.
SOSOpt leverages PolyMat's functionality to construct and solve polynomial expressions that arise in SOS optimization problem.

<!-- What do we do in thsi tutorial? -->
<!-- In this introductory tutorial, we will:
* define polynomial and decision variables, define a polynomial containing polynomial and decision variables
* 
-->

## Constructing polynomial expressions

<!-- SOSOpt is build on top of the PolyMat Python library. -->
To define a polynomial variable, use `polymat.define_variable` method. This variable can then be used to build polynomial expressions using algebraic manipulations.

``` Python
polynomial_variable_names = ('x_1', 'x_2')
polynomial_variables = tuple(polymat.define_variable(name) for name in polynomial_variable_names)
x1, x2 = polynomial_variables
x = polymat.v_stack(polynomial_variables)
```

In contrast, to define a decision variable to be used in the SDP solver, use the `sosopt.define_variable` method. Such a decision variable can be manipulated in the same manner as a polynomial variable.

``` Python
decision_variable_names = ('c_1', 'c_2', 'c_3', 'c_4', 'c_5')
decision_variables = tuple(sosopt.define_variable(name) for name in decision_variable_names)
c1, c2, c3, c4, c5 = decision_variables
```

Given the polynomial variables $x_1$, $x_2$ and decision variables $c_1$, ..., $c_5$, a new polynomial object $r(x)$ can be defined using algebraic operations such as +, -, *, **, /, and other operations such as trace, transpose, and differentiation:

``` Python
r = -1 + c1 * x1 + c2 * x2 + c3 * x1**2 + c4 * x1*x2 + c5 * x2**2
```

Alternatively, a parametrized polynomial $r(x)$ can be constructed using `sosopt.define_polynomial`. 
This function eliminates the need to manually define decision variables for each monomial of the polynomial:

``` Python
r_var = sosopt.define_polynomial('r', monomials=x.combinations(degrees=(1,2)))
r = -1 + r_var
```

All the polynomial matrix objects create above are implemented as instances of `polymat.Expression`.
These objects represent polynomial matrix expressions using a abstract syntax tree (AST) structure.
This AST-based representation allows for for efficient manipulation and evaluation of polynomial expressions.

<!-- All output operations require to compute an internal sparse representation of the polynomial matrix based on a state object.
This state object provides information to build an internal sparse representation, and to store information for future construction of the internal sparse representation.  -->
<!-- To compute the polynomial matrix from the expression -->
<!-- an abstract description of the polynomial matrix expression. -->
<!-- , representing an abstract description of the polynomial matrix. -->
<!-- expression of a polynomial matrix containing different types of variables. -->
<!-- To compute the polynomial matrix resulting from the expression -->


## Printing and debugging expressions

The PolyMat library provides various **output operations** to convert these polynomial matrix expressions into different formats, such as:
* A symbolic representation using `sympy`
* A numerical array representation.

To perform these output operations, PolyMat first computes an **internal sparse representation** of the polynomial matrix.
This computation relies on a **state object**, which:
* Provides the necessary information to construct the internal sparse representation.
* Stores metadata and intermediate data to facilitate future constructions of the sparse representation, improving efficiency for repeated operations.

``` Python
state = polymat.init_state()
```

<!-- To enable the creation of an actual polynomial representation -->
<!-- To print the actual polynomial from an expression -->
<!-- Any PolyMat expression can be converted to a `sympy` expression, enabling esay and visually appealing printing. -->

The `sympy` representation enables easy and visually appealing printing.
The following will output: $c_0 x_1 + c_1 x_2 + c_2 x_1^2 + c_3 x_1 x_2 + c_4 x_2^2 - 1$.

``` Python
state, r_sympy = polymat.to_sympy(r).apply(state)
r_sympy
```
