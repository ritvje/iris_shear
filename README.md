# IRIS SHEAR tools

This repository contains utilities for calculating IRIS SHEAR products and
dealing with IRIS SHEAR products calculated by IRIS.

The IRIS SHEAR algorithm is property of Vaisala Inc, details can be found in [the IRIS Product and Display manual](ftp://ftp.sigmet.com/outgoing/manuals/IRIS_Product_and_Display_Manuals.pdf).

## Installation

Before installing, remove possible old versions:
```bash
cd demo # Can't remove in main directory
pip uninstall iris
cd ..
```

The package can then be installed locally with `pip install ./`.


## Functions

Module                       | Description
-----------------------------| ------------------------------------------------
[`utils`](utils.py)       | Utility functions.
[`iristools`](iris.pyx) | Cython functions for the IRIS SHEAR algorithms. Has functions for calculating radial azimuthal differences.


The script [`create_pgm_from_IRIS_shear_prod.py`](scripts/create_pgm_from_IRIS_shear_prod.py) script can be used to create PGM images from original, raw IRIS SHEAR products.
To do this, in addition to the IRIS products, header information is required.
It can be obtained with the `productx` utility program on servers where IRIS is installed. To run it on some set of IRIS products and save the output into text files, use for example the following bash snippet:

```bash
#!/bin/bash

for f in VAN170812*.SHED9*; do
	t=${f%.SHED9*}.txt
	productx $f > $t
done
```

The expression in the for-loop should be changed so, that when used with `ls`, it gives the desired product list. Change also the `.SHED9*` inside the loop to match the filename extensions.

## Generating documentation

To generate documentation, use e.g. [`pdoc3`](https://pdoc3.github.io/pdoc/). Installation `pip install pdoc3`.

Generating documentation is apparently a bit tricky due to the Cython module.
At least the following works.

```bash
# In main directory
python setup.py build_ext --inplace
pdoc3 --html -o docs --force ./iris
mv docs/iris/* docs/
rm -rf docs/iris
```

Author: [Jenna Ritvanen](mailto:jenna.ritvanen@fmi.fi)
