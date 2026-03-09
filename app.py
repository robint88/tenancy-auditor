from flask import Flask, render_template, request
from bot import get_audit_result  # Import your new function
from dotenv import load_dotenv
import os
from io import BytesIO
from xhtml2pdf import pisa
from flask import make_response

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("flask_secret")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename != "":
            # 1. Reset the pointer to the start of the file
            file.seek(0)

            # 2. Read the bytes
            file_bytes = file.read()

            # 3. Check if we actually got data
            if len(file_bytes) == 0:
                return "Error: The uploaded file is empty."

            analysis = get_audit_result(file_bytes)
            return render_template("results.html", ai_result=analysis)

    return render_template("index.html")


@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    ai_result = request.form.get("ai_result")

    # File-like buffer to receive PDF data
    buffer = BytesIO()

    # HTML wrapper for the PDF
    pdf_html = f"""
    <html>
        <body>
            <h1>LANDO | Audit Report</h1>
            <div class="content">{ai_result}</div>
            <hr>
            <p style="font-size: 9pt; color: #444;">
                <strong>LEGAL NOTICE:</strong> This document was generated using Artificial Intelligence. 
                It does not constitute legal advice and does not create a solicitor-client relationship. 
                Legislation like the Renters' Rights Act 2026 can be complex; please consult a 
                qualified legal professional or Citizens Advice before taking action.
            </p>
        </body>
    </html>
"""

    # HTML to PDF
    pisa_status = pisa.CreatePDF(pdf_html, dest=buffer)

    if pisa_status.err:
        return "Error generating PDF", 500

    # Prepare the response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        "attachment; filename=Lando_Audit_Report.pdf"
    )

    return response


if __name__ == "__main__":
    app.run(debug=True)
