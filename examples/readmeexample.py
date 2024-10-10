from donotation import do
import statemonad
import polymat
import sosopt

# The state object is passed through all operations involved in solveing 
# the SOS problem.
state = polymat.init_state()

# Define the polynomial variables and stack them into one vector.
variable_names = ("x_1", "x_2", "x_3")
x1, x2, x3 = tuple(polymat.define_variable(name) for name in variable_names)
x = polymat.v_stack((x1, x2, x3))

# Encode the cylindrical constraint ([-0.8, 0.2], [-1.3, 1.3]) as the
# intersection of the zero-sublevel sets of two polynomials w1 and w2.
w1 = ((x1 + 0.3) / 0.5) ** 2 + (x2 / 20) ** 2 + (x3 / 20) ** 2 - 1
w2 = ((x1 + 0.3) / 20) ** 2 + (x2 / 1.3) ** 2 + (x3 / 1.3) ** 2 - 1

# Define a polynomial variables whose coefficients are all decision variables
# of the resulting SOS problem.
r_var = sosopt.define_polynomial(
    name='r',
    monomials=x.combinations(degrees=(1, 2)),
    polynomial_variables=x,
)
# Fix the constant part of the polynomial to 1 to ensure numerical stability.
r = r_var - 1

# Prints the symbol representation of the polynomial variable
# r_poly_var = 
#   r_0*x_1 + r_1*x_2 + r_2*x_3 + r_3*x_1**2 + r_4*x_1*x_2 
#   + r_5*x_1*x_3 + r_6*x_2**2 + r_7*x_2*x_3 + r_8*x_3**2 - 1
state, sympy_repr = polymat.to_sympy(r).apply(state)
print(f'r={sympy_repr}')

# use the do notation to avoid calling `apply(state)` method
@do()
def define_sos_problem():

    # Use Putinar's Positivstellensatz to ensure the containment of
    # the cylindrical constraints encoded by w1 and w2 within the zero
    # sublevel set of r.
    constraint = yield from sosopt.sos_constraint_putinar(
        name="rpos",
        smaller_than_zero=r,
        domain=sosopt.set_(
            smaller_than_zero={
                "w1": w1,
                "w2": w2,
            },
        ),
    )

    # Collect all constraints
    constraints = (constraint,)

    # Minimize a surrogate of the volume of the zero sublevel set of r.
    r_diag = r.to_gram_matrix(x).diag()

    problem = yield from sosopt.sos_problem(
        lin_cost=-r_diag.sum(),
        quad_cost=r_diag,
        constraints=constraints,
        solver=sosopt.cvx_opt_solver,   # choose solver
        # solver=sosopt.mosek_solver,
    )

    return statemonad.from_(problem)

# define the SOS problem
state, problem = define_sos_problem().apply(state)

# solve the SOS problem
state, sos_result = problem.solve().apply(state)

# Prints a dictionary that maps each symbol to its corresponding value found by the solver:
# sos_result.symbol_values={
#   'r': (0.5442930462735407, 7.960826937815216e-28, 1.5901672575501424e-25, ...), 
#   'r_w1_gamma': (0.22625415065548013,), 
#   'r_w2_gamma': (0.8553898002589362,)}
print(f'{sos_result.symbol_values=}')

print(f'{sos_result.solver_data.status}')      # Output will be 'optimal'
print(f'{sos_result.solver_data.iterations}')  # Output will be 6
print(f'{sos_result.solver_data.cost}')        # Output will -1.2523582776230828
print(f'{sos_result.solver_data.solution}')    # Output will array([ 5.44293046e-01, ...])