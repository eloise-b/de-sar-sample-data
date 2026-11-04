from collections import defaultdict

import numpy as np
from odc.geo import BoundingBox
import pandas as pd
from pystac_client import Client
import shapely


def summarise_coverage_monthly(
    stac_client: Client,
    collection: str,
    aoi: BoundingBox,
    start_month: str,
    end_month: str,
    grid_size: int = 100,
) -> pd.DataFrame:
    """Summarise how well a collection covers an area of interest in each calendar month.

    This compares item footprints with a grid of points across the area, so it's quick because no
    data is loaded. Footprints can overstate the pixels with data, so `min_passes` in particular is
    only a guide. Each absolute orbit is counted as a pass.

    Parameters
    ----------
    stac_client : Client
        The STAC client used by pystac-client
    collection : str
        The collection to search, e.g. `ga_s1_nrb_iw_hh_1`
    aoi : BoundingBox
        The area of interest
    start_month : str
        The first month to summarise, e.g. `2025-01`
    end_month : str
        The last month to summarise, inclusive, e.g. `2026-10`
    grid_size : int
        The number of points to check along each side of the area, by default 100

    Returns
    -------
    pd.DataFrame
        One row per month, including months without data, with the columns:
        `passes`: the number of passes that touch the area,
        `coverage_percent`: the percentage of the area covered by at least one pass,
        `min_passes` and `median_passes`: the number of passes over each point in the area,
        `best_pass_percent`: the percentage of the area covered by the most complete single pass
    """
    aoi = aoi.polygon.to_crs("EPSG:4326").boundingbox
    x_step = (aoi.right - aoi.left) / grid_size
    y_step = (aoi.top - aoi.bottom) / grid_size
    x, y = np.meshgrid(
        aoi.left + x_step * (np.arange(grid_size) + 0.5),
        aoi.bottom + y_step * (np.arange(grid_size) + 0.5),
    )

    items = stac_client.search(
        collections=[collection],
        datetime=f"{start_month}/{end_month}",
        intersects=shapely.box(aoi.left, aoi.bottom, aoi.right, aoi.top),
    ).item_collection()

    footprints = defaultdict(lambda: defaultdict(list))
    for item in items:
        month = item.datetime.strftime("%Y-%m")
        orbit = item.properties["sat:absolute_orbit"]
        footprints[month][orbit].append(shapely.geometry.shape(item.geometry))

    rows = []
    for period in pd.period_range(start_month, end_month, freq="M"):
        month = str(period)
        covered = [
            shapely.contains_xy(shapely.union_all(shapes), x, y)
            for shapes in footprints[month].values()
        ]
        counts = np.sum(covered, axis=0) if covered else np.zeros_like(x, dtype=int)
        rows.append(
            {
                "month": month,
                "passes": len(covered),
                "coverage_percent": round(100 * float(np.mean(counts > 0)), 1),
                "min_passes": int(counts.min()),
                "median_passes": float(np.median(counts)),
                "best_pass_percent": round(100 * max((float(c.mean()) for c in covered), default=0.0), 1),
            }
        )

    return pd.DataFrame(rows).set_index("month")
