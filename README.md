# IRIS SHEAR tools

This repository contains utilities for calculating IRIS SHEAR products and
dealing with IRIS SHEAR products calculated by IRIS.

The IRIS SHEAR algorithm is property of Vaisala Inc, details can be found in [the IRIS Product and Display manual](ftp://ftp.sigmet.com/outgoing/manuals/IRIS_Product_and_Display_Manuals.pdf).


## Functions


Module                       | Description
-----------------------------| ------------------------------------------------
[`utils.py`](utils.py)       | Utility functions.
[`iris_shear/iris.pyx`](iris.pyx) | Cython functions for the IRIS SHEAR algorithms. Should be compiled with `python setup.py build_ext --inplace`, after which the functions can be accessed through `iris_tools` module.


The script [`create_pgm_from_IRIS_shear_prod.py`](create_pgm_from_IRIS_shear_prod.py) script can be used to create PGM images from original, raw IRIS SHEAR products.
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


Author: [Jenna Ritvanen](mailto:jenna.ritvanen@fmi.fi)
