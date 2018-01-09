# Copyright 2017, Sam Borgeson.
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Direct inquiries to Sam Borgeson (sam@convergenceda.com)

import os
from SAMwrapper import SAMEngine, LKInterpreter

if __name__ == '__main__':

    sam = SAMEngine(debug=False)
    lki = LKInterpreter('test/lk/untitled.lk', debug=False)
    run_config = lki.sam_vars_to_dict()
    print(run_config.keys())
    results = sam.run_from_config(run_config,output_selector=None)

    print(sam.summarize(results))

