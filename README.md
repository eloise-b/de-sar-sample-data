# Accessing Geoscience Australia's Sentinel-1 IW Backscatter (collection 0)

This repository demonstrates how to use Python to access preliminary Sentinel-1 Interferometric Wide (IW) mode backscatter products developed by Geoscience Australia. 

For Sentinel-1, Geoscience Australia's Digital Earth (DE) branch are currently offering a suite of experimental products that we are calling **collection 0**, with sample data available over parts of Australia and Antarctica.
The product is a collaborative effort from Digital Earth Australia and Digital Earth Antarctica.

## Data availability

Geoscience Australia's Sentinel-1 data is published across multiple products, one for each polarisation mode used to capture the data.
You can see the distribution of captured data over time and space in the DEA Dev Explorer:
* [VV+VH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_vv_vh_0)
* [VV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_vv_0)
* [HH distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_hh_0)
* [HH+HV distribution](https://explorer.dev.dea.ga.gov.au/products/ga_s1_nrb_iw_hh_hv_0)

## Documentation

This repository provides examples for how to load data in two ways:
* Using DE's STAC API, which can be run on any computer.
* Using DE's development Open Data Cube, which is only available in DE's Development or Production Sandbox environment. 

If you are not a Geoscience Australia employee, you will need to use the STAC API approach.

We provide two options for documentation
* [Rendered html pages](demo_html_pages), which can be viewed in a browser. 
This shows you the outcome of each step required to load and transform the data.
* [iPython notebooks](demo_notebooks), which can be run in an appropriate environment.

To view either file, you will first need to [clone the repository](#cloning-the-repository) to get a copy of the files.

## Set up

### Cloning the repository
To access and run the iPython notebooks, you will need to clone this repository into your local computing environment, or the DE Dev Sandbox. 

In a terminal, navigate to where you wish to keep the repository and run
```
git clone https://github.com/caitlinadams/de-sar-sample-data.git
```

### Setting up the environment

If using DE's Dev Sandbox, no environment set up is required.

If using your own computer to run the STAC API notebook, you will need a Python environment with the required packages. 
Two different environment files are provided:
* A Conda [environment.yaml](environment.yaml) file
    * [Install conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#installing-conda)
    * [Install the environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)
    * [Activate the environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment)
* A Pixi [pyproject.toml](pyproject.toml) file
    * [Install pixi](https://pixi.sh/dev/installation/)
    * [Install the environment](https://pixi.sh/dev/python/tutorial/#installation-pixi-install)
    * [Activate the environment](https://pixi.sh/dev/workspace/environment/#activation)

You can also choose to manually install the following required packages using your package manager of choice:
* ipykernel
* odc-stac
* pystac-client
* numpy
* folium
* botocore
* matplotlib
* scipy