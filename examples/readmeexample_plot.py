import numpy as np
import numpy.matlib
from matplotlib import pyplot
import polymat
import sosopt

state = polymat.init_state()

variable_names = ("x_1", "x_2", "x_3")
x1, x2, x3 = tuple(polymat.define_variable(name) for name in variable_names)
x = polymat.v_stack((x1, x2, x3))

w1 = ((x1 + 0.3) / 0.5) ** 2 + (x2 / 20) ** 2 + (x3 / 20) ** 2 - 1
w2 = ((x1 + 0.3) / 20) ** 2 + (x2 / 1.3) ** 2 + (x3 / 1.3) ** 2 - 1

r_var = sosopt.define_polynomial(
    name="r",
    monomials=x.combinations(degrees=(1, 2)),
    polynomial_variables=x,
)
r = r_var - 1

state, sympy_repr = polymat.to_sympy(r).apply(state)
print(f"r={sympy_repr}")

state, constraint = sosopt.psatz_putinar_constraint(
    name="rpos",
    smaller_than_zero=r,
    domain=sosopt.set_(
        smaller_than_zero={
            "w1": w1,
            "w2": w2,
        },
    ),
).apply(state)

Qr_diag = r.to_gram_matrix(x).diag()

problem = sosopt.sos_problem(
    lin_cost=-Qr_diag.sum(),
    quad_cost=Qr_diag,
    constraints=(constraint,),
    solver=sosopt.cvx_opt_solver,
)

state, sos_result = problem.solve().apply(state)

# materialize polynomials w1(x), w2(x), and r(x), allowing to evaluate these
# polynomials for specified vectors
state, w1_array = polymat.to_array(w1, x).apply(state)
state, w2_array = polymat.to_array(w2, x).apply(state)
state, r_array = polymat.to_array(r.eval(sos_result.symbol_values), x).apply(state)


# Plot results
##############

pyplot.close()
fig = pyplot.figure(figsize=(6, 6))
ax = fig.subplots()

# define 2D projection for plotting
proj = lambda x, y: np.array((x, y, 0)).reshape(-1, 1)

# create mesh (i_d, i_q)
ticksX = np.arange(-2, 1, 0.04)
ticksY = np.arange(-2, 2, 0.04)
n_row, n_col = len(ticksY), len(ticksX)
X = np.matlib.repmat(ticksX, n_row, 1)
Y = np.matlib.repmat(ticksY.reshape(-1, 1), 1, n_col)

# plot contour of zero-sublevel sets {x | w1(x) <= 0}, {x | w2(x) <= 0}, 
# and {x | r(x) <= 0}
Z_eq = np.vectorize(lambda x, y: w1_array(proj(x, y)))(X, Y)
Z_eq = np.vectorize(lambda x, y: w2_array(proj(x, y)))(X, Y)
Z_eq = np.vectorize(lambda x, y: r_array(proj(x, y)))(X, Y)
ax.contour(X, Y, Z_eq, [0], linewidths=0.5, colors=["#A0B1BA"])
ax.contour(X, Y, Z_eq, [0], linewidths=0.5, colors=["#A0B1BA"])
ax.contour(X, Y, Z_eq, [0], linewidths=2, colors=["#A0B1BA"])

# plot box-like set with red dashed lines
x_min, x_max, y_min, y_max = -0.8, 0.2, -1.3, 1.3
args = {"color": "#FF1F5B", "linestyle": "dashed", "linewidth": 2}
ax.plot(np.array((x_min, x_max)), np.array((y_min, y_min)), **args)
ax.plot(np.array((x_min, x_max)), np.array((y_max, y_max)), **args)
ax.plot(np.array((x_min, x_min)), np.array((y_min, y_max)), **args)
ax.plot(np.array((x_max, x_max)), np.array((y_min, y_max)), **args)

pyplot.show()
