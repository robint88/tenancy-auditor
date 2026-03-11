import os
import uuid
import stripe
from flask import (
    Flask,
    render_template,
    request,
    make_response,
    redirect,
    url_for,
    session,
)
from bot import get_audit_result
from dotenv import load_dotenv
from io import BytesIO
from xhtml2pdf import pisa
import re

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("flask_secret")

# Create folder for temporary PDFs if doesn't exist
UPLOAD_FOLDER = "temp_uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

stripe.api_key = os.getenv("stripe_key_test")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename != "":
            # 1. Generate unique ID. save to disk
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.pdf")
            file.save(file_path)

            # 2. Store ID in session
            session["pending_file_id"] = file_id

            # 3. Create Stripe Session
            try:
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            "price_data": {
                                "currency": "gbp",
                                "product_data": {"name": "Tenancy Agreement Audit"},
                                "unit_amount": 1500,
                            },
                            "quantity": 1,
                        }
                    ],
                    mode="payment",
                    success_url=url_for("success", _external=True),
                    cancel_url=url_for("index", _external=True),
                )
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                return str(e)

    return render_template("index.html")


@app.route("/success")
def success():
    # 1. Get ID from session
    file_id = session.get("pending_file_id")
    if not file_id:
        return redirect(url_for("index"))

    # 2. Find the file
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.pdf")

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # 3. Run audit
        analysis = get_audit_result(file_bytes)

        # 4. Delete file and clear session
        os.remove(file_path)
        session.pop("pending_file_id", None)

        return render_template("results.html", ai_result=analysis)

    return "Error: Audit file expired or not found.", 404


@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    ai_result_raw = request.form.get("ai_result")

    # --- STEP 1: Convert string to structured data ---
    # This uses regex to parse your AI output if it's a single string
    # If your AI already returns JSON/dict, you can skip this step
    compliance_score_match = re.search(r"Compliance Score: (\d+)", ai_result_raw)
    summary_match = re.search(
        r"Summary: (.*?)Issues Identified:", ai_result_raw, re.DOTALL
    )

    compliance_score = (
        compliance_score_match.group(1) if compliance_score_match else "N/A"
    )
    summary = summary_match.group(1).strip() if summary_match else ""

    # Extract individual issues
    issue_splits = re.split(r"\d+\.\sIssue Type:", ai_result_raw)[
        1:
    ]  # skip first empty split
    issues = []
    for split in issue_splits:
        split = split.strip()
        issue_type_match = re.match(r"(.*?)\sRelevant Clause:", split)
        relevant_clause_match = re.search(
            r"Relevant Clause:\s*(.*?)Explanation:", split, re.DOTALL
        )
        explanation_match = re.search(
            r"Explanation:\s*(.*?)Suggested Improvement:", split, re.DOTALL
        )
        suggested_improvement_match = re.search(
            r"Suggested Improvement:\s*(.*?)Severity:", split, re.DOTALL
        )
        severity_match = re.search(r"Severity:\s*(.*)", split)

        issue = {
            "Issue Type": issue_type_match.group(1).strip() if issue_type_match else "",
            "Relevant Clause": (
                relevant_clause_match.group(1).strip() if relevant_clause_match else ""
            ),
            "Explanation": (
                explanation_match.group(1).strip() if explanation_match else ""
            ),
            "Suggested Improvement": (
                suggested_improvement_match.group(1).strip()
                if suggested_improvement_match
                else ""
            ),
            "Severity": severity_match.group(1).strip() if severity_match else "",
        }
        issues.append(issue)

    # --- STEP 2: Build the HTML ---
    issues_html = ""
    for issue in issues:
        severity_class = issue.get("Severity", "").lower()
        issues_html += f"""
        <div class="issue">
            <h3>⚠ Issue Type: {issue.get('Issue Type')}</h3>
            <p><strong>Relevant Clause:</strong> {issue.get('Relevant Clause')}</p>
            <p><strong>Explanation:</strong> {issue.get('Explanation')}</p>
            <p><strong>Suggested Improvement:</strong> {issue.get('Suggested Improvement')}</p>
            <p class="{severity_class}"><strong>Severity:</strong> {issue.get('Severity')}</p>
        </div>
        """

    pdf_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                color: #222;
                font-size: 11pt;
            }}
            h1 {{
                text-align: center;
                color: #2E86AB;
                margin-bottom: 15px;
            }}
            h2 {{
                color: #2E86AB;
                border-bottom: 2px solid #ccc;
                padding-bottom: 5px;
                margin-top: 25px;
            }}
            .score {{
                font-size: 20pt;
                font-weight: bold;
                color: #E74C3C;
            }}
            .issue {{
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 15px;
                background-color: #fdfdfd;
                box-shadow: 1px 1px 3px #ccc;
            }}
            .issue h3 {{
                margin: 0 0 5px 0;
                font-size: 12pt;
            }}
            .clause, .explanation, .suggestion, .severity {{
                margin: 5px 0;
            }}
            .critical {{ color: #C0392B; }}
            .moderate {{ color: #D68910; }}
            .minor {{ color: #1F618D; }}
            .footer {{
                font-size: 9pt;
                color: #555;
                margin-top: 30px;
                border-top: 1px solid #ccc;
                padding-top: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>LANDO | Tenancy Audit Report</h1>

        <h2>Compliance Overview</h2>
        <p class="score">{compliance_score}</p>
        <p>{summary}</p>

        <h2>Issues Identified</h2>
        {issues_html}

        <div class="footer">
            LEGAL NOTICE: This report was generated using AI. It is an informational audit only and does not constitute legal advice.
        </div>
    </body>
    </html>
    """

    # --- STEP 3: Generate PDF ---
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(pdf_html, dest=buffer)
    if pisa_status.err:
        return "Error generating PDF", 500

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        "attachment; filename=Lando_Audit_Report.pdf"
    )
    return response


if __name__ == "__main__":
    # 1. Get the port Render assigned to you
    port = int(os.environ.get("PORT", 5000))
    # 2. Bind to 0.0.0.0 so the public URL can reach the app
    app.run(host="0.0.0.0", port=port)
