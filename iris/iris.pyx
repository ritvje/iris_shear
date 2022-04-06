# cython: profile=True
import numpy as np
cimport numpy as cnp
cimport cython

cpdef enum padmode:
    WRAP = 0
    CONSTANT = 1
    EDGE = 2

@cython.boundscheck(False)
@cython.wraparound(False)
def diff_radial(cnp.ndarray[cnp.float64_t, ndim=2] data,
                cnp.ndarray[cnp.int_t, ndim=2] mask,
                unsigned int range_filter_len):
    """Calculate the radial difference as required in the IRIS algorithm.

    Parameters
    ----------
    data : numpy.array of type np.float64
        The velocity data, with azimuth along 0-axis and range along 1-axis.
    mask : numpy.array of type np.int
        The mask of the data.
    range_filter_len : int
        The Range Filter Length in bins.

    Returns
    -------
    res : 2d numpy array
        The resulting difference array with same shape as data.
    """

    # Initialize result
    cdef cnp.ndarray[cnp.float64_t, ndim=2] res

    cdef unsigned int i, j, n, jt, nt
    cdef unsigned int n_az = data.shape[0]
    cdef unsigned int n_r = data.shape[1]
    cdef unsigned int rf = range_filter_len // 2 + 1

    res = np.zeros((n_az, n_r), dtype=np.float64)

    for i in range(n_az):
        for j in range(n_r):
            if not mask[i, j]:
                for n in range(rf):
                    nt = j + n + 1
                    if ((nt < n_r) and not mask[i, nt]):
                        jt = j + (n + 1) // 2
                        # Get the first value that is not masked and inside
                        # the filter limit
                        res[i, jt] = data[i, j] - data[i, nt]
                        break
    return res


@cython.boundscheck(False)
@cython.wraparound(False)
def diff_azimuthal(cnp.ndarray[cnp.float64_t, ndim=2] data,
                   cnp.ndarray[cnp.int_t, ndim=2] mask,
                   unsigned int az_filter_len,
                   padmode pad_mode=WRAP):
    """Calculate the azimuthal difference as required in the IRIS algorithm.

    Example usage:

    ```python
    import numpy as np
    from iris import iristools

    data = np.random.randn(360, 500).astype(np.float64)
    mask = (np.abs(data) > 0.7).astype(np.int)
    # With continuous/wrap padding
    az_diff_wrap = iristools.diff_azimuthal(data, mask, 3)

    # With constant zero padding
    az_diff_const = iristools.diff_azimuthal(data, mask, 3, iristools.padmode.CONSTANT)

    # With edge padding
    az_diff_edge = iristools.diff_azimuthal(data, mask, 3, iristools.padmode.EDGE)

    assert np.any(az_diff_wrap != az_diff_const)
    ```

    Parameters
    ----------
    data : numpy.array of type np.float64
        The velocity data, with azimuth along 0-axis and range along 1-axis.
    mask : numpy.array of type np.int
        The mask of the data.
    az_filter_len : int
        The Azimuth Filter Length in bins.
    pad_mode : enum padmode
        The method used for padding the data to handle edges of the image.
        WRAP (default) works for data that is continuous along azimuth.
        CONSTANT pads with empty values and works for non-continous data.
        EDGE pads with edge values and works for non-continuous data.

    Returns
    -------
    res : 2d numpy array
        The resulting difference array with same shape as data.
    """
    # Initialize result
    cdef cnp.ndarray[cnp.float64_t, ndim=2] res
    cdef cnp.ndarray[cnp.float64_t, ndim=2] pad_data
    cdef cnp.ndarray[cnp.int_t, ndim=2] pad_mask

    cdef unsigned int i, j, n, it, nt
    cdef unsigned int n_az = data.shape[0]
    cdef unsigned int n_r = data.shape[1]
    cdef unsigned int aft = az_filter_len // 2
    cdef unsigned int af = aft + 1
    cdef unsigned int pad_n_az = n_az + aft

    res = np.zeros((n_az, n_r), dtype=np.float64)
    # We have to pad the data along first axis so that there are no gaps
    if pad_mode == WRAP:
        # data is continuous along azimuth angles
        pad_mask = np.vstack((mask, mask[0:aft, :]))
        pad_data = np.pad(data, ((0, aft), (0,0)), 'wrap')
    elif pad_mode == CONSTANT:
        # data is not continuous, pad with zero
        pad_mask = np.vstack((mask, np.zeros((aft, n_r), dtype=np.int)))
        pad_data = np.pad(data, ((0, aft), (0,0)), 'constant', constant_values=0.0)
    elif pad_mode == EDGE:
        # data is not continuous, pad with zero
        pad_mask = np.vstack((mask, np.zeros((aft, n_r), dtype=np.int)))
        pad_data = np.pad(data, ((0, aft), (0,0)), 'edge')

    for j in range(n_r):
        for i in range(n_az):
            if not pad_mask[i, j]:
                for n in range(af):
                    nt = i + n + 1
                    it = i + (n + 1) // 2
                    if ((nt < pad_n_az) and (it < n_az) and not pad_mask[nt, j]):
                        # Get the first value that is not masked and inside
                        # the filter limit
                        # Also the location where we put the result has to be
                        # inside the image
                        res[it, j] = pad_data[i, j] - pad_data[nt, j]
                        break
    return res
