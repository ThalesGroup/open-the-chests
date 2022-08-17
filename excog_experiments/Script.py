# -*- coding: utf8 -*-
"""Standard Excog run script"""

import os
import excog


if __name__ == '__main__':
    os.makedirs("temp", exist_ok=True)
    results = excog.process_plan("config.yaml")
    results.to_csv("temp/results.csv")
    print(results)