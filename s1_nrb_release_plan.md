# Sentinel-1 NRB release: notebooks and dea-tools plan

**Goal:** when the product is released, users can load, convert, filter and display NRB with tested `dea-tools` functions. A small set of notebooks shows the workflow and real uses.

**Starting point:** this repo (`de-sar-sample-data`), with C0/C1 tutorials, extended examples and the `de_sar_demo` package.

## 1. dea-tools functions (proposed `dea_tools.sar` module)

| Priority | Function | Source in `de_sar_demo` | Work needed |
| --- | --- | --- | --- |
| P1 | `load_nrb(items, convention=...)`: loads in gamma0, DEM sigma0, ellipsoid sigma0 or beta0, and warns for gamma0 south of 60°S | `loading.py` | Agree the API; add datacube (`dc.load`) support as well as STAC |
| P1 | `convert_backscatter(ds, convention)` | `sar_utils.py` | Tests |
| P1 | `to_db` / `from_db` | `sar_utils.convert_linear_to_db_xr` | Add inverse; handle zeros/NaN; keep attrs |
| P1 | Layover and shadow mask decode and dilation | `masking.dilate_mask` | Dilate by metres, not pixels; decode flag values |
| P2 | Speckle filters: Lee (have), refined/enhanced Lee, Frost, boxcar, multitemporal (Quegan) | `speckle_filters.lee_filter_xr` | Make dask-friendly (`map_overlap`); linear scale only; tests on edges and NaN |
| P2 | Pass-aware compositing (group by absolute orbit or solar day; linear mean or median) | Hero images notebook | Turn into a function |
| P2 | Display styles and image export (`ice_blue`, VV+VH false colour, dual-pol, multitemporal RGB) | `visualisation.py` | Check fit with existing `dea_tools.plotting` |
| P3 | Coverage summary per month | `coverage.summarise_coverage_monthly` | Optional |
| P1 | `search_scenes(stac_client, scene_ids)`: find all bursts for one or more SLC scene IDs | `loading.find_and_load_single_scene_from_stac` | Get the collection (`1SSH`→HH, `1SDH`→HH+HV, `1SSV`→VV, `1SDV`→VV+VH) and the time range from the scene name, so `asf_search` isn't needed; use a CQL2 `in` filter on `sarard:scene_id`; report scene IDs with no bursts |
| P1 | `load_scenes(stac_client, scene_ids, convention=..., ...)`: one time step per scene | Same | Wraps `search_scenes` + `load_nrb` with `groupby="sarard:scene_id"`; optional GeoTIFF/COG export per scene |

**Standards for everything moved:** docstrings, unit tests, lazy (dask) support, standard band names (`<pol>_<convention>`), and no hard-coded dev URLs.

## 2. Release notebooks (DEA notebooks repo)

| Notebook | Built from | Notes |
| --- | --- | --- |
| Product introduction (collections, bands, conversion layers, coverage) | `tutorial_c1/01_product_info`, `02_demonstration` | Beginner |
| Loading data (STAC and datacube) | `tutorial_c1/03`, `04` | Switch to `load_nrb` |
| Loading known scenes by scene ID | `dataloading_known_scenes` | Uses `search_scenes` / `load_scenes` |
| Backscatter conventions and Antarctic DEM artifacts | `visualisation_compare_backscatter_conventions` | Key for Antarctic users |
| Post-processing: dB, speckle filters, layover and shadow masking | `tutorial_c1/05_post_processing` | Compare filters side by side |
| Visualisation and high-quality images | `visualisation_s1_hero_images` | Uses the styles functions |
| Applications: ice fronts (Pine Island, Denman), fire (Kangaroo Island), agriculture (Moree), SAR + optical time series | `s1_nrb_denman_glacier`, hero locations, `visualisation_sar_optical_timeseries_animation` | Pick 2–3 for release |

**Not for release:** `compare_static_layer_artifacts`, `compare_ew_isce3_ew_gamma` (internal QA), and the C0 tutorials.

## 3. Product and docs

- **Product docs page:** explain the conventions, the conversion layers and the Antarctic DEM artifact issue, and recommend ellipsoid sigma0 over ice.
- **Web map (OWS) style for Antarctica:** show ellipsoid sigma0 using band math on the conversion layers.
- **Release clean-up:** switch dev to production STAC/explorer URLs and final collection names, pin the environment, and update the README.

## 4. Decisions for the meeting

1. Should the default convention stay gamma0 with an Antarctic warning, or be ellipsoid sigma0 in Antarctica?
2. Should the functions go in one `dea_tools.sar` module, or be spread across existing modules?
3. Which speckle filters ship at release, and which come later?
4. Which application notebooks ship at release?
5. Who owns each item, and what are the target dates?
