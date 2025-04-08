from __future__ import annotations

from sosopt.state.init import (
    init_state as _init_state,
)
from sosopt.solvers.cvxoptsolver import CVXOPTSolver
from sosopt.solvers.moseksolver import MosekSolver
from sosopt.solvers.solveargs import to_solver_args as _get_solver_args
from sosopt.semialgebraicset import set_ as _set_
from sosopt.polymat.from_ import (
    define_multiplier as _define_multiplier,
    define_polynomial as _define_polynomial,
    define_symmetric_matrix as _define_symmetric_matrix,
    define_variable as _define_variable,
    gram_matrix as _gram_matrix,
    sos_monomial_basis as _sos_monomial_basis,
)
from sosopt.polymat.to import to_symbol_values as _to_symbol_values
from sosopt.coneconstraints.from_ import(
    equality_constraint as _equality_constraint,
    semi_definite_constraint as _semidefinite_constraint,
)
from sosopt.polynomialconstraints.from_ import (
    sos_constraint as _sos_constraint,
    zero_polynomial_constraint as _zero_polynomial_constraint,
    sos_matrix_constraint as _sos_matrix_constraint,
    quadratic_module_constraint as _psatz_putinar_constraint,
)
from sosopt.sosproblem import init_sos_problem as _init_sos_problem

init_state = _init_state

to_symbol_values = _to_symbol_values

cvxopt_solver = CVXOPTSolver()
mosek_solver = MosekSolver()

gram_matrix = _gram_matrix
sos_monomial_basis = _sos_monomial_basis

# Defining Optimization Variables
define_variable = _define_variable
define_polynomial = _define_polynomial
define_symmetric_matrix = _define_symmetric_matrix
define_multiplier = _define_multiplier

# Defining Sets
set_ = _set_

# Defining Cone Constraints
equality_constraint = _equality_constraint
semidefinite_constraint = _semidefinite_constraint

# Defining Polynomial Constraints
zero_polynomial_constraint = _zero_polynomial_constraint
sos_constraint = _sos_constraint
sos_psd_constraint = _sos_matrix_constraint      # depricated?
sos_matrix_constraint = _sos_matrix_constraint
psatz_putinar_constraint = _psatz_putinar_constraint      # depricated?
putinar_psatz_constraint = _psatz_putinar_constraint
quadratic_module_constraint = _psatz_putinar_constraint

# Defining the SOS Optimization Problem
solver_args = _get_solver_args
sos_problem = _init_sos_problem
