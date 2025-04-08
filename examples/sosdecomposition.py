import numpy as np
import polymat
import sosopt

state = sosopt.init_state(sparse_smr=False)

# Define polynomial variables
state_variables = tuple(polymat.define_variable(name) for name in ('x1', 'x2'))
x1, x2 = state_variables
x = polymat.v_stack(state_variables)

# Create polynomial and SOS constraint
p = x1**2 - x1*x2**2 + x2**4 + 1

state, constraint = sosopt.sos_constraint(
    name="p",
    greater_than_zero=p,
).apply(state)

# Formulate SOS problem (feasibility formulation)
sos_problem = sosopt.sos_problem(
    constraints=(constraint,),
    solver=sosopt.cvxopt_solver,
)

# No decision variables are defined so far
# Output: empty tuple
print(sos_problem.decision_variable_symbols)

# Solve SOS problem
state, sos_result = sos_problem.solve().apply(state)

# Retrieve monomial basis and SMR from the SOS constraint
Z = constraint.sos_monomial_basis
Qp = constraint.gram_matrix

# Evaluate the decomposition variables with the results of the SOS problem
Qp_eval = Qp.eval(sos_result.symbol_values)

# Output matrix as nested tuples
state, Qp_np = polymat.to_tuple(Qp_eval).map(np.array).apply(state)

# Use SVD decomposition instead of Cholesky decomposition
_, S, V = np.linalg.svd(Qp_np)

# Vector of polynomials
q = polymat.from_(np.diag(np.sqrt(S)) @ V) @ Z

state, q_sympy = polymat.to_sympy(q).apply(state)
print(q_sympy)

state, p_sympy = polymat.to_sympy(q.T @ q).apply(state)
print(p_sympy)
