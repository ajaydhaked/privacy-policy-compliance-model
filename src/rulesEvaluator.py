
from dataclasses import dataclass, field
from typing import Any
import json
from src.accessRequest import AccessRequest
from src.utils import log

PURPOSE_LEGITIMATE_USE_VALUES = {
    "integrity_of_india",
    "sovereignty_of_india",
    "security_of_state",
    "obligation_under_law",
    "medical_emergency",
    "disaster_management",
    "safeguarding_employment",
    "state_benefits",
}


class RulesEvaluator:
    def __init__(self):
        self.rules = {
            "rule1": {
                "function": self.rule1,
                "dependencies": []
            },
            "rule3": {
                "function": self.rule3,
                "dependencies": ["rule1", "rule7", "rule8", "rule11"]
            },
            "rule4": {
                "function": self.rule4,
                "dependencies": []
            },
            "rule5": {
                "function": self.rule5,
                "dependencies": ["rule4", "rule6"]
            },
            "rule6": {
                "function": self.rule6,
                "dependencies": []
            },
            "rule7": {
                "function": self.rule7,
                "dependencies": ["rule5"]
            },
            "rule8": {
                "function": self.rule8,
                "dependencies": ["rule5"]
            },
            "rule9": {
                "function": self.rule9,
                "dependencies": ["rule7", "rule8"]
            },
            "rule10": {
                "function": self.rule10,
                "dependencies": ["rule1", "rule7", "rule8", "rule11"]
            },
            "rule11": {
                "function": self.rule11,
                "dependencies": ["rule7", "rule8"]
            },
        }
        self.evaluation_order = self.get_evaluation_order()  
        self.evaluation_logs = ""
 

    def get_evaluation_order(self) -> list[str]:
        visited = set()
        rec_stack = set()
        order = []
 
        def dfs(rule_name: str):
            if rule_name in rec_stack:
                raise ValueError(f"Cycle detected in rule dependencies involving '{rule_name}'")
            if rule_name in visited:
                return
            visited.add(rule_name)
            rec_stack.add(rule_name)
            for dep in self.rules[rule_name]["dependencies"]:
                dfs(dep)
            rec_stack.remove(rule_name)
            order.append(rule_name)
 
        for rule_name in self.rules:
            dfs(rule_name)
 
        return order
        

    # ---------------------------------------------------------------------------
    # Rule 1
    # IF offering_service_to_data_principal_within_india = true
    # THEN law_applicable = true
    # ---------------------------------------------------------------------------
    def rule1(self, request) -> bool:
        success = request.get("offering_service_to_data_principal_within_india") == "true"
 
        if success:
            request.set("law_applicable", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 1 Success" if success else "# Rule 1 Failure"}

            IF
            offering_service_to_data_principal_within_india = (true)
            THEN
            law_applicable = true

            # Attribute values
            offering_service_to_data_principal_within_india = {request.get("offering_service_to_data_principal_within_india")}
            law_applicable = {request.get("law_applicable")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 2
    # IF offering_service_to_data_principal_within_india = false
    # THEN law_applicable = false
    # ---------------------------------------------------------------------------
    def rule2(self, request) -> bool:
        success = request.get("offering_service_to_data_principal_within_india") == "false"
 
        if success:
            request.set("law_applicable", "false")
 
        self.evaluation_logs += f"""
            {"# Rule 2 Success" if success else "# Rule 2 Failure"}

            IF 
            offering_service_to_data_principal_within_india = (false)
            THEN
            law_applicable = false

            # Attribute values
            offering_service_to_data_principal_within_india = {request.get("offering_service_to_data_principal_within_india")}
            law_applicable = {request.get("law_applicable")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 3
    # IF law_applicable = true
    #    AND (consent_status = active OR legitimate_use = true)
    #    AND lawful_purpose = true
    # THEN allow_data_processing = true
    # ---------------------------------------------------------------------------
    def rule3(self, request) -> bool:
        law_applicable = request.get("law_applicable") == "true"
        consent_or_legitimate = (
            request.get("consent_status") == "active"
            or request.get("legitimate_use") == "true"
        )
        lawful_purpose = request.get("lawful_purpose") == "true"
 
        success = law_applicable and consent_or_legitimate and lawful_purpose
 
        if success:
            request.set("allow_data_processing", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 3 Success" if success else "# Rule 3 Failure"}

            IF
            law_applicable = true AND (consent_status = active OR legitimate_use = true) AND lawful_purpose = true
            THEN
            allow_data_processing = true

            # Attribute values
            law_applicable = {request.get("law_applicable")}
            consent_status = {request.get("consent_status")}
            legitimate_use = {request.get("legitimate_use")}
            lawful_purpose = {request.get("lawful_purpose")}
            allow_data_processing = {request.get("allow_data_processing")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 4
    # IF consent_notice_information_about_personal_data = true
    #    AND consent_notice_purpose_of_processing = true
    #    AND consent_notice_how_to_exercise_rights_sec6.4 = true
    #    AND consent_notice_how_to_exercise_rights_sec13 = true
    #    AND consent_notice_how_to_complaint_to_board = true
    #    AND notice_languages_all_eighth_schedule = true
    # THEN consent_notice_wellformed = true
    # ---------------------------------------------------------------------------
    def rule4(self, request) -> bool:
        info_about_personal_data = (
            request.get("consent_notice_information_about_personal_data") == "true"
        )
        purpose_of_processing = (
            request.get("consent_notice_purpose_of_processing") == "true"
        )
        rights_sec6_4 = (
            request.get("consent_notice_how_to_exercise_rights_sec6.4") == "true"
        )
        rights_sec13 = (
            request.get("consent_notice_how_to_exercise_rights_sec13") == "true"
        )
        complaint_to_board = (
            request.get("consent_notice_how_to_complaint_to_board") == "true"
        )
        language_options_valid = request.get("notice_languages_all_eighth_schedule") == "true"
 
        success = (
            info_about_personal_data
            and purpose_of_processing
            and rights_sec6_4
            and rights_sec13
            and complaint_to_board
            and language_options_valid
        )
 
        if success:
            request.set("consent_notice_wellformed", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 4 Success" if success else "# Rule 4 Failure"}

            IF
            consent_notice_information_about_personal_data = true AND 
            consent_notice_purpose_of_processing = true AND 
            consent_notice_how_to_exercise_rights_sec6.4  = true AND 
            consent_notice_how_to_exercise_rights_sec13 = true AND 
            consent_notice_how_to_complaint_to_board  = true AND
            notice_languages_all_eighth_schedule = true
            THEN
            consent_notice_wellformed = true

            # Attribute values
            consent_notice_information_about_personal_data = {request.get("consent_notice_information_about_personal_data")}
            consent_notice_purpose_of_processing = {request.get("consent_notice_purpose_of_processing")}
            consent_notice_how_to_exercise_rights_sec6.4 = {request.get("consent_notice_how_to_exercise_rights_sec6.4")}
            consent_notice_how_to_exercise_rights_sec13 = {request.get("consent_notice_how_to_exercise_rights_sec13")}
            consent_notice_how_to_complaint_to_board = {request.get("consent_notice_how_to_complaint_to_board")}
            notice_languages_all_eighth_schedule = {request.get("notice_languages_all_eighth_schedule")}
            consent_notice_wellformed = {request.get("consent_notice_wellformed")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 5
    # IF consent_is_freely_given = true
    #    AND consent_is_specific_to_purpose = true
    #    AND consent_is_informed = true
    #    AND consent_is_unambiguous = true
    #    AND consent_request_language_all_eighth_schedule = true
    #    AND consent_request_contains_contact_details_of_dpo_or_equivalent = true
    #    AND option_for_consent_withdrawal = true
    #    AND consent_notice_wellformed = true
    # THEN consent_preconditions_fullfilled = true
    # ---------------------------------------------------------------------------
    def rule5(self, request) -> bool:
        freely_given = request.get("consent_is_freely_given") == "true"
        specific_to_purpose = request.get("consent_is_specific_to_purpose") == "true"
        informed = request.get("consent_is_informed") == "true"
        unambiguous = request.get("consent_is_unambiguous") == "true"
        language_options_valid = request.get("consent_request_language_all_eighth_schedule") == "true"
        dpo_contact = (
            request.get(
                "consent_request_contains_contact_details_of_dpo_or_equivalent"
            )
            == "true"
        )
        withdrawal_option = request.get("option_for_consent_withdrawal") == "true"
        notice_wellformed = request.get("consent_notice_wellformed") == "true"
 
        success = (
            freely_given
            and specific_to_purpose
            and informed
            and unambiguous
            and language_options_valid
            # and dpo_contact
            and withdrawal_option
            and notice_wellformed
        )
 
        if success:
            request.set("consent_preconditions_fullfilled", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 5 Success" if success else "# Rule 5 Failure"}

            IF
            consent_is_freely_given = true
            AND
            consent_is_specific_to_purpose = true
            AND
            consent_is_informed = true
            AND
            consent_is_unambiguous = true
            AND
            consent_request_language_all_eighth_schedule = true AND
            consent_request_contains_contact_details_of_dpo_or_equivalent = true
            AND
            option_for_consent_withdrawal = true
            AND
            consent_notice_wellformed = true
            THEN
            consent_preconditions_fullfilled = true

            # Attribute values
            consent_is_freely_given = {request.get("consent_is_freely_given")}
            consent_is_specific_to_purpose = {request.get("consent_is_specific_to_purpose")}
            consent_is_informed = {request.get("consent_is_informed")}
            consent_is_unambiguous = {request.get("consent_is_unambiguous")}
            consent_request_language_all_eighth_scedule = {request.get("consent_request_language_all_eighth_schedule")}
            consent_request_contains_contact_details_of_dpo_or_equivalent = {request.get("consent_request_contains_contact_details_of_dpo_or_equivalent")}
            option_for_consent_withdrawal = {request.get("option_for_consent_withdrawal")}
            consent_notice_wellformed = {request.get("consent_notice_wellformed")}
            consent_preconditions_fullfilled = {request.get("consent_preconditions_fullfilled")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 6
    # IF easy_consent_withdrawal = true
    # THEN option_for_consent_withdrawal = true
    # ---------------------------------------------------------------------------
    def rule6(self, request) -> bool:
        success = request.get("easy_consent_withdrawal") == "true"
 
        if success:
            request.set("option_for_consent_withdrawal", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 6 Success" if success else "# Rule 6 Failure"}

            IF
            easy_consent_withdrawal = true 
            THEN
            option_for_consent_withdrawal = true 

            # Attribute values
            easy_consent_withdrawal = {request.get("easy_consent_withdrawal")}
            option_for_consent_withdrawal = {request.get("option_for_consent_withdrawal")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 7
    # IF consent_preconditions_fullfilled = true
    #    AND consent_action = true
    #    AND consent_withdraw_action = false
    # THEN consent_status = active
    # ---------------------------------------------------------------------------
    def rule7(self, request) -> bool:
        preconditions = request.get("consent_preconditions_fullfilled") == "true"
        consent_action = request.get("consent_action") == "true"
        not_withdrawn = request.get("consent_withdraw_action") == "false"
 
        success = preconditions and consent_action and not_withdrawn

        if success:
            request.set("consent_status", "active")
 
        self.evaluation_logs += f"""
            {"# Rule 7 Success" if success else "# Rule 7 Failure"}

            IF
            consent_preconditions_fullfilled = true and 
            consent_action = true AND consent_withdraw_action = false
            THEN
            consent_status = active

            # Attribute values
            consent_preconditions_fullfilled = {request.get("consent_preconditions_fullfilled")}
            consent_action = {request.get("consent_action")}
            consent_withdraw_action = {request.get("consent_withdraw_action")}
            consent_status = {request.get("consent_status")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 8
    # IF consent_preconditions_fullfilled = true
    #    AND consent_action = true
    #    AND consent_withdraw_action = true
    # THEN consent_status = withdrawn
    # ---------------------------------------------------------------------------
    def rule8(self, request) -> bool:
        preconditions = request.get("consent_preconditions_fullfilled") == "true"
        consent_action = request.get("consent_action") == "true"
        withdrawn = request.get("consent_withdraw_action") == "true"
 
        success = preconditions and consent_action and withdrawn
 
        if success:
            request.set("consent_status", "withdrawn")
 
        self.evaluation_logs += f"""
            {"# Rule 8 Success" if success else "# Rule 8 Failure"}

            IF
            consent_preconditions_fullfilled = true and 
            consent_action = true AND consent_withdraw_action = true
            THEN
            consent_status = withdrawn

            # Attribute values
            consent_preconditions_fullfilled = {request.get("consent_preconditions_fullfilled")}
            consent_action = {request.get("consent_action")}
            consent_withdraw_action = {request.get("consent_withdraw_action")}
            consent_status = {request.get("consent_status")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 9
    # IF consent_status = withdrawn
    # THEN past_processing_with_active_consent_legal = true
    # ---------------------------------------------------------------------------
    def rule9(self, request) -> bool:
        success = request.get("consent_status") == "withdrawn"
 
        if success:
            request.set("past_processing_with_active_consent_legal", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 9 Success" if success else "# Rule 9 Failure"}

            IF consent_status = withdrawn
            THEN
            past_processing_with_active_consent_legal = true

            # Attribute values
            consent_status = {request.get("consent_status")}
            past_processing_with_active_consent_legal = {request.get("past_processing_with_active_consent_legal")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 10
    # IF law_applicable = true
    #    AND (
    #          (consent_status = withdrawn AND reasonable_time_elapsed = false)
    #          OR legitimate_use = true
    #        )
    #    AND lawful_purpose = true
    # THEN allow_data_processing = true
    # ---------------------------------------------------------------------------
    def rule10(self, request) -> bool:
        law_applicable = request.get("law_applicable") == "true"
        withdrawn_within_time = (
            request.get("consent_status") == "withdrawn"
            and request.get("reasonable_time_elapsed") == "false"
        )
        legitimate_use = request.get("legitimate_use") == "true"
        lawful_purpose = request.get("lawful_purpose") == "true"
 
        success = law_applicable and (withdrawn_within_time or legitimate_use) and lawful_purpose
 
        if success:
            request.set("allow_data_processing", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 10 Success" if success else "# Rule 10 Failure"}

            IF
            law_applicable = true AND ((consent_status = withdrawn AND reasonable_time_elapsed = false ) OR legitimate_use = true) AND lawful_purpose = true
            THEN
            allow_data_processing = true

            # Attribute values
            law_applicable = {request.get("law_applicable")}
            consent_status = {request.get("consent_status")}
            reasonable_time_elapsed = {request.get("reasonable_time_elapsed")}
            legitimate_use = {request.get("legitimate_use")}
            lawful_purpose = {request.get("lawful_purpose")}
            allow_data_processing = {request.get("allow_data_processing")}
        """
        return success
 
    # ---------------------------------------------------------------------------
    # Rule 11
    # IF (
    #       (consent_status = (not_given OR active) AND voluntary_data_for_specified_purpose = true)
    #       OR (
    #             (consent_for_state_benefits = true OR available_to_state_and_notified_by_government = true)
    #             AND purpose_of_processing = state_benefits
    #          )
    #       OR purpose_of_processing IN {integrity_of_india, sovereignty_of_india, security_of_state,
    #                                     obligation_under_law, medical_emergency, disaster_management,
    #                                     safeguarding_employment}
    #    )
    # THEN legitimate_use = true
    # ---------------------------------------------------------------------------
    def rule11(self, request) -> bool:
        consent_status = request.get("consent_status")
        purpose = request.get("purpose_of_processing")
 
        voluntary_branch = (
            consent_status in ("not_given", "active")
            and request.get("voluntary_data_for_specified_purpose") == "true"
        )
 
        state_benefits_branch = (
            (
                request.get("consent_for_state_benefits") == "true"
                or request.get("available_to_state_and_notified_by_government") == "true"
            )
            and purpose == "state_benefits"
        )
 
        sovereign_purposes = {
            "integrity_of_india",
            "sovereignty_of_india",
            "security_of_state",
            "obligation_under_law",
            "medical_emergency",
            "disaster_management",
            "safeguarding_employment",
        }
        sovereign_branch = purpose in sovereign_purposes
 
        success = voluntary_branch or state_benefits_branch or sovereign_branch
 
        if success:
            request.set("legitimate_use", "true")
 
        self.evaluation_logs += f"""
            {"# Rule 11 Success" if success else "# Rule 11 Failure"}

            IF
            (
            consent_status = (not_given OR active) AND 
            voluntary_data_for_specified_purpose = true
            ) 
            OR
            (
            (consent_for_state_benefits = true OR available_to_state_and_notified_by_government = true) AND
            purpose_of_processing = state_benefits
            ) 
            OR
            purpose_of_processing = integrity_of_india
            OR
            purpose_of_processing = sovereignty_of_india
            OR
            purpose_of_processing = security_of_state
            OR
            purpose_of_processing = obligation_under_law
            OR
            purpose_of_processing = medical_emergency
            OR
            purpose_of_processing = disaster_management
            OR
            purpose_of_processing = safeguarding_employment
            THEN
            legitimate_use = true


            # Attribute values
            consent_status = {consent_status}
            voluntary_data_for_specified_purpose = {request.get("voluntary_data_for_specified_purpose")}
            consent_for_state_benefits = {request.get("consent_for_state_benefits")}
            available_to_state_and_notified_by_government = {request.get("available_to_state_and_notified_by_government")}
            purpose_of_processing = {purpose}
            legitimate_use = {request.get("legitimate_use")}
        """
        return success


    def evaluate_all_rules(self, request):
        """
        Evaluate all rules for the given request.
        """
        for rule_name in self.evaluation_order:
            rule_func = self.rules[rule_name]["function"]
            rule_func(request)
