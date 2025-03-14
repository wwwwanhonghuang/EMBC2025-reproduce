import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from scipy.stats import entropy
from tqdm import tqdm
from sklearn.feature_selection import mutual_info_classif
import pandas as pd
import argparse
import itertools

def normalize(values):
    """Normalize a list of values using min-max scaling."""
    min_val = np.min(values)
    max_val = np.max(values)
    return (values - min_val) / (max_val - min_val)

def is_dominated(feature_a, feature_b):
    """Check if feature_a is dominated by feature_b."""
    return all(a >= b for a, b in zip(feature_a, feature_b)) and any(a > b for a, b in zip(feature_a, feature_b))

def find_pareto_optimal_set(results):
    """Find the Pareto optimal set from the integrated results."""
    # Convert to a numpy array for easier manipulation
    features = list(results.keys())
    scores = np.array([results[feature] for feature in features])
    
    # Normalize scores for consistency
    normalized_scores = np.array([normalize(score) for score in scores.T]).T
    
    pareto_set = []
    for i, feature_score in enumerate(normalized_scores):
        # Check if any other feature dominates this one
        if not any(is_dominated(feature_score, other_score) for other_score in normalized_scores if not np.array_equal(feature_score, other_score)):
            pareto_set.append(features[i])
    
    return pareto_set

parser = argparse.ArgumentParser()
parser.add_argument("--kl_comparision_list", type=str, nargs="+", 
    default=["normal", "seizures", "preepileptic"])
parser.add_argument("--mi_evaluation_list", type=str, nargs="+", 
    default=["normal", "seizures", "preepileptic"])

parser.add_argument("--output_folder", type=str, default="./out")
parser.add_argument("--record_base_path", type=str, 
    default="../data/feature_records/0_clean_data")

args = parser.parse_args()
record_base_path = args.record_base_path
output_folder = args.output_folder
mi_evaluation_list = args.mi_evaluation_list
kl_comparision_list = args.kl_comparision_list

if not os.path.exists(record_base_path):
    raise FileNotFoundError(f"Base path '{record_base_path}' does not exist.")

kl_record_files =  np.load(os.path.join(output_folder, 
    f"all_kl_values.npy"), allow_pickle=True).item()

mi_record_files = \
    np.load(os.path.join(output_folder, f"all_kl_values.npy"), allow_pickle=True).item()


common_feature_names = set(mi_record_files.keys()) 
common_feature_names &= set(kl_record_files.keys())
    
print(f'Features Names = {common_feature_names}.')

integrared_result = {

}

for feature_name in common_feature_names:
    integrared_result[feature_name] = {}
    values = []
    for category in mi_record_files[feature_name]:
        values.append(-np.array(mi_record_files[feature_name][category]).mean()) # for mutual information, bigger the better. However, KL distance is on the contraty. To maintain consistancy, we use negative mutual information.
    for category in kl_record_files[feature_name]:
        values.append(np.array(kl_record_files[feature_name][category]).mean())
    integrared_result[feature_name] = np.array(values)

pareto_optimal_features = find_pareto_optimal_set(integrared_result)
print(f"Pareto Optimal Features (Count: {len(pareto_optimal_features)}): {pareto_optimal_features}")
np.save(os.path.join(output_folder, "pareto_optimal_features.npy"), pareto_optimal_features, allow_pickle=True)
