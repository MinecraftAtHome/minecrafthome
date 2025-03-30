#!/usr/bin/env python
from assimilator import *
from Boinc import boinc_project_path
import re, os

class MCAtHAssimilator(Assimilator):
        def __init__(self):
                Assimilator.__init__(self)

        def assimilate_handler(self, wu, results, canonical_result):
                try:
                    if canonical_result == None:
                            return

                    path = boinc_project_path.project_path("xoroshigo_results")
                    input_path = self.get_file_path(canonical_result)

                    with open(input_path) as input_file:
                        input_str = input_file.read()

                    try:
                        os.makedirs(path)
                    except OSError:
                        pass

                    lines = list()
                    input_lines = input_str.splitlines()
                    config_filename = input_lines[2].split(' ')[0]
                    config_name = config_filename[0:len(config_filename)-4]
                    results_filename = config_name + "-results.txt"
                    with open(os.path.join(path, results_filename), "a") as f:
                        for line in input_str.splitlines():
                            lines.add(line)
                        for line in lines:
                            f.write("{}\n".format(line))
                except Exception as e: print(e)

if __name__ == "__main__":
        asm = MCAtHAssimilator()
        asm.run()