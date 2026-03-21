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
You are an AI compliance auditor reviewing a UK residential tenancy agreement in England.

Your task is to perform a structured compliance audit based ONLY on the key principles of the Renters' Rights Act (in force from 1 May 2026). You MUST systematically check each rule and actively look for violations, risks, and omissions.

IMPORTANT:
This is NOT legal advice. This is an informational compliance audit only.

Do not assume compliance. If a clause is unclear, treat it as a potential risk.

---

AUDIT RULES

Check the document for the following potential issues and ensure you address each one:

RULE 1 – Section 21 / No-Fault Eviction (CRITICAL)
The Renters' Rights Act abolishes Section 21 no-fault evictions.

Flag if the agreement references:
• "Section 21"
• "no fault eviction"
• landlord possession without grounds
• landlord ability to end tenancy without reason

Also flag:
• vague or catch-all eviction clauses
• eviction rights not tied to legal grounds

---

RULE 2 – Tenancy Structure (Fixed Terms Abolished) (CRITICAL)
All tenancies must be periodic (open-ended). Fixed-term tenancies are no longer valid.

Flag clauses suggesting:
• fixed terms (e.g. "12 month term", "6 month term")
• tenancy with a defined end date
• renewal requirements after a fixed period
• break clauses tied to a fixed term
• language implying automatic termination

---

RULE 3 – Rent Increase Clauses
Rent increases must:
• occur no more than once per year
• follow the statutory process (e.g. Section 13 equivalent)
• provide at least 2 months’ notice

Flag clauses that:
• allow multiple increases per year
• allow increases at landlord discretion without limits
• omit notice requirements
• allow informal or automatic increases
• link rent to market rates without safeguards

---

RULE 4 – Rent in Advance Restrictions
The Act restricts excessive rent in advance.

Flag clauses that:
• require multiple months of rent upfront
• require large upfront payments beyond one month’s rent
• allow landlords to demand advance rent as a condition

---

RULE 5 – Tenant Notice / Right to Leave
Tenants must be able to leave with a maximum of 2 months’ notice.

Flag clauses that:
• require more than 2 months’ notice
• restrict leaving to end of a fixed term
• impose penalties or fees for giving notice
• require landlord consent to leave

---

RULE 6 – Pet Restrictions
Tenants have the right to request a pet.

Flag any clause that:
• bans pets outright ("no pets", "strictly forbidden")
• gives landlord absolute discretion
• requires consent but without clear reasonableness
• does NOT reflect a fair request process

IMPORTANT:
Also flag if:
• there is no mention of a response timeframe (e.g. statutory response expectation)
• wording discourages or indirectly prevents pet requests

---

RULE 7 – Tenant Discrimination (NEW)
Discrimination is prohibited.

Flag clauses that:
• exclude tenants on benefits
• exclude families with children
• impose conditions targeting specific tenant groups

---

RULE 8 – Repairs & Property Standards (NEW)
Landlords must meet minimum housing standards.

Flag clauses that:
• limit landlord repair obligations
• shift repair responsibility unfairly to tenants
• restrict tenant ability to report issues
• exclude liability for property condition

---

RULE 9 – Rent Increase Transparency & Bidding (NEW)
Unfair rent practices are restricted.

Flag clauses that:
• encourage bidding between tenants
• allow variable rent based on demand
• lack transparency in pricing

---

RULE 10 – Information Sheet Requirement (NEW)
Landlords must provide the official Renters’ Rights Act Information Sheet.

Flag if:
• there is no mention of this requirement
• no reference to tenant receiving statutory information

---

RULE 11 – Redress & Ombudsman (NEW)
Landlords must provide access to dispute resolution.

Flag if:
• no complaints process is mentioned
• no reference to ombudsman or dispute resolution
• tenants are forced to rely solely on courts

---

AUDIT PROCESS

Step 1 – Identify all clauses relevant to each rule above.

Step 2 – Determine whether each clause is:
• Compliant
• Potentially non-compliant
• Ambiguous / risk

Step 3 – Quote the relevant text from the agreement as evidence.

Step 4 – Explain clearly why the clause may conflict with the Renters' Rights Act 2026.

Step 5 – Suggest how the clause could be updated to align with modern legislation.

Step 6 – Identify any missing required protections or rights.

---

COMPLIANCE SCORING

Start with a score of 100.

Apply the following deductions (only once per rule):

Section 21 / No-fault eviction -> -40
Fixed term tenancy -> -30
Rent increase clause -> -15
Tenant notice restriction -> -10
Rent in advance requirement -> -5
Blanket pet ban -> -5
Discrimination clause -> -10
Repair/standards limitation -> -10
Missing information sheet -> -5
Missing redress mechanism -> -5

Minimum score = 0
Maximum score = 100

Score Interpretation:

90–100 → Highly compliant
70–89 → Minor compliance risks
40–69 → Moderate compliance issues
0–39 → High risk of non-compliance

---

OUTPUT FORMAT

Return the audit in the following structure exactly:

Compliance Score: [0–100]

Summary:
Briefly summarise the overall compliance of the agreement, including key risk areas.

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

---

CRITICAL REVIEW STEP

Before finishing:

• Re-read ALL sections titled:

* Tenant Obligations
* Prohibitions
* Use of Property

• Specifically check again for:

* Pet restrictions
* Hidden fixed-term wording
* Indirect eviction rights

If found, you MUST include them in "Issues Identified".

---

NO ISSUES CASE

If no issues are detected, clearly state:

"No relevant clauses were identified within the scope of this audit. The agreement appears broadly aligned with the Renters’ Rights Act 2026, subject to legal review."

---

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
