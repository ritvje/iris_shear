"""Utility functions for dealing with IRIS products."""
import os
import gzip
import logging
import numpy as np
from datetime import timedelta
from scipy.ndimage.filters import generic_filter
from scipy.ndimage.interpolation import map_coordinates
import matplotlib.pyplot as plt


def read_vvp(path, filepattern, date, altitude="lowest"):
    """Read VVP data.

    Reads VVP data located at path, and returns the wind vector
    at elevation closest to the requested altitude.

    Parameters
    ----------
    path : str
        Path to directory containing VVP data.
    filepattern : str
        The filepatttern using placeholders for time.
    date : datetime.datetime
        The current time.
    altitude : str or float-like
        The requested altitude. Either altitude in meters or 'lowest'.

    Returns:
    --------
    u : float
        Zonal velocity.
    v : float
        Meridional velocity.

    """
    # Floor date down to 15 minutes
    d = date - timedelta(
        minutes=date.minute % 15,
        seconds=date.second,
        microseconds=date.microsecond)
    fn = os.path.join(path, d.strftime(filepattern))
    data = np.loadtxt(fn, skiprows=3)

    if isinstance(altitude, str):
        print("str")
        if str == "lowest":
            ind = -1
        else:
            logging.error(
                "VVP altitude option '%s' not implement!" % altitude)
    elif isinstance(altitude, (int, float)):
        alts = data[:, 0]
        ind = np.abs(alts - altitude).argmin()
    else:
        ind = -1
        logging.error(
            "VVP altitude option '%s' not implement!" % str(altitude))

    ws = data[ind, 3]
    wd = data[ind, 5]

    # Calculate wind components based on speed and direction
    u = (-1) * np.abs(ws) * np.sin(np.radians(wd))
    v = (-1) * np.abs(ws) * np.cos(np.radians(wd))

    return u, v


def iris_declutter(data, range_filter_len, az_filter_len, vel_thr_pc=0.02):
    """Declutter velocity data according to the IRIS SHEAR algorithm.

    Parameters
    ----------
    data : numpy.ma.array
        The velocity data, with azimuth along 0-axis and range along 1-axis.
    range_filter_len : int
        The Range Filter Length in bins.
    az_filter_len : int
        The Azimuth Filter Length in bins.
    vel_thr_pc : float
        The percentage threshold for clutter bins, defaults to 0.02 (2%).

    Returns
    -------
    data : np.ma.array
        The declutteed velocity data.

    """
    clutter_range_filter_len = range_filter_len // 3
    clutter_az_filter_len = az_filter_len // 3
    # Get the threshold for velocity below which values are filtered out
    vel_thr = np.quantile(np.abs(data), vel_thr_pc)
    clutter_candidates = np.abs(data.filled()) < vel_thr
    clutter_candidates[data.mask] = False
    clutter_n = generic_filter(
        clutter_candidates.astype(int), np.count_nonzero,
        size=(clutter_az_filter_len, clutter_range_filter_len))
    data[(clutter_n > 0) &
         (clutter_n <= clutter_range_filter_len)] = np.ma.masked
    return data


def read_shear_pgm(filename, gzipped=False, dtype=np.float32):
    """Read a shear image from a PGM file.

    The image should contain 8-bit shear magnitude values. The image is
    treated as byte data ('rb'-flag used when opening files).

    Parameters
    ----------
    filename : str
        The file to read from.
    gzipped : bool
        If True, the input file is treated as a compressed gzip file.
    dtype : data-type
        The data type into which the resulting array is converted to.

    Returns
    -------
    out : ndarray
        Two-dimensional array containing the image.
    params : dict
        Dictionary of parameters describind the data.

    """
    if not gzipped:
        R = plt.imread(filename)
        f = open(filename, 'rb')
    else:
        R = plt.imread(gzip.open(filename, 'rb'))
        f = gzip.open(filename, 'rb')

    params = {}
    line = f.readline().decode()
    while line[0] != '#':
        line = f.readline().decode()
    while line[0] == '#':
        line = f.readline().decode()
    line = f.readline().decode()
    missingval = int(line)
    f.close()

    missingval = 0
    nodataval = 255

    MASK = R == missingval
    R = R.astype(dtype)
    R[MASK] = np.nan
    MASK = R == nodataval
    R = R.astype(dtype)
    R[MASK] = -np.inf

    R = (R - 128) * 0.2
    return R, params


def polar_to_cart(polar_data, theta_step, range_step, x, y,
                  range_start=0, order=1, cval=-np.inf):
    """Reproject polar data to cartesian grid.

    From https://stackoverflow.com/a/16695217

    Order 1 is recommended to obtain results that minize interpolation
    (results remind simply plotting the polar data in cartesian form).

    Parameters
    ----------
    polar_data : numpy.ndarray
        The data that is reprojected. The first axis is the azimuth
        angles and the second is the range.
    theta_step : float
        The step in azimuth angles.
    range_step : float
        The step in ranges.
    x : numpy.ndarray
        The new x coordinates.
    y : numpy.ndarray
        The new y coordinates.
    range_start : float
        The offset for ranges from center of polar coordinate system.
    order : int
        The order of spline interpolation, defaults to 1.
    cval : float
        The value that used to pixels outside original grid. Defaults to
        -inf.

    Returns
    -------
    cart_data : numpy.ndarray
        The data reprojected onto new coordinates.
    """

    # "x" and "y" are numpy arrays with the desired cartesian coordinates
    # we make a meshgrid with them
    X, Y = np.meshgrid(x, y)

    # Now that we have the X and Y coordinates of each point in the output
    # plane we can calculate their corresponding theta and range
    Tc = np.degrees(np.arctan2(Y, X)).ravel()
    Rc = (np.sqrt(X ** 2 + Y ** 2)).ravel()

    # Negative angles are corrected
    Tc[Tc < 0] = 360 + Tc[Tc < 0]

    # Using the known theta and range steps, the coordinates are mapped to
    # those of the data grid
    Tc = Tc / theta_step
    Rc = Rc / range_step

    # An array of polar coordinates is created stacking the previous arrays
    coords = np.vstack((Tc, Rc))

    # To avoid holes in the 360º - 0º boundary, the last column of the data
    # copied in the beginning
    polar_data = np.vstack((polar_data, polar_data[-1, :]))

    # The data is mapped to the new coordinates
    # Values outside range are substituted with cval
    cart_data = map_coordinates(polar_data, coords, order=order,
                                mode='constant', cval=cval)

    # The data is reshaped and returned
    return (cart_data.reshape(len(y), len(x)).T)
