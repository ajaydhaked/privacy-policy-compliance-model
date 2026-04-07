import os
import json
from src.utils import read_file, read_json, write_json_file, log
from src.llm import llm
from src.attributeValidator import AttributeValidator


class InferAttributesLLM:

    def parse_json_response(self, response_text):
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        text = text.strip()
        text = text.lower()
        return json.loads(text)

#   [
#     {
#       "attribute_name": "law_applicable",
#       "inferred_value": "true",
#       "justification": "The privacy policy states that services are offered to users in India, which brings the processing under the DPDP Act."
#     }...
#   ]
#   to verify attribute_name, inferred_value, justification are present
#   then to verify value

    def verify_json_response(self, json_response:list, attribute_validator:AttributeValidator):
        for ele in json_response:
            if "attribute_name" not in ele or "inferred_value" not in ele or "justification" not in ele:
                raise ValueError("Invalid JSON response: missing attribute_name, inferred_value, or justification")
            attribute_validator.validate_key_value(ele["attribute_name"], ele["inferred_value"])

        

    def infer_attributes_from_privacy_policy_text(self, privacy_policy_text, attribute_json_text, 
                    llm_instance, attribute_inference_prompt_template, attribute_validator, log_file_path = None):
        
        prompt = attribute_inference_prompt_template.replace(
            "<PRIVACY_POLICY_TEXT>", privacy_policy_text).replace(
                "<ATTRIBUTE_JSON>", attribute_json_text)
        log(prompt, heading="PROMPT", file_path=log_file_path)

        
        response = llm_instance.process_prompt(prompt)
        log(json.dumps(
                llm_instance.last_used_tokens
            ), heading="TOKEN_USAGE", file_path=log_file_path)
        log(response, heading="LLM_RESPONSE", file_path=log_file_path)

        parsed_json_response = self.parse_json_response(response)
        self.verify_json_response(parsed_json_response, attribute_validator)
        return parsed_json_response
