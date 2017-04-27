# Copyright 2017, Sam Borgeson.
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Direct inquiries to Sam Borgeson (sam@convergenceda.com)

from SAMpy import SAMEngine

if __name__ == '__main__':

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
        "solar_resource_file": 'Australia AUS Melbourne (INTL).csv'
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