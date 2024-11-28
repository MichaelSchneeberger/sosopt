import polymat
import sosopt

# Initialize the state object, which is passed through all operations related to solving
# the SOS problem
state = polymat.init_state()

# Define polynomial variables and stack them into a vector
variable_names = ("x_1", "x_2", "x_3")
x1, x2, x3 = tuple(polymat.define_variable(name) for name in variable_names)
x = polymat.v_stack((x1, x2, x3))

# Define the cylindrical constraint ([-0.8, 0.2], [-1.3, 1.3]) as the
# intersection of the zero-sublevel sets of two polynomials, w1 and w2.
w1 = ((x1 + 0.3) / 0.5) ** 2 + (x2 / 20) ** 2 + (x3 / 20) ** 2 - 1
w2 = ((x1 + 0.3) / 20) ** 2 + (x2 / 1.3) ** 2 + (x3 / 1.3) ** 2 - 1

# Define a polynomial where the coefficients are decision variables in the SOS problem
r_var = sosopt.define_polynomial(
    name='r',
    monomials=x.combinations(degrees=(1, 2)),
    polynomial_variables=x,
)
# Fix the constant part of the polynomial to -1 to ensure numerical stability
r = r_var - 1

# Prints the symbol representation of the polynomial:
# r = r_0*x_1 + r_1*x_2 + ... + r_8*x_3**2 - 1
state, sympy_repr = polymat.to_sympy(r).apply(state)
print(f'r={sympy_repr}')

# Apply Putinar's Positivstellensatz to ensure the cylindrical constraints (w1 and w2) 
# are contained within the zero sublevel set of r.
state, constraint = sosopt.sos_constraint_putinar(
    name="rpos",
    smaller_than_zero=r,
    domain=sosopt.set_(
        smaller_than_zero={
            "w1": w1,
            "w2": w2,
        },
    ),
).apply(state)

# Minimize the volume surrogate of the zero-sublevel set of r
Qr_diag = r.to_gram_matrix(x).diag()

# Define the SOS problem
problem = sosopt.sos_problem(
    lin_cost=-Qr_diag.sum(),
    quad_cost=Qr_diag,
    constraints=(constraint,),
    solver=sosopt.cvx_opt_solver,   # choose solver
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