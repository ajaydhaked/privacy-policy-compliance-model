import os
import sys
import json
from src.utils import log, read_file, read_json
from src.rulesEvaluator import RulesEvaluator
from src.createAllAccessRequests import CreateAllAccessRequest
from src.violationAnalyzer import ViolationAnalyzer
from src.tee import Tee
import time

ALL_ATTRIBUTES_FILE_PATH = "all_attributes_list.json"
ATTRIBUTE_INFERENCE_PROMPT_TEMPLATE_PATH = "prompts/attribute_inference_llm_prompt.txt"
PRIVACY_POLICY_FOLDER = "privacy_policies"
INFERRED_VALUES_FOLDER = "inferred_values"
GROUND_TRUTH_FOLDER = "ground_truths"
LOGS_FOLDER = "logs"

if not os.path.exists(LOGS_FOLDER):
    os.makedirs(LOGS_FOLDER)

if not os.path.exists(INFERRED_VALUES_FOLDER):
    os.makedirs(INFERRED_VALUES_FOLDER)




def save_inferred_values(inferred_attributes, company_name):
    file_path = os.path.join(INFERRED_VALUES_FOLDER, company_name + ".json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(inferred_attributes, f, indent=2)

def main():
    stdout_capture_file = f"{LOGS_FOLDER}/stdout_capture_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    tee = Tee(stdout_capture_file)
    sys.stdout = tee
    print(f"Stdout also being saved to: {stdout_capture_file}\n")
    try:
        _run()
    finally:
        sys.stdout = tee._terminal
        tee.close()


def _run():
    all_attributes = read_json(ALL_ATTRIBUTES_FILE_PATH)
    attribute_inference_prompt_template = read_file(ATTRIBUTE_INFERENCE_PROMPT_TEMPLATE_PATH)
    create_all_access_request = CreateAllAccessRequest(all_attributes, attribute_inference_prompt_template)
    rules_evaluator = RulesEvaluator()
    violation_analyzer = ViolationAnalyzer()

    privacy_policies = sorted(os.listdir(PRIVACY_POLICY_FOLDER))
    total_policies   = len(privacy_policies)

    print("\n" + "=" * 70)
    print(f"   DPDP ACT COMPLIANCE EVALUATION  —  {total_policies} policies found")
    print("=" * 70 + "\n")

    policy_summary = []   

    for pol_idx, privacy_policy_file in enumerate(privacy_policies, start=1):
        company_name        = privacy_policy_file.split(".")[0]
        privacy_policy_path = os.path.join(PRIVACY_POLICY_FOLDER, privacy_policy_file)
        privacy_policy_text = read_file(privacy_policy_path)
        log_file_name       = (
            LOGS_FOLDER + "/" + company_name
            + "_log_" + time.strftime('%Y%m%d_%H%M%S') + ".txt"
        )

        print(f"[{pol_idx}/{total_policies}] Evaluating: {company_name}")
        print("-" * 50)

        all_access_requests = create_all_access_request.form_all_access_request_for_privacy_policy(
            privacy_policy_text,
            log_file_path=log_file_name
        )
        save_inferred_values(create_all_access_request.last_inferred_values, company_name)

        # # all_access_requests = create_all_access_request.form_all_access_request_for_privacy_policy_from_inferred_attributes(
        # #     file_path=f"{INFERRED_VALUES_FOLDER}/{company_name}.json"
        # # )

        # all_access_requests = create_all_access_request.form_all_access_request_for_privacy_policy_from_ground_truth(
        #     file_path=f"{GROUND_TRUTH_FOLDER}/{company_name}.json"
        # )


        total_requests     = len(all_access_requests)
        compliant_requests = 0

        for req_idx, access_request in enumerate(all_access_requests, start=1):
            log(json.dumps(access_request.get_attributes(), indent=2),
                heading="CHECKING BELOW ACCESS_REQUEST", file_path=log_file_name)

            rules_evaluator.evaluate_all_rules(access_request)

            log(rules_evaluator.evaluation_logs,
                heading="EVALUATION LOGS", file_path=log_file_name)

            allowed = access_request.get("allow_data_processing") == "true"

            if allowed:
                compliant_requests += 1



        policy_compliant = compliant_requests > 0

        policy_summary.append({
            "name"              : company_name,
            "compliant"         : policy_compliant,
        })  

        if not policy_compliant:
            violations = violation_analyzer.get_violations(access_request)
            formatted_violations = violation_analyzer.format_violations(violations)
            log(json.dumps(violations, indent=2), heading="VIOLATIONS", file_path=log_file_name)
            log(formatted_violations, heading="FORMATTED VIOLATIONS", file_path=log_file_name)
            print("Violations Found")
            print(formatted_violations)
        else:
            log("DATA PROCESSING IS ALLOWED",
                heading="DATA PROCESSING ALLOWED", file_path=log_file_name)
            print("Data Processing is Allowed")
        verdict_icon  = "✅ COMPLIANT" if policy_compliant else "❌ NON-COMPLIANT"
        print(f"\n   Result  : {verdict_icon}")
        print()


    compliant_policies     = [p for p in policy_summary if p["compliant"]]
    non_compliant_policies = [p for p in policy_summary if not p["compliant"]]

    print("\n" + "=" * 70)
    print("                        FINAL COMPLIANCE SUMMARY")
    print("=" * 70)
    print(f"  Total policies evaluated  : {total_policies}")
    print(f"  ✅ Compliant              : {len(compliant_policies)}")
    print(f"  ❌ Non-Compliant          : {len(non_compliant_policies)}")
    print()

    if compliant_policies:
        print("  ── Compliant Policies ──────────────────────────────────────────────")
        for p in compliant_policies:
            print(f"   ✅  {p['name']}")

    if non_compliant_policies:
        print()
        print("  ── Non-Compliant Policies ──────────────────────────────────────────")
        for p in non_compliant_policies:
            print(f"   ❌  {p['name']}")

    print()
    print(f"  {len(compliant_policies)} out of {total_policies} privacy policies are COMPLIANT with the DPDP Act.")
    print("=" * 70 + "\n")

main()