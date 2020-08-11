# cython: profile=True
import numpy as np
cimport numpy as cnp
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def diff_radial(cnp.ndarray[cnp.float64_t, ndim=2] data,
                cnp.ndarray[cnp.int_t, ndim=2] mask,
                unsigned int range_filter_len):
    """ Calculate the radial difference as required in the IRIS algorithm.

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
                   unsigned int az_filter_len):
    """ Calculate the azimuthal difference as required in the IRIS algorithm.

    Parameters
    ----------
    data : numpy.array of type np.float64
        The velocity data, with azimuth along 0-axis and range along 1-axis.
    mask : numpy.array of type np.int
        The mask of the data.
    az_filter_len : int
        The Azimuth Filter Length in bins.

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
    # (since data is continuous along azimuth angles)
    pad_mask = np.vstack((mask, mask[0:aft, :]))
    pad_data = np.pad(data, ((0, aft), (0,0)), 'wrap')

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
