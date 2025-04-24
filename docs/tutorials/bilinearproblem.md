# Handling bilinear SOS Problems

The SOS problem returned by `sosopt.sos_problem` may include a cost function and constraints that do not depend linearly on the decision variables.
If such a non-linear SOS problem is passed to the solver, an exception is raised.
To solve a bilinear SOS Problem using the alternating algorithm, a set of decision variables -- that appear bilinearly -- must be substituted with the values obtained from the previous iteration.
This transformation is performed by calling the `eval` method on the SOS problem:

``` python
# defines decision variable substitutions
symbol_values = {
    u.symbol: (0, -1, -1),
}

# create an SOS problem that is linear in its decision variable
# by substituting a group of decision variables
problem = problem.eval(symbol_values)
```

Performing this substitution at the SOS problem level is crucial, as different substitution choices lead to different SDP formulations, affecting computational efficiency and numerical stability.

See [examples/bilinearproblem](../examples/bilinearproblem.md) for a full example on how to evaluate a bilinear SOS problem.