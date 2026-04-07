# Model Execution

This directory contains the necessary code and data for the privacy policy compliance model.

## How to Run

To run experiments and evaluate the model's performance, follow these steps:

1. **Run the model on Privacy policies**: 
   ```bash
   python run_model_on_privacy_policies.py
   ```
   Running this script extracts and generates all inferences for the privacy policies, stores them in the `inferred_values` folder, and evaluates all rules to check whether data processing is allowed or not.

2. **Run the Experiments**:
   ```bash
   python run_experiments.py
   ```
   This script compares the LLM outputs in `inferred_values` against the manually curated `ground_truths`. It provides the following analysis:
   - **Ground Truth Analytics**: A breakdown of `true`, `false`, and `unknown` values per attribute and per company.
   - **Performance Evaluation**: Confusion Matrix (True Positives, True Negatives, False Positives, False Negatives), Accuracy, Precision, and Recall metrics evaluated overall, per privacy policy, and per individual attribute.

## Directory Structure

- **`inferred_values/`**: Contains all the inferences of normal attributes from llm.
- **`logs/`**: Used for storing execution logs.
- **`privacy_policies/`**: Contains the extracted raw text for each privacy policy.
- **`prompts/`**: Contains the prompts used in our experiments.
- **`ground_truths/`**: Contains manually curated ground truths for each privacy policy, which are used as a reference point.
