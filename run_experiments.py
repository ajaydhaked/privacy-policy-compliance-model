import os
import json
import time
import sys
from collections import defaultdict
from src.tee import Tee

EXPERIMENTS_DIR = "experiments"
GT_DIR = "ground_truths"
INF_DIR = "inferred_values"

def create_confusion_matrix():
    return {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}

def get_metrics(cm):
    tp, tn, fp, fn = cm['TP'], cm['TN'], cm['FP'], cm['FN']
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return accuracy, precision, recall, total


def is_negative(val):
    return str(val).lower() in ['false', 'unknown', 'none']

def determine_result(gt_val, inf_val):
    gt_neg = is_negative(gt_val)
    inf_neg = is_negative(inf_val)
    
    if gt_neg and inf_neg:
        return 'TN'
    elif not gt_neg and not inf_neg:
        if str(gt_val).lower() == str(inf_val).lower():
            return 'TP'
        else:
            return 'FN'
    elif not gt_neg and inf_neg:
        return 'FN'
    elif gt_neg and not inf_neg:
        return 'FP'

def main():
    gt_dir = GT_DIR
    inf_dir = INF_DIR
    
    if not os.path.exists(gt_dir) or not os.path.exists(inf_dir):
        print(f"Error: Make sure both '{gt_dir}' and '{inf_dir}' directories exist.")
        return

    # Experiment 1: Analysis of ground truths
    attr_policy_map = defaultdict(lambda: defaultdict(list))
    policy_counts = defaultdict(lambda: {'true': 0, 'false': 0, 'unknown': 0})
    policies_list = []
    
    for filename in os.listdir(gt_dir):
        if not filename.endswith('.json'): continue
        policy_name = filename.replace('.json', '')
        policies_list.append(policy_name)
        with open(os.path.join(gt_dir, filename), 'r') as f:
            try:
                data = json.load(f)
                for item in data:
                    attr = item.get('attribute_name')
                    val = str(item.get('value', 'unknown')).lower()
                    if val not in ['true', 'false']:
                        val = 'unknown'
                    
                    attr_policy_map[attr][val].append(policy_name)
                    policy_counts[policy_name][val] += 1
            except json.JSONDecodeError:
                pass
                
    print(f"Loaded {len(policies_list)} policies.")
    print("\n" + "="*80)
    print("GROUND TRUTH ANALYSIS - Per-Attribute Breakdown (true / false / unknown) with Policy Lists")
    print("="*80)
    
    for attr, vals in attr_policy_map.items():
        print(f"\nAttribute : {attr}")
        for val in ['true', 'false', 'unknown']:
            policies_for_val = sorted(vals[val])
            count = len(policies_for_val)
            policies_str = ", ".join(policies_for_val) if count > 0 else "---"
            print(f"  {val.capitalize():<7} ({count:2d}) : {policies_str}")

    print("\n" + "="*80)
    print("ANALYTICS 2 - Per-Company Analysis (true / false / unknown)")
    print("="*80)
    print(f"{'Policy'.ljust(20)} {'True':>6} {'False':>6} {'Unknown':>7}")
    print("-" * 43)
    for policy in sorted(policy_counts.keys()):
        counts = policy_counts[policy]
        t, f_c, u = counts['true'], counts['false'], counts['unknown']
        print(f"{policy.ljust(20)} {t:6d} {f_c:6d} {u:7d}")

    # Experiment 2: Performance Evaluation
    print("\n" + "="*80)
    print("PERFORMANCE EVALUATION WITH GROUND TRUTHS - (TP, TN, FP, FN)")
    print("="*80)
    
    overall_cm = create_confusion_matrix()
    policy_cm = defaultdict(create_confusion_matrix)
    attr_cm = defaultdict(create_confusion_matrix)
    
    for filename in os.listdir(gt_dir):
        if not filename.endswith('.json'): continue
        policy_name = filename.replace('.json', '')
        
        gt_path = os.path.join(gt_dir, filename)
        inf_path = os.path.join(inf_dir, filename)
        
        if not os.path.exists(inf_path):
            continue
            
        with open(gt_path, 'r') as f:
            gt_data = json.load(f)
        with open(inf_path, 'r') as f:
            inf_data = json.load(f)
            
        # Create mapping of attribute -> value
        gt_map = {item['attribute_name']: str(item.get('value', 'unknown')).lower() for item in gt_data}
        inf_map = {item['attribute_name']: str(item.get('inferred_value', 'unknown')).lower() for item in inf_data}
        
        for attr, gt_val in gt_map.items():
            inf_val = inf_map.get(attr, 'unknown')
            
            res = determine_result(gt_val, inf_val)
            overall_cm[res] += 1
            policy_cm[policy_name][res] += 1
            attr_cm[attr][res] += 1

    # Print Overall Results
    print("\n--- OVERALL METRICS ---")
    acc, prec, rec, total = get_metrics(overall_cm)
    print(f"Total Evaluated: {total}")
    print(f"Confusion Matrix: TP: {overall_cm['TP']} | TN: {overall_cm['TN']} | FP: {overall_cm['FP']} | FN: {overall_cm['FN']}")
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    
    # Print Per Privacy Policy Results
    print("\n--- METRICS PER PRIVACY POLICY ---")
    for policy, cm in sorted(policy_cm.items()):
        acc, prec, rec, _ = get_metrics(cm)
        print(f"[{policy.upper().ljust(20)}] "
              f"Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} "
              f" (TP:{cm['TP']:2d} TN:{cm['TN']:2d} FP:{cm['FP']:2d} FN:{cm['FN']:2d})")
        
    # Print Per Attribute Results
    print("\n--- METRICS PER ATTRIBUTE ---")
    for attr, cm in sorted(attr_cm.items()):
        acc, prec, rec, _ = get_metrics(cm)
        print(f"[{attr}]")
        print(f"    Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} "
              f" (TP:{cm['TP']:2d} TN:{cm['TN']:2d} FP:{cm['FP']:2d} FN:{cm['FN']:2d})")

if __name__ == '__main__':
    stdout_capture_file = f"{EXPERIMENTS_DIR}/results_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    tee = Tee(stdout_capture_file)
    sys.stdout = tee
    print(f"Stdout also being saved to: {stdout_capture_file}\n")
    try:
        main()
    finally:
        sys.stdout = tee._terminal
        tee.close()
