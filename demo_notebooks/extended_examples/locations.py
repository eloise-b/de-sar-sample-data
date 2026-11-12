from dataclasses import dataclass
from typing import Literal, Optional

from odc.geo import BoundingBox

from de_sar_demo.visualisation import Percentiles


@dataclass(frozen=True)
class Location:
    """An area and time to make an image of.

    Parameters
    ----------
    name : str
        A short name, used for the output file name
    description : str
        A brief caption for the image, covering the location, the data and what can be seen
    collection : str
        The collection to load, e.g. `ga_s1_nrb_iw_hh_1`
    aoi : BoundingBox
        The area of interest
    start_date : str
        The start of the time range to search, e.g. `2025-01-01`
    end_date : str
        The end of the time range to search, e.g. `2025-02-01`
    resolution : int
        The pixel size to load, in metres
    percentiles : Optional[Percentiles]
        The recommended percentiles for `apply_style`, for areas that suit a stretch
        better than the style's fixed ranges, by default None
    mask_layover_shadow : bool
        Whether to remove pixels affected by layover and shadow. Turn this off for steep terrain
        where it would leave large holes in the image, by default False
    backscatter : Literal["gamma0", "sigma0_ellipsoid", "sigma0_dem", "beta0"]
        The backscatter convention to display. Ellipsoid sigma0 removes the DEM-based brightness
        correction in gamma0, which can help where DEM errors show in the image. DEM sigma0 is
        relative to the ground including terrain, using the `oa_gamma0_to_sigma0_ratio` layer.
        Beta0 is relative to the radar slant range, using the `oa_gamma0_to_beta0_ratio` layer,
        by default "gamma0"
    """

    name: str
    description: str
    collection: str
    aoi: BoundingBox
    start_date: str
    end_date: str
    resolution: int
    percentiles: Optional[Percentiles] = None
    mask_layover_shadow: bool = False
    backscatter: Literal["gamma0", "sigma0_ellipsoid", "sigma0_dem", "beta0"] = "gamma0"


