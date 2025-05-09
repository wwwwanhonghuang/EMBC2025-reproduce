import numpy as np
import os, sys
from tqdm import tqdm
import re
import pandas as pd
import argparse
import yaml

def parse_file(file_path):
    """
    Parses a file with fixed and variable key-value pairs into a dictionary and optionally a DataFrame.

    Args:
        file_path (str): The path to the file to be parsed.

    Returns:
        dict: A dictionary containing the parsed data.
        pd.DataFrame: A DataFrame representation of the parsed data.
    """
    parsed_data = {}

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":")
                if value.lower() == "nan":
                        parsed_data[key.strip()] = np.nan
                else:
                    # Try converting the value to float, if it fails, set it as NaN
                    try:
                        parsed_data[key.strip()] = float(value)
                    except ValueError:
                        parsed_data[key.strip()] = np.nan

    df = pd.DataFrame(parsed_data.items(), columns=["Key", "Value"])
    return df


parser = argparse.ArgumentParser()
parser.add_argument("--configuration_file_path", type=str, default="dataframe_generation_configuration.yaml")
args = parser.parse_args()
configuration_path = args.configuration_file_path
with open(configuration_path, "r") as file:
    configuration = yaml.safe_load(file)

base_path = configuration["base_path"]
print(f"Base Path: {base_path}")


report_base_path = {
}

dataset_info = configuration["dataset"]

for item in dataset_info:
    print(f"Name: {item['name']}, Path: {item['path']}")
    report_base_path[item['name']] = os.path.join(base_path, item['path'])

def integrate_and_save_dataframe_data(reports, save_path="/data1/"):
    dataframes = reports
    combined_dataframe = pd.concat(dataframes)
    combined_dataframe.to_csv(save_path, index=False)

reports = []

for area_type in report_base_path:
    filenames = os.listdir(report_base_path[area_type])
    reports = []
    part = 0
    for index, filename in tqdm(enumerate(filenames), desc=f"Processing {area_type}", total=len(filenames)):
        df = parse_file(os.path.join(report_base_path[area_type], filename))
        match = re.match(r"sentence_([0-9]+)\.report", filename)
        df['id'] = match.group(1)
        reports.append(df)
        if(len(reports) > 500000):
            integrate_and_save_dataframe_data(reports, f"/data1/{area_type}_data.{part + 1}.csv")
            part += 1
            reports = []
        
    if len(reports) > 0:
        if part == 0:
            integrate_and_save_dataframe_data(reports, f"/data1/{area_type}_data.csv")
        else:
            integrate_and_save_dataframe_data(reports, f"/data1/{area_type}_data.{part + 1}.csv")
            
