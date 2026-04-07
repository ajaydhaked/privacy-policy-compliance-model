import os
import json
import itertools
from src.utils import read_file, read_json, write_json_file, log
from src.inferAttributesLLM import InferAttributesLLM
from src.attributeValidator import AttributeValidator
from src.accessRequest import AccessRequest
from src.llm import llm


class CreateAllAccessRequest:
    def __init__(self, all_attributes:list, atttribute_inference_prompt_template:str):
        self.llm_instance = llm()
        self.attribute_validator = AttributeValidator(
            {val["attribute_name"]: val["values"] for val in all_attributes}
        )
        self.infer_attributes_llm = InferAttributesLLM()
        self.all_attributes = all_attributes
        self.unkonwn_attributes = [val for val in all_attributes if val["attribute_type"] == "unknown"]
        self.normal_attributes = [val for val in all_attributes if val["attribute_type"] == "normal"]
        self.dependent_attributes = [val for val in all_attributes if val["attribute_type"] == "dependent"]
        self.attribute_inference_prompt_template = atttribute_inference_prompt_template
        self.unknown_combinations = self._build_unknown_combinations(self.unkonwn_attributes)
        self.last_inferred_values = None

    def _build_unknown_combinations(self, unknown_attributes: list) -> list[list]:
        """Return a list of [(attr_name, value), ...] combinations for all unknown attributes."""
        combinations = []

        def generate(index, current):
            if index == len(unknown_attributes):
                combinations.append(list(current))
            else:
                for value in unknown_attributes[index]["values"]:
                    current.append((unknown_attributes[index]["attribute_name"], value))
                    generate(index + 1, current)
                    current.pop()

        generate(0, [])
        return combinations

    def _build_consent_given_access_request(self):
        ar = AccessRequest(self.attribute_validator)
        ar.set("consent_action", "true")
        ar.set("consent_withdraw_action", "false")
        ar.set("reasonable_time_elapsed", "false")
        ar.set("consent_for_state_benefits", "false")
        ar.set("available_to_state_and_notified_by_government", "false")
        ar.set("voluntary_data_for_specified_purpose", "false")
        ar.set_description(
            "Consent is given by the data principal for the processing of her personal data."
        )
        return ar

    def _build_consent_withdrawn_access_request(self):
        ar = AccessRequest(self.attribute_validator)
        ar.set("consent_action", "true")
        ar.set("consent_withdraw_action", "true")
        ar.set("reasonable_time_elapsed", "false")
        ar.set("consent_for_state_benefits", "false")
        ar.set("available_to_state_and_notified_by_government", "false")
        ar.set_description(
            "Consent is withdrawn by the data principal for the processing of her personal data."
        )
        return ar

    def _build_consent_withdrawn_reasonable_time_elapsed_access_request(self):
        ar = AccessRequest(self.attribute_validator)
        ar.set("consent_action", "true")
        ar.set("consent_withdraw_action", "true")
        ar.set("reasonable_time_elapsed", "true")
        ar.set("consent_for_state_benefits", "false")
        ar.set("available_to_state_and_notified_by_government", "false")
        ar.set_description(
            "Consent is withdrawn by the data principal for the processing of her personal data and a reasonable time has elapsed since the data principal gave consent for the processing of her personal data."
        )
        return ar

    def _make_fresh_requests(self, unknown_combinations: list) -> list:
        """Instantiate a brand-new AccessRequest per combination (no shared state)."""
        requests = []
        for combo in unknown_combinations:
            ar = AccessRequest(self.attribute_validator)
            for attr_name, attr_value in combo:
                ar.set(attr_name, attr_value)
            requests.append(ar)
        return requests

    def form_all_access_request_for_privacy_policy(self, privacy_policy: str, log_file_path = None):
        inferred_attributes = self.infer_attributes_llm.infer_attributes_from_privacy_policy_text(
            privacy_policy_text=privacy_policy,
            attribute_json_text=json.dumps(self.normal_attributes),
            llm_instance=self.llm_instance,
            attribute_inference_prompt_template=self.attribute_inference_prompt_template,
            attribute_validator=self.attribute_validator,
            log_file_path=log_file_path
        )
        self.last_inferred_values = inferred_attributes

        # Fresh requests every call — no state shared between policies
        fresh_requests = []
        fresh_requests.append(self._build_consent_given_access_request())
        for access_request in fresh_requests:
            for attr in inferred_attributes:
                access_request.set(attr["attribute_name"], attr["inferred_value"])
            for attr in self.dependent_attributes:
                access_request.set(attr["attribute_name"], attr["default"])
        return fresh_requests


        



    


