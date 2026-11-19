import numpy as np
from scipy.ndimage import uniform_filter
import xarray as xr
from typing import Literal, cast
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


# Backscatter conventions
#
# NRB is delivered as gamma0. The other conventions are calculated from it with the
# conversion layers that come with each item:
#
# | Convention | Calculation |
# | --- | --- |
# | `gamma0` | As delivered |
# | `sigma0_dem` | `gamma0 * oa_gamma0_to_sigma0_ratio` |
# | `sigma0_ellipsoid` | `gamma0 * oa_gamma0_to_beta0_ratio * sin(oa_incidence_angle)` |
# | `beta0` | `gamma0 * oa_gamma0_to_beta0_ratio` |
#
# Over Antarctica, gamma0 and DEM sigma0 can show artifacts from errors in the DEM used in
# processing. Ellipsoid sigma0 doesn't use the DEM, so it avoids them.

Convention = Literal["gamma0", "sigma0_dem", "sigma0_ellipsoid", "beta0"]

CONVENTIONS = ("gamma0", "sigma0_dem", "sigma0_ellipsoid", "beta0")

BETA0_RATIO = "oa_gamma0_to_beta0_ratio"
SIGMA0_RATIO = "oa_gamma0_to_sigma0_ratio"
INCIDENCE_ANGLE = "oa_incidence_angle"

REQUIRED_LAYERS = {
    "gamma0": (),
    "sigma0_dem": (SIGMA0_RATIO,),
    "sigma0_ellipsoid": (BETA0_RATIO, INCIDENCE_ANGLE),
    "beta0": (BETA0_RATIO,),
}


def _check_convention(convention: str) -> None:
    if convention not in CONVENTIONS:
        raise ValueError(f"convention must be one of {CONVENTIONS}, got: {convention!r}")


def _gamma0_bands(names) -> list[str]:
    return [str(name) for name in names if str(name).lower().endswith("_gamma0")]


def convert_backscatter(
    ds: xr.Dataset,
    convention: Convention,
    drop_layers: bool = True,
) -> xr.Dataset:
    """Convert the gamma0 bands of a dataset to another backscatter convention.

    Each `<polarisation>_gamma0` band is replaced by `<polarisation>_<convention>`, in linear scale.
    Works on lazy (dask) and computed data. Convert to decibels afterwards, if required.

    Parameters
    ----------
    ds : xr.Dataset
        Data with one or more `<polarisation>_gamma0` bands in linear scale, and the conversion
        layers the convention needs (see `REQUIRED_LAYERS`)
    convention : Convention
        One of "gamma0", "sigma0_dem", "sigma0_ellipsoid" or "beta0"
    drop_layers : bool, optional
        Whether to drop the conversion layers used, by default True

    Returns
    -------
    xr.Dataset
        The dataset with the backscatter in the requested convention. Other bands are kept.
        `attrs["backscatter_convention"]` records the convention

    Raises
    ------
    ValueError
        the convention is unknown, the dataset has no gamma0 bands, or a conversion layer is missing
    """
    _check_convention(convention)
    gamma0_bands = _gamma0_bands(ds.data_vars)
    if not gamma0_bands:
        raise ValueError(f"Dataset has no <polarisation>_gamma0 bands to convert. Bands: {list(ds.data_vars)}")
    missing = [name for name in REQUIRED_LAYERS[convention] if name not in ds.data_vars]
    if missing:
        raise ValueError(f"Converting to {convention} needs the {missing} layer(s), which the dataset doesn't have")

    converted = ds.copy()
    for name in gamma0_bands:
        gamma0 = ds[name]
        if convention == "gamma0":
            continue
        with xr.set_options(keep_attrs=True):
            if convention == "sigma0_dem":
                values = gamma0 * ds[SIGMA0_RATIO]
            elif convention == "sigma0_ellipsoid":
                values = convert_gamma0_to_sigma0_ellipsoid_xr(gamma0, ds[BETA0_RATIO], ds[INCIDENCE_ANGLE])
            else:
                values = gamma0 * ds[BETA0_RATIO]
        new_name = name[: -len("gamma0")] + convention
        converted[new_name] = values.rename(new_name)
        converted = converted.drop_vars(name)

    if drop_layers:
        converted = converted.drop_vars(list(REQUIRED_LAYERS[convention]))
    converted.attrs["backscatter_convention"] = convention
    return converted
