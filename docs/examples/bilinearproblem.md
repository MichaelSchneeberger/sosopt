# Bilinear SOS Problem

This example ensures stability of a dynamical system

$$
\dot x = f(x) + G(x) u(x) = \begin{bmatrix}x_2 + x_1^2 - x_1^3 \\ 0\end{bmatrix} + \begin{bmatrix}0 \\ 1\end{bmatrix} u(x)
$$

by finding a polynomial Lyapunov function $V(x)$.
This involves finding a positive definite scalar polynomial $V(x)$ (i.e., $V(x) > 0$ for $x \neq 0$ and $V(0) = 0$), which satisfies for all $x$:

$$
\dot V(x) = \nabla V(x)^\top \left ( f(x) + G(x) u(x) \right ) < 0.
$$


Given the Square Matricial Representation (SMR)

$$
V(x) = Z(x)^\top Q_V Z(x),
$$

the SOS problem encoding these condition is selected as:

$$
\begin{array}{ll}
    \text{find} & Q_V \\
    \text{minimize} & \text{tr}( Q_V ) \\
    \text{subject to} & \nabla V(x)^\top \left ( f(x) + G(x) u(x) \right ) + 0.1 x^\top x \leq 0 \quad \forall x \\
    & V(x) - 0.1 x^\top x \geq 0 \quad \forall x.
\end{array}
$$




``` python
--8<-- "examples/bilinearproblem.py"
```