def main():
    privacy_policy_file_paths = []
    if os.path.exists("privacy_policies"):
        for dirpath, _, filenames in os.walk("privacy_policies"):
            for filename in filenames:
                if filename.endswith(".txt"):
                    privacy_policy_file_paths.append(os.path.join(dirpath, filename))
    else:
        print("Directory 'privacy_policies' not found.")
                
    all_attributes = read_json(ATTRIBUTE_LIST_FILE_PATH)
    attribute_inference_prompt_template = read_file(ATTRIBUTE_INFERENCE_PROMPT_TEMPLATE_PATH)

    normal_attributes = []
    unknown_attributes = []
    
    for attr in all_attributes:
        attr_type = attr.get("attribute type", "").strip().lower()
        attr["attribute_name"] = normalize_attribute_name(attr["attribute_name"])
        
        if attr_type == "normal":
            normal_attributes.append(attr)
        elif attr_type == "unknown":
            unknown_attributes.append(attr)
            
    llm_attributes_payload = []
    for attr in normal_attributes:
        llm_attributes_payload.append({
            "attribute_name": attr["attribute_name"],
            "values": attr["values"],
            "description": attr.get("description", "")
        })

    unknown_names = [attr["attribute_name"] for attr in unknown_attributes]
    unknown_value_lists = [attr["values"] for attr in unknown_attributes]
    
    # Generate all possible combinations
    unknown_combinations = list(itertools.product(*unknown_value_lists))
    print(f"Number of 'unknown' attributes: {len(unknown_attributes)}")
    print(f"Total combinations per policy: {len(unknown_combinations)}")

    llm_instance = llm()
    os.makedirs("output", exist_ok=True)

    for privacy_policy_file_path in privacy_policy_file_paths:
        output_file_path = "output/" + os.path.basename(privacy_policy_file_path).replace('.txt', '_all_requests.json')
        privacy_policy_text = read_file(privacy_policy_file_path)
        if not privacy_policy_text:
            print(f"Privacy policy file {privacy_policy_file_path} is empty. Nothing to process.")
            continue
            
        print(f"\nProcessing {privacy_policy_file_path}...")
        
        result = infer_attributes_from_privacy_policy_text(
            privacy_policy_text=privacy_policy_text,
            attribute_json_text=json.dumps(llm_attributes_payload, indent=2),
            llm_instance=llm_instance,
            attribute_inference_prompt_template=attribute_inference_prompt_template
        )
        log(LOG_FILE_PATH, json.dumps(result, indent=2), heading="PARSED_RESULT")
        
        inferred_dict = {}
        for r in result:
            name = normalize_attribute_name(r.get("attribute_name", ""))
            val = r.get("inferred_value", "unknown")
            inferred_dict[name] = val
            
        all_requests = []
        for combo in unknown_combinations:
            request_obj = {}
            for k, v in inferred_dict.items():
                request_obj[k] = v
                
            for i, val in enumerate(combo):
                request_obj[unknown_names[i]] = val
                
            all_requests.append(request_obj)
            
        write_json_file(output_file_path, all_requests)
        print(f"Success! {len(all_requests)} requests saved to {output_file_path}")

if __name__ == "__main__":
    main()
