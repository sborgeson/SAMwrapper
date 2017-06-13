# Copyright 2017, Sam Borgeson.
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Direct inquiries to Sam Borgeson (sam@convergenceda.com)

import os
from SAMwrapper import SAMEngine

if __name__ == '__main__':

    model_params = {
        "wind_resource_filename" : 'CA Northern-Rolling Hills.srw',
        'wind_resource_shear' : 0.14,
        'wind_resource_turbulence_coeff' : 0.1,
        'system_capacity' : 100, # in kW
        'wind_resource_model_choice' : 0, # Hourly=0 or Weibull=1 model
        'wind_turbine_rotor_diameter' : 10, # in m
        'wind_turbine_powercurve_windspeeds' : [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                                 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                                                 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
                                                 35, 36, 37, 38, 39, 40 ],
        'wind_turbine_powercurve_powerout':   [0, 0, 0, 0, 3.7000000476837158, 10.5, 19, 29.399999618530273, 41,
                                               54.299999237060547, 66.800003051757813, 77.699996948242188,
                                               86.400001525878906, 92.800003051757813, 97.300003051757813,
                                               100, 100.80000305175781, 100.59999847412109, 99.800003051757813,
                                               99.400001525878906, 98.599998474121094, 97.800003051757813,
                                               97.300003051757813, 97.300003051757813, 98, 99.699996948242188,
                                               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'wind_turbine_hub_ht': 25,
        'wind_turbine_max_cp': 0.37,
        # 3 turbines laid out in a row from east to west
        'wind_farm_xCoordinates': [0, 168, 336],
        'wind_farm_yCoordinates': [0, 0, 0],
        'wind_farm_losses_percent': 0,
        'wind_farm_wake_model': 0, # Simple=0, Park (WAsP)=1, Eddy-Viscosity=2
        'adjust:constant': 0,

    }

    cols_of_interest = [
        'wind_speed', #[4.879, 3.347 + 8758 more.]
        'wind_direction', #[9.000, 346.000 + 8758
        'temp', #[9.490, 7.740 + 8758
        'pressure',
        'gen' # in kw
    ]

    # initialize the SAM system, which includes loading the underlying ssc shared library
    sam = SAMEngine(debug=True)

    # perform the modeling run
    results = sam.run_module(module_name='windpower', model_params=model_params)

    # print out the details of the model results
    print(sam.summarize(results))

    # extract an [8760 x n] DataFrame of hourly simulation output values
    resultsdf = sam.results_to_pandas(results,cols_of_interest)

    # a look at the structure of the data
    print(resultsdf.head(5))
    print(resultsdf.tail(5))