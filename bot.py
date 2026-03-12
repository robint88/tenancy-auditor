from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API = os.getenv("google_api")
client = genai.Client(api_key=GOOGLE_API)


def get_audit_result(file_bytes):
    prompt = (
        prompt
    ) = """
You are an AI compliance auditor reviewing a UK residential tenancy agreement.

Your task is to perform a structured compliance audit based ONLY on the key principles of the Renters' Rights Act 2026. You MUST look at each of the principles/rules stated.

IMPORTANT:
This is NOT legal advice. This is an informational compliance audit only.

Follow the instructions exactly.

--------------------------------------------------

AUDIT RULES

Check the document for the following potential issues and ensure you address each one:

RULE 1 – Section 21 / No-Fault Eviction
The Renters' Rights Act abolishes Section 21 no-fault evictions.
Flag if the agreement references:
• "Section 21"
• "no fault eviction"
• landlord possession without grounds
• landlord ability to end tenancy without reason

RULE 2 – Fixed Term Tenancies
Tenancy agreements should no longer create fixed-term tenancies.
Flag clauses suggesting:
• fixed terms (e.g. "12 month term", "6 month term")
• tenancy with a defined end date
• renewal requirements after a fixed period
• break clauses tied to a fixed term

RULE 3 – Rent Increase Clauses
Rent increases should generally occur no more than once per year via the statutory process.
Flag clauses that:
• allow multiple increases per year
• allow increases at landlord discretion without time limits
• allow increases without a formal notice process

RULE 4 – Rent in Advance Restrictions
The Act restricts excessive rent in advance payments.

Flag clauses that:
• require multiple months of rent in advance
• require large upfront rent payments beyond normal monthly rent
• allow landlords to demand several months rent upfront as a condition of the tenancy

RULE 5 – Tenant Notice / Right to Leave
Tenants should be able to end periodic tenancies with two months' notice.

Flag clauses that:
• require tenants to give more than two months' notice
• prevent tenants leaving except at the end of a fixed term
• impose penalties for ending the tenancy with notice

RULE 6 – Pet Restrictions
The Act limits blanket bans on pets.

Flag clauses that:
• prohibit pets entirely
• state "no pets allowed" without qualification
• give landlords absolute discretion to refuse pets without justification

--------------------------------------------------

AUDIT PROCESS

Step 1 – Identify any clause that may relate to the above rules.

Step 2 – Determine whether the clause appears compliant or potentially non-compliant.

Step 3 – Quote the relevant text from the agreement as evidence.

Step 4 – Explain clearly why the clause may conflict with the Renters' Rights Act 2026.

Step 5 – Suggest how the clause might be updated to align with modern legislation.

--------------------------------------------------

COMPLIANCE SCORING

Start with a score of 100.

Apply the following deductions:

Section 21 / No-fault eviction -> -40
Fixed term tenancy -> -30
Rent increase clause -> -15
Tenant notice restriction -> -10
Rent in advance requirement	-> -5
Blanket pet ban	-> -5

If multiple examples exist for the same rule, only deduct once.

Minimum score = 0  
Maximum score = 100

Score Interpretation

90–100 → Highly compliant
70–89 → Minor compliance risks
40–69 → Moderate compliance issues
0–39 → High risk of non-compliance

--------------------------------------------------

OUTPUT FORMAT

Return the audit in the following structure exactly.

Compliance Score: [0–100]

Summary:
Briefly summarise the overall compliance of the agreement.

Issues Identified:

1. Issue Type: [Rule Name]

Relevant Clause:
[Quote the clause text]

Explanation:
Explain why this clause may conflict with the Renters' Rights Act 2026.

Suggested Improvement:
Provide example wording that could make the clause more compliant.

Severity:
Critical / Moderate / Minor

--------------------------------------------------

If no issues are detected, clearly state that no relevant clauses were identified within the scope of this audit.

--------------------------------------------------

DISCLAIMER

This report is an AI-generated compliance audit designed to highlight potential issues in light of the Renters' Rights Act 2026.

It is NOT legal advice and should not replace review by a qualified solicitor or property law professional.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            types.Part.from_bytes(
                data=file_bytes,
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )
    return response.text
