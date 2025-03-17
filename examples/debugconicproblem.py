import numpy as np
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

conic_problem = problem.to_conic_problem()

state, args = conic_problem.to_solver_args().apply(state)

# Conic problem summary
#######################

# print solver argument summary
print(args.to_summary())

# improve string representation of numpy arrays
np.set_printoptions(precision=2, threshold=1000, linewidth=1000, suppress=True)

# print linear cost of conic problem
print(f'Linear cost={args.lin_cost.to_numpy(1)}')

# print matrices encoding semidefinite constraints
if args.semidef_cone:
    print('Data encoding semidefinite constraints:')
    for array in args.semidef_cone:
        print(f'- const={array.to_numpy(0)}')
        print(f'- linear={array.to_numpy(1)}')

# print matrices encoding equality constraints
if args.equality:
    print('Data encoding equality constraints:')
    for array in args.equality:
        print(f'- const={array.to_numpy(0)}')
        print(f'- linear={array.to_numpy(1)}')
