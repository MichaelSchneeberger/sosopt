# Home

**SOSOpt** is a Python library designed for solving sums-of-squares (SOS) optimization problems.


## Features

* *PolyMat* integration: Extends the [*PolyMat*](https://github.com/MichaelSchneeberger/polymat) ecosystem by introducing a new variable type for decision variables.
* High-performance: While languages like *Matlab* (via *SOSTOOLS*) and *Julia* (via *SumOfSqaures.jl*) offer powerful SOS solvers, Python lack a comparable native implementation. **SOSOpt** fills this gap by providing a high-performance SOS optimization library.
* Multiple Evaluations: Supports advanced workflows, including multiple evaluations of SOS problems and efficient substitutions of decision variables in a bilinear SOS formulations.


## Installation

You can install **SOSOpt** using pip:

```
pip install sosopt
```