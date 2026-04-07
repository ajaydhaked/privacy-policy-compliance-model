class ViolationAnalyzer:

    attribute_violation_reasons = {
        "offering_service_to_data_principal_within_india": {
            "false": "The service is explicitly not offered to individuals in India. DPDP Act applicability cannot be established.",
            "unknown": "Insufficient information to determine whether the service is offered to individuals in India.",
        },
        "lawful_purpose": {
            "false": "One or more stated data processing purposes are unlawful or expressly forbidden by law.",
        },
        "notice_languages_all_eighth_schedule": {
            "false": "The privacy notice is not available in all 22 Eighth Schedule languages of the Indian Constitution.",
        },
        "consent_is_freely_given": {
            "false": "Consent involves coercion, undue influence, fraud, misrepresentation, or is tied to unrelated services.",
        },
        "consent_is_specific_to_purpose": {
            "false": "Consent is not limited to a specific, clearly defined lawful purpose.",
        },
        "consent_is_informed": {
            "false": "The policy fails to inform users about the nature of data collected, purpose, rights, or grievance contact details.",
        },
        "consent_is_unambiguous": {
            "false": "Consent relies on passive mechanisms like pre-ticked boxes, silence, or implied consent rather than a clear opt-in.",
            "unknown": "The policy does not describe how consent is collected.",
        },
        "consent_request_language_all_eighth_schedule": {
            "false": "The consent request is not available in English and all 22 Eighth Schedule languages.",
        },
        "consent_request_contains_contact_details_of_dpo_or_equivalent": {
            "false": "No Data Protection Officer or equivalent contact details are provided in the policy or consent request.",
        },
        "easy_consent_withdrawal": {
            "false": "Withdrawing consent is more burdensome than giving it (e.g., requires physical letter or multi-step process).",
            "unknown": "No withdrawal mechanism is described or insufficient detail to assess ease of withdrawal.",
        },
        "consent_notice_information_about_personal_data": {
            "false": "The consent notice does not describe specific categories of personal data being collected.",
        },
        "consent_notice_purpose_of_processing": {
            "false": "The consent notice does not clearly state the purpose(s) for data collection and processing.",
        },
        "consent_notice_how_to_exercise_rights_sec6.4": {
            "false": "The consent notice does not explain how to withdraw consent (Section 6(4), DPDP Act).",
        },
        "consent_notice_how_to_exercise_rights_sec13": {
            "false": "The consent notice does not describe a grievance redressal mechanism (Section 13, DPDP Act).",
        },
        "consent_notice_how_to_complaint_to_board": {
            "false": "The consent notice does not inform users about their right to complain to the Data Protection Board of India.",
        },
    }

    def get_violations(self, access_request) -> list[dict]:
        violations = []

        for attribute, reason_map in self.attribute_violation_reasons.items():
            value = access_request.get(attribute)

            if value in reason_map:
                violations.append({
                    "attribute": attribute,
                    "value": value,
                    "reason": reason_map[value],
                })

        return violations

    def get_violations_list(self, violations: list[dict]) -> list[str]:
        return [violation["reason"] for violation in violations]

    def format_violations(self, violations: list[dict]) -> str:
        if not violations:
            return "No violations found. The privacy policy is compliant."

        lines = []
        for idx, violation in enumerate(violations, start=1):
            lines.append(f"{idx}. {violation['reason']}")

        return "\n".join(lines)