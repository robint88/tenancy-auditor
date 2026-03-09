# 🐕 LANDO | UK Tenancy Agreement Auditor

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0-white.svg)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-v4.0-38B2AC.svg)
![AI](https://img.shields.io/badge/Powered_by-Gemini_2.5_Flash--Lite-indigo.svg)

**Lando** is a specialist AI "watchdog" built to protect UK renters. It audits tenancy agreements against the **Renters' Rights Act 2026**, identifying illegal clauses and ensuring compliance with the latest housing legislation.

---

## 🚀 Key Features

* **🚫 Section 21 Scrutiny:** Automatically flags illegal 'no-fault' eviction clauses.
* **🔄 Periodic Term Verification:** Confirms fixed-term tenancies have been correctly transitioned to periodic/rolling terms.
* **📈 Rent Hike Audit:** Monitors rent increase clauses to ensure they stay within the "once per year" legal limit.
* **📄 Instant PDF Reporting:** Generates a professional compliance summary for immediate use in negotiations.

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python / Flask |
| **AI Engine** | Google GenAI (Gemini 2.5 Flash-Lite) |
| **Styling** | Tailwind CSS (Lando Indigo Theme) |
| **PDF Engine** | xhtml2pdf |
| **Deployment** | Render + Gunicorn |

## 📦 Quick Start

### 1. Clone & Navigate
git clone [https://github.com/YOUR_USERNAME/lando-auditor.git](https://github.com/YOUR_USERNAME/lando-auditor.git)
cd lando-auditor

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Environment Secrets
Create a .env file in the root directory:

## Code snippet
google_api=your_gemini_api_key_here

flask_secret=your_random_secret_string
### 4. Launch Lando
python app.py


⚖️ Legal Disclaimer
Lando provides informational analysis only. It is not a law firm and does not provide formal legal advice. AI models may occasionally misinterpret complex legal nuances. Always verify findings with a qualified legal professional or Citizens Advice before taking legal action.

Built with ❤️ for fairer renting in the UK.
