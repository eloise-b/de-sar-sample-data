from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable, Mapping, Optional, Union

import matplotlib.pyplot as plt
from matplotlib.colors import Colormap, LinearSegmentedColormap
import numpy as np
import xarray as xr

from de_sar_demo.sar_utils import convert_linear_to_db_xr

PercentilePair = tuple[float, float]
Percentiles = Union[PercentilePair, Mapping[str, PercentilePair]]

# Deep blue at low backscatter, through to white at high backscatter
ICE_BLUE = LinearSegmentedColormap.from_list(
    "ice_blue", ["#010a17", "#082f5b", "#2f7fbc", "#9bd0ea", "#ffffff"]
)


def _backscatter_bands(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    """Return the backscatter bands of a dataset, keyed by lowercase polarisation."""
    bands = {}
    for name in ds.data_vars:
        match = re.fullmatch(r"(hh|hv|vv|vh)_(gamma0|sigma0_ellipsoid)", str(name).lower())
        if match:
            if match.group(1) in bands:
                raise ValueError(
                    f"Dataset has more than one backscatter band for {match.group(1)}: "
                    f"{bands[match.group(1)].name} and {name}. Select the one to display."
                )
            bands[match.group(1)] = ds[name]
    return bands


def _require_bands(ds: xr.Dataset, *polarisations: str) -> list[xr.DataArray]:
    """Return the requested polarisations, or raise if any are missing."""
    bands = _backscatter_bands(ds)
    missing = [pol for pol in polarisations if pol not in bands]
    if missing:
        raise ValueError(
            f"Style needs polarisation(s) {missing}, but the dataset only has {sorted(bands)}"
        )
    return [bands[pol] for pol in polarisations]


def _single_band(ds: xr.Dataset) -> xr.DataArray:
    """Return the co-polarised band if there is one, otherwise the only band."""
    bands = _backscatter_bands(ds)
    for pol in ("hh", "vv", "hv", "vh"):
        if pol in bands:
            return bands[pol]
    raise ValueError("Dataset has no backscatter bands")


def _co_and_cross_bands(ds: xr.Dataset) -> tuple[xr.DataArray, xr.DataArray]:
    """Return the co-polarised and cross-polarised bands of a dual-pol dataset."""
    bands = _backscatter_bands(ds)
    for co_pol, cross_pol in (("vv", "vh"), ("hh", "hv")):
        if co_pol in bands and cross_pol in bands:
            return bands[co_pol], bands[cross_pol]
    raise ValueError(
        f"Style needs VV+VH or HH+HV bands, but the dataset only has {sorted(bands)}"
    )


def _ice_blue_channels(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    hh = _require_bands(ds, "hh")[0]
    return {"value": convert_linear_to_db_xr(hh)}


def _greyscale_db_channels(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    return {"value": convert_linear_to_db_xr(_single_band(ds))}


def _false_colour_linear_channels(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    vv, vh = _require_bands(ds, "vv", "vh")
    return {"red": vv, "green": vh, "blue": vh / vv}


def _dual_pol_db_channels(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    co_pol, cross_pol = _co_and_cross_bands(ds)
    co_pol_db = convert_linear_to_db_xr(co_pol)
    cross_pol_db = convert_linear_to_db_xr(cross_pol)
    return {"red": co_pol_db, "green": cross_pol_db, "blue": co_pol_db - cross_pol_db}


def _multitemporal_channels(ds: xr.Dataset) -> dict[str, xr.DataArray]:
    band = _single_band(ds)
    if "time" not in band.dims or band.sizes["time"] < 3:
        raise ValueError(
            "Style 'multitemporal_rgb' needs a dataset with at least 3 time steps"
        )
    # Average in linear scale within three windows holding near-equal time steps
    band = band.sortby("time")
    windows = np.array_split(np.arange(band.sizes["time"]), 3)
    return {
        channel: convert_linear_to_db_xr(band.isel(time=window).mean("time"))
        for channel, window in zip(("red", "green", "blue"), windows)
    }


@dataclass(frozen=True)
class Style:
    """A named way of turning linear gamma0 bands into an image.

    Parameters
    ----------
    title : str
        A human readable name for the style
    channels : Callable[[xr.Dataset], dict[str, xr.DataArray]]
        Calculates the values to display from a dataset of linear backscatter bands.
        Returns either a "value" channel, or "red", "green" and "blue" channels
    scale_ranges : Mapping[str, tuple[float, float]]
        The default (low, high) display range for each channel
    cmap : Optional[Colormap]
        The colour map for styles with a single "value" channel, by default None
    uses_time : bool
        Whether the style uses the time dimension, rather than a single image, by default False
    """

    title: str
    channels: Callable[[xr.Dataset], dict[str, xr.DataArray]]
    scale_ranges: Mapping[str, tuple[float, float]]
    cmap: Optional[Colormap] = None
    uses_time: bool = False


STYLES = {
    "ice_blue": Style(
        title="HH white-to-blue ice scale (dB)",
        channels=_ice_blue_channels,
        scale_ranges={"value": (-20.0, 0.0)},
        cmap=ICE_BLUE,
    ),
    "greyscale_db": Style(
        title="Single band greyscale (dB)",
        channels=_greyscale_db_channels,
        scale_ranges={"value": (-20.0, 0.0)},
        cmap=plt.get_cmap("bone"),
    ),
    "vv_vh_false_colour_linear": Style(
        title="VV+VH False Colour",
        channels=_false_colour_linear_channels,
        scale_ranges={
            "red": (0.00978187, 0.2739456),
            "green": (0.00096179, 0.06779868),
            "blue": (0.01472214, 4.3769968),
        },
    ),
    "dual_pol_db": Style(
        title="Dual-pol composite: co-pol, cross-pol, co-pol minus cross-pol (dB)",
        channels=_dual_pol_db_channels,
        scale_ranges={"red": (-20.0, 0.0), "green": (-28.0, -6.0), "blue": (0.0, 15.0)},
    ),
    "multitemporal_rgb": Style(
        title="Multi-temporal composite: early, middle and late periods as RGB (dB)",
        channels=_multitemporal_channels,
        scale_ranges={"red": (-20.0, 0.0), "green": (-20.0, 0.0), "blue": (-20.0, 0.0)},
        uses_time=True,
    ),
}

_DEFAULT_STYLE_BY_POLARISATION = {
    "hh_hv": "dual_pol_db",
    "vv_vh": "vv_vh_false_colour_linear",
    "hh": "ice_blue",
    "vv": "greyscale_db",
}


def default_style_for_collection(collection: str) -> str:
    """Choose the default style for a collection, based on its polarisation.

    Parameters
    ----------
    collection : str
        The name of the collection, e.g. `ga_s1_nrb_iw_hh_1`

    Returns
    -------
    str
        The name of a style in `STYLES`

    Raises
    ------
    ValueError
        the polarisation could not be found in the collection name
    """
    match = re.search(r"_(hh_hv|vv_vh|hh|vv)_", collection.lower())
    if match is None:
        raise ValueError(f"Could not find a polarisation in collection: {collection}")
    return _DEFAULT_STYLE_BY_POLARISATION[match.group(1)]


def _percentiles_by_channel(
    percentiles: Optional[Percentiles], channels: Mapping[str, xr.DataArray]
) -> dict[str, PercentilePair]:
    """Expand the percentiles argument to a dictionary, keyed by channel."""
    if percentiles is None:
        return {}
    if isinstance(percentiles, Mapping):
        unknown = sorted(set(percentiles) - set(channels))
        if unknown:
            raise ValueError(
                f"Unknown channel(s) {unknown} in percentiles. Style has channels: {list(channels)}"
            )
        by_channel = dict(percentiles)
    else:
        by_channel = {channel: percentiles for channel in channels}

    for channel, (low, high) in by_channel.items():
        if not 0 <= low < high <= 100:
            raise ValueError(
                f"Percentiles for channel '{channel}' must satisfy 0 <= low < high <= 100, got ({low}, {high})"
            )
    return by_channel


def _rescale(values: np.ndarray, low: float, high: float) -> np.ndarray:
    """Linearly rescale values from the range (low, high) to (0, 1), clipping values outside the range."""
    if high <= low:
        return np.zeros_like(values, dtype=np.float32)
    return np.clip((values - low) / (high - low), 0, 1).astype(np.float32)


def apply_style(
    ds: xr.Dataset,
    style: str,
    percentiles: Optional[Percentiles] = None,
) -> xr.DataArray:
    """Apply a named style to linear backscatter bands, producing an RGBA image.

    Parameters
    ----------
    ds : xr.Dataset
        Bands named `<polarisation>_gamma0` or `<polarisation>_sigma0_ellipsoid` in any case, in linear scale,
        with dimensions `y` and `x`.
        Must also have a `time` dimension for `multitemporal_rgb`. Other styles accept a
        `time` dimension only if it has a length of 1.
    style : str
        The name of a style in `STYLES`
    percentiles : Optional[Percentiles], optional
        Sets the display range from percentiles of the image's valid pixels, rather than the style's fixed range.
        Percentiles are calculated on the values displayed by each channel, e.g. dB for dB styles.
        Use a pair such as `(2, 98)` for all channels, or a dictionary such as `{"red": (2, 98)}`
        to set individual channels, leaving other channels on their fixed range. By default None.
        Note that percentile ranges differ between images, so colours are not comparable between them.

    Returns
    -------
    xr.DataArray
        An RGBA image with dimensions `y`, `x` and `band`, and values between 0 and 1. Pixels with
        missing data are transparent. The display ranges used are stored in `attrs["scale_ranges"]`.

    Raises
    ------
    ValueError
        the style is unknown, the bands or dimensions don't suit the style, or the percentiles are invalid or
        are requested for an image with no valid pixels
    """
    if style not in STYLES:
        raise ValueError(f"Unknown style '{style}'. Choose from: {list(STYLES)}")
    selected_style = STYLES[style]

    # Compute the bands once up front, so lazy data isn't reloaded for each channel
    ds = xr.Dataset({band.name: band for band in _backscatter_bands(ds).values()}).compute()
    if "time" in ds.dims and not selected_style.uses_time:
        if ds.sizes["time"] > 1:
            raise ValueError(
                f"Style '{style}' needs a single image, but the dataset has {ds.sizes['time']} time steps. "
                "Select one time step or create a composite first."
            )
        ds = ds.squeeze("time", drop=True)

    channels = selected_style.channels(ds)
    channels = {
        channel: values.transpose("y", "x") for channel, values in channels.items()
    }
    percentiles_by_channel = _percentiles_by_channel(percentiles, channels)

    template = next(iter(channels.values()))
    is_valid = np.ones(template.shape, dtype=bool)
    for values in channels.values():
        is_valid &= np.isfinite(values.values)

    scale_ranges = {}
    scaled = {}
    for channel, values in channels.items():
        if channel in percentiles_by_channel:
            if not is_valid.any():
                raise ValueError("Cannot calculate percentiles: image has no valid pixels")
            low, high = np.percentile(
                values.values[is_valid], percentiles_by_channel[channel]
            )
        else:
            low, high = selected_style.scale_ranges[channel]
        scale_ranges[channel] = (float(low), float(high))
        scaled[channel] = np.nan_to_num(_rescale(values.values, low, high), nan=0.0)

    if selected_style.cmap is not None:
        # bytes=True keeps memory use low for large images
        rgb = selected_style.cmap(scaled["value"], bytes=True)[..., :3] / 255
        rgb = rgb.astype(np.float32)
    else:
        rgb = np.stack([scaled[channel] for channel in ("red", "green", "blue")], axis=-1)

    rgba = np.concatenate(
        [rgb, is_valid[..., np.newaxis].astype(np.float32)], axis=-1
    )
    # Hide colour under transparent pixels, which keeps the saved image clean
    rgba[~is_valid] = 0

    return xr.DataArray(
        rgba,
        dims=("y", "x", "band"),
        coords={**template.coords, "band": ["red", "green", "blue", "alpha"]},
        attrs={"style": style, "scale_ranges": scale_ranges},
    )


def save_image(rgba: xr.DataArray, path: Union[str, Path]) -> Path:
    """Save an RGBA image from `apply_style` as a PNG, with one image pixel per array cell.

    Parameters
    ----------
    rgba : xr.DataArray
        The image to save, with dimensions `y`, `x` and `band`
    path : Union[str, Path]
        The file to write. Missing parent folders will be created.

    Returns
    -------
    Path
        The path of the saved file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # The first row of the image needs to be the northernmost row
    image = rgba.sortby("y", ascending=False).transpose("y", "x", "band")
    plt.imsave(path, image.values)
    return path
