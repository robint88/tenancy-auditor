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
    ai_result = request.form.get("ai_result")
    buffer = BytesIO()
    pdf_html = f"""
    <html>
        <body>
            <h1>LANDO | Audit Report</h1>
            <div class="content">{ai_result}</div>
            <hr>
            <p style="font-size: 9pt; color: #444;">
                <strong>LEGAL NOTICE:</strong> This document was generated using AI. 
                It does not constitute legal advice.
            </p>
        </body>
    </html>
    """
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
    app.run(debug=True)
