import numpy as np
from scipy.ndimage import uniform_filter
import xarray as xr
from typing import cast
import dask.array as dsa


# function for converting linear to decibels for xarray.DataArray
def convert_linear_to_db_xr(da: xr.DataArray, epsilon: float = 1e-10) -> xr.DataArray:

    # The function clips values less than epsilon to avoid introducing -Inf
    clipped = da.clip(min=epsilon)
    with xr.set_options(keep_attrs=True):
        db = cast(xr.DataArray, 10 * np.log10(clipped))

    return db


# function for converting gamma0 to ellipsoid sigma0 for xarray.DataArray
def convert_gamma0_to_sigma0_ellipsoid_xr(
    gamma0: xr.DataArray,
    gamma0_to_beta0_ratio: xr.DataArray,
    incidence_angle: xr.DataArray,
) -> xr.DataArray:
    """Convert gamma0 backscatter to ellipsoid sigma0, which is relative to the ground, without terrain.

    The conversion is:
    beta0 = gamma0 * gamma0_to_beta0_ratio
    sigma0_ellipsoid = beta0 * sin(incidence_angle)

    Parameters
    ----------
    gamma0 : xr.DataArray
        The gamma0 backscatter in linear scale. Convert the result to decibels afterwards, if required.
    gamma0_to_beta0_ratio : xr.DataArray
        The per-pixel conversion from gamma0 to beta0, e.g. `oa_gamma0_to_beta0_ratio`
    incidence_angle : xr.DataArray
        The angle between the line-of-sight vector and the ellipsoid normal vector, in degrees, e.g. `oa_incidence_angle`

    Returns
    -------
    xr.DataArray
        The ellipsoid sigma0 backscatter in linear scale
    """
    with xr.set_options(keep_attrs=True):
        beta0 = gamma0 * gamma0_to_beta0_ratio
        sigma0_ellipsoid = cast(xr.DataArray, beta0 * np.sin(np.radians(incidence_angle)))

    return sigma0_ellipsoid
