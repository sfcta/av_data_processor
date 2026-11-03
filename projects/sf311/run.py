import sys, argparse, tomllib
import numpy as np
import pandas as pd
from pathlib import Path
from data_models.sf311.reports import Cases

def read_and_validate(config):
    pass

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Process TOML configuration file for validation.")
    parser.add_argument("config_path", type=str, help="Path to the TOML configuration file.")
    
    # Check if the script is running in an interactive environment or not
    if len(sys.argv) > 1:
        # Running from command line, use the provided argument
        args = parser.parse_args()
        
        # Load the TOML configuration file
        with open(args.config_path, 'rb') as f:
            config = tomllib.load(f)['nhtsa']
    else:
        print("Please supply a config file.")
        sys.exit()

    df = read_and_validate(config, write_mapping_files=True)

    print('Done.')