# SAMwrapper
A high level python 2.x and 3.x wrapper around NREL's official SAM (System Advisory Model) SDK, which is low level, not
very pythonic, and doesn't support python 3. SAM is simulation system for distributed energy projects, with the ability
to configure and simulate PV, batteries, and other DER systems. This package provides a pythonic wrapper around their
bare bones SDK.

# External software requirements
* Requires and wraps around the SAM SDK, which you can download and extract from: https://sam.nrel.gov/node/69515 (the path to the SDK is a SAMwrapper config option).
* Uses resource from the SAM GUI tool, which you can download and install from: https://sam.nrel.gov/download

# Compatability
While it is expected to work with a range of versions, testing of this module currently covers SAM 2017.1.17 and SAM SDK 2017.1.17.r1.

# Example usage

Install from github
```sh
pip install --upgrade git+https://github.com/sborgeson/SAMwrapper
```
Install from source (after cloning this repository)
```
python setup.py install
```
Run a simple PV Watts simulation example
```sh
python pvwatts_example.py
```
Which executes the following code

```python
from SAMwrapper import SAMEngine

model_params = {
    'system_capacity': 4,
    'module_type': 0,
    'dc_ac_ratio': 1.1,
    'inv_eff': 96,
    'losses': 14.0757,
    'array_type': 0,
    'tilt': 10,
    'azimuth': 180,
    'gcr': 0.4,
    'adjust:constant': 0,
    "solar_resource_file": 'USA CA Oakland Metropolitan Arpt (TMY3).csv'
}

cols_of_interest = [
    'tamb',  #15.699999809265137, 16.299999237060547] + 8758
    'aoi',  #0.0, 0.0] + 8758
    'shad_beam_factor',  #1.0, 1.0] + 8758
    'sunup',  #0.0, 0.0] + 8758
    'gh',  #nan, nan] + 8758
    'dn',  #0.0, 0.0] + 8758
    'tcell',  #15.699999809265137, 16.299999237060547] + 8758
    'df',  #0.0, 0.0] + 8758
    'wspd',  #1.5, 0.0] + 8758
    'poa',  #0.0, 0.0] + 8758
    'tpoa',  #0.0, 0.0] + 8758
    'dc',  #0.0, 0.0] + 8758
    'ac',  #0.0, 0.0] + 8758
    'gen'  #0.0, 0.0] + 8758
]

# initialize the SAM system, which includes loading the underlying ssc shared library
sam = SAMEngine(debug=True)

# perform the modeling run
results = sam.run_pvwatts(model_params=model_params)

# print out the details of the model results
print(sam.summarize(results))

# extract an [8760 x n] DataFrame of hourly simulation output values
resultsdf = sam.results_to_pandas(results,cols_of_interest)

# a look at the structure of the data
print(resultsdf.head(5))
```