LOCATIONS = {
    location.name: location
    for location in (
        Location(
            name="pine_island_glacier_front",
            description=(
                "Pine Island Glacier, West Antarctica, in January 2025, from Geoscience Australia's Sentinel-1 radar backscatter (HH ellipsoid sigma0, contains modified Copernicus Sentinel data 2025). "
                "The glacier's bright, crevassed floating ice shelf ends in a sharp calving front, with dark ocean and scattered ice floes beyond."
            ),
            collection="ga_s1_nrb_iw_hh_1",
            aoi=BoundingBox(left=-104.0, bottom=-75.6, right=-98.5, top=-74.5, crs="EPSG:4326"),
            start_date="2025-01-01",
            end_date="2025-02-01",
            resolution=60,
            backscatter="sigma0_ellipsoid",
        ),
        Location(
            name="pine_island_glacier_front_zoom",
            description=(
                "A closer view of the Pine Island Glacier ice front, West Antarctica, in January 2025, from Geoscience Australia's Sentinel-1 radar backscatter (HH ellipsoid sigma0, contains modified Copernicus Sentinel data 2025). "
                "Flow bands and crevasses mark the floating ice shelf, which ends abruptly at the darker ocean and ice floes."
            ),
            collection="ga_s1_nrb_iw_hh_1",
            aoi=BoundingBox(left=-102.5, bottom=-75.3, right=-100.0, top=-74.8, crs="EPSG:4326"),
            start_date="2025-01-01",
            end_date="2025-02-01",
            resolution=20,
            backscatter="sigma0_ellipsoid",
        ),
        Location(
            name="casey_station_vanderford_glacier",
            description=(
                "Casey station and Vanderford Glacier, East Antarctica, on 13 and 15 January 2022, from Geoscience Australia's Sentinel-1 radar backscatter (HH, two passes, contains modified Copernicus Sentinel data 2022). "
                "The crevassed glacier tongue and rocky Windmill Islands stand out against dark Vincennes Bay."
            ),
            collection="ga_s1_nrb_iw_hh_1",
            aoi=BoundingBox(left=109.85, bottom=-67, right=110.7, top=-66.15, crs="EPSG:4326"),
            start_date="2022-01-12",
            end_date="2022-01-15",
            resolution=20,
        ),
        Location(
            name="antarctic_peninsula",
            description=(
                "Crane Glacier and the Larsen B embayment, Antarctic Peninsula, in January 2025, from Geoscience Australia's Sentinel-1 radar backscatter (HH, contains modified Copernicus Sentinel data 2025). "
                "Bright, steep mountains are cut by glaciers that flow east to the darker, ice-covered waters of the embayment."
            ),
            collection="ga_s1_nrb_iw_hh_1",
            aoi=BoundingBox(left=-63.5, bottom=-65.8, right=-61.1, top=-65.1, crs="EPSG:4326"),
            start_date="2025-01-01",
            end_date="2025-02-01",
            resolution=20,
            mask_layover_shadow=False,
        ),
        Location(
            name="erebus_ice_tongue_mcmurdo",
            description=(
                "The Erebus Ice Tongue and McMurdo Station, Ross Island, Antarctica, in January and February 2026, from Geoscience Australia's Sentinel-1 radar backscatter (HH, contains modified Copernicus Sentinel data 2026). "
                "The narrow ice tongue juts from Ross Island into the dark waters of McMurdo Sound, with the volcano Mount Erebus in the rugged terrain behind it. Bright white lines show transit routes from McMurdo Station."
            ),
            collection="ga_s1_nrb_iw_hh_1",
            aoi=BoundingBox(left=166.2, bottom=-77.93, right=167.3, top=-77.5, crs="EPSG:4326"),
            start_date="2026-01-01",
            end_date="2026-03-01",
            resolution=20,
        ),
        Location(
            name="kangaroo_island_after_fire",
            description=(
                "Kangaroo Island, South Australia, in February 2020, weeks after the 2019-20 bushfires, from Geoscience Australia's Sentinel-1 radar backscatter (false colour with enhanced contrast: red VV, green VH, blue VH/VV; contains modified Copernicus Sentinel data 2020). "
                "Compare with the pre-fire image to see changes in the island's bushland, as the fires burned around half of the island, mostly in the west."
            ),
            collection="ga_s1_nrb_iw_vv_vh_1",
            aoi=BoundingBox(
                left=136.4522854909602,
                bottom=-36.14017562416003,
                right=138.16354422308083,
                top=-35.52783587880561,
                crs="EPSG:4326",
            ),
            start_date="2020-01-25",
            end_date="2020-03-01",
            resolution=40,
            percentiles={"red": (2, 99.5), "green": (2, 99.5)},
        ),
        Location(
            name="kangaroo_island_before_fire",
            description=(
                "Kangaroo Island, South Australia, in November and December 2019, before the 2019-20 bushfires, from Geoscience Australia's Sentinel-1 radar backscatter (false colour with enhanced contrast: red VV, green VH, blue VH/VV; contains modified Copernicus Sentinel data 2019). "
                "Colours separate the island's bushland and cleared farmland, set against the dark ocean, as a baseline for the post-fire image."
            ),
            collection="ga_s1_nrb_iw_vv_vh_1",
            aoi=BoundingBox(
                left=136.4522854909602,
                bottom=-36.14017562416003,
                right=138.16354422308083,
                top=-35.52783587880561,
                crs="EPSG:4326",
            ),
            start_date="2019-11-01",
            end_date="2019-12-15",
            resolution=40,
            percentiles={"red": (2, 99.5), "green": (2, 99.5)},
        ),
        Location(
            name="moree_farmland",
            description=(
                "Farmland around Moree, New South Wales, in September and October 2026, from Geoscience Australia's Sentinel-1 radar backscatter (false colour: red VV, green VH, blue VH/VV; contains modified Copernicus Sentinel data 2026). "
                "The patchwork of colours shows differences between fields, which can reflect crop type, growth stage and soil moisture, with the winding river corridor crossing the scene."
            ),
            collection="ga_s1_nrb_iw_vv_vh_1",
            aoi=BoundingBox(left=149.4, bottom=-29.7, right=150.0, top=-29.2, crs="EPSG:4326"),
            start_date="2026-09-01",
            end_date="2026-11-01",
            resolution=20,
        ),
        Location(
            name="lake_eyre",
            description=(
                "Kati Thanda-Lake Eyre, South Australia, in September and October 2026, from Geoscience Australia's Sentinel-1 radar backscatter (false colour with enhanced contrast: red VV, green VH, blue VH/VV; contains modified Copernicus Sentinel data 2026). "
                "The smooth lake basins appear dark, surrounded by pale river channels and textured desert landscapes."
            ),
            collection="ga_s1_nrb_iw_vv_vh_1",
            aoi=BoundingBox(left=136.2, bottom=-30.0, right=138.7, top=-28.0, crs="EPSG:4326"),
            start_date="2026-09-01",
            end_date="2026-11-01",
            resolution=60,
            percentiles=(2, 98),
        ),
        Location(
            name="melbourne",
            description=(
                "Melbourne and Port Phillip Bay, Victoria, in September and October 2026, from Geoscience Australia's Sentinel-1 radar backscatter (false colour: red VV, green VH, blue VH/VV; contains modified Copernicus Sentinel data 2026). "
                "The city's buildings glow yellow and orange, surrounded by green-toned vegetation, while the smooth bay appears dark and ships show as bright points."
            ),
            collection="ga_s1_nrb_iw_vv_vh_1",
            aoi=BoundingBox(left=144.202423, bottom=-38.375039, right=145.316162, top=-37.76, crs="EPSG:4326"),
            start_date="2026-09-20",
            end_date="2026-10-20",
            resolution=20,
        ),
    )
}
