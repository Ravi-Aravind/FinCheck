# FinCheck — Financial Fraud Detection System

**Software Engineering Assignment 10: Design and Demonstration of Test Cases Using Testing Tools**

FinCheck is a locally runnable academic demonstration of a transaction review workflow. It accepts transaction details, applies readable deterministic rules, stores the results in SQLite, and makes them available through a browser UI and JSON API. It does not identify real-world fraud reliably and is not a production financial service.

## Problem, objectives, and scope

The assignment demonstrates how a small application can be exercised at three levels: pytest unit and Flask integration tests, Postman REST assertions, and Selenium browser workflows. The project focuses on input validation, predictable scoring, persistence, and test isolation. It does not connect to banks, payment networks, external AI, or real-time fraud feeds.

Features include a responsive analysis form, client and server validation, result score and classification, local transaction history with deletion, SQLite persistence, and health/analyze/list/read/delete API routes. The frontend obtains results from the actual backend; it contains no seeded sample history.

## Technology and architecture

- Python 3.11+ (verified development environment: Python 3.12.0), Flask, SQLite
- HTML, CSS, and vanilla JavaScript
- pytest, Postman collection v2.1, Selenium 4 with Chrome and Selenium Manager

Request flow: browser form → `POST /api/analyze` → server-side validation → `fraud_detector.py` scoring → parameterized SQLite insert → JSON result → browser renders the saved result. History loads from `GET /api/transactions`; deletion calls the API.

## Repository structure

```text
app.py                         Flask routes and request validation
database.py                    SQLite schema and connections
fraud_detector.py              Pure scoring and classification rules
templates/                     Analysis and history pages
static/                         Responsive CSS and API-driven JavaScript
tests/                          pytest unit, API, and validation tests
selenium_tests/                 Browser workflows and isolated server fixture
postman/financial_fraud_detection.postman_collection.json
requirements.txt                Runtime and test dependencies
.env.example                    Optional database configuration example
```

## Rules and schema

Scores start at zero and add: amount **greater than ₹100,000** +30; any location other than India +25; a location outside the explicitly recognized list +20; configured high-risk type +25. The final score is capped at 100. `LEGITIMATE` means 0–49; `SUSPICIOUS` means 50–100. The recognized locations are India, United States, United Kingdom, Canada, Australia, Singapore, Germany, France, and Japan (case-insensitive). Other location text is accepted as an unknown location. Valid types are `PURCHASE`, `TRANSFER`, `WITHDRAWAL`, and `REFUND`; high-risk types are an explicitly configurable empty set by default.

These rules are intentionally simple and have no empirical validation. Because the independent international and unknown-location rules both apply, an unknown non-India location adds 45 points. This is a teaching example, not a calibrated risk model.

SQLite table `transactions`: `transaction_id` TEXT primary key, `amount` REAL, `location` TEXT, `transaction_type` TEXT, `risk_score` INTEGER, `status` TEXT, and `created_at` UTC ISO-8601 TEXT. IDs accept 1–64 ASCII letters, numbers, `_`, or `-`; duplicate IDs produce 409 and never overwrite a record.

## API

All API errors are JSON objects of the form `{"error":"..."}`. Successful analysis returns 201. Amount must be a finite JSON number greater than zero (booleans are rejected). Required fields are `transaction_id`, `amount`, `location`, and `transaction_type`.

### `GET /api/health`

200: `{"status":"ok","service":"financial-fraud-detection"}`

### `POST /api/analyze`

Example request:

```json
{"transaction_id":"DEMO-001","amount":2500,"location":"India","transaction_type":"PURCHASE"}
```

201: `{"transaction_id":"DEMO-001","risk_score":0,"status":"LEGITIMATE","created_at":"2026-10-18T12:00:00+00:00"}`. Invalid content type, malformed body, missing or invalid fields: 400. Duplicate ID: 409.

### `GET /api/transactions`

200: `{"transactions":[{"transaction_id":"DEMO-001","amount":2500.0,"location":"India","transaction_type":"PURCHASE","risk_score":0,"status":"LEGITIMATE","created_at":"..."}]}`. An empty database returns an empty array.

### `GET /api/transactions/<transaction_id>`

200 returns one transaction in the list schema above; absent transaction: 404.

### `DELETE /api/transactions/<transaction_id>`

200: `{"message":"transaction deleted","transaction_id":"DEMO-001"}`; absent transaction: 404.

## Install and run locally

Prerequisites: Python 3.11 or later and pip. A browser is only needed for Selenium; Chrome/Chromium is recommended. In PowerShell from the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

If PowerShell blocks venv activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for that terminal, or invoke `.venv\Scripts\python.exe` directly. On Linux/macOS:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. The default database is `instance/transactions.sqlite3`, created at application startup. To use another path, set `FINCHECK_DATABASE` before starting the process. To reset the local database, stop the app and remove `instance/transactions.sqlite3`; the schema is recreated on next startup. This reset removes all saved local transaction records.

## Testing

Run the backend tests (they use a separate temporary database per test):

```powershell
python -m pytest -q
```

The unit tests cover score rules and threshold boundaries; API/validation tests cover malformed and invalid input, persistence, health, list/read/delete, and duplicate IDs. Browser tests have a separate temporary SQLite database and server for each test, and use explicit waits:

```powershell
python -m pytest -q selenium_tests/
```

`pytest.ini` limits default discovery to `tests/`, keeping browser prerequisites optional. The explicit Selenium command runs the five browser workflows. Selenium Manager attempts to obtain a compatible driver automatically. Chrome must be installed and available. For a visible browser set `$env:SELENIUM_HEADLESS = '0'`; reset with `Remove-Item Env:SELENIUM_HEADLESS`. If Selenium Manager cannot resolve a driver due to network restrictions, install a compatible ChromeDriver and place it on `PATH`.

### Postman

Start the app, import `postman/financial_fraud_detection.postman_collection.json` into Postman, and run the collection in order. It defaults `base_url` to `http://127.0.0.1:5000` and uses `test_id` for create/get/list/duplicate/delete dependencies. A second run can encounter a duplicate on the initial create: change the collection variable `test_id` to a fresh ID first. The collection includes successful health/create/list/get/delete, suspicious scoring, and invalid/malformed/duplicate/missing-resource cases. Assertions check statuses and response content. Newman may run it when installed with `newman run postman/financial_fraud_detection.postman_collection.json`; Newman is not a project dependency.

## Results and limitations

**Verified execution results (18 October 2026):** `python -m pytest -q` passed **36 tests** in 0.84 seconds. `python -m pytest -q selenium_tests/` passed **5 browser tests** in 88.30 seconds. Together the two documented commands execute all 41 tests. Chrome and its driver were available to Selenium in this environment. `git check-ignore -v chromedriver/ se-metadata.json` confirmed both paths are ignored; `git ls-files -- chromedriver se-metadata.json` returned no tracked files. Postman execution was not part of this remediation verification.

The scoring is transparent but not statistically validated; location recognition is a small fixed list; no authentication, authorization, encryption at rest, rate limiting, or production deployment hardening is included. Do not enter real account or payment data. Flask's local development server is intended for local academic use only.

## Review focus

For independent review, inspect server-side validation and database isolation in `app.py` / `tests/conftest.py`, scoring boundaries in `fraud_detector.py` / `tests/test_fraud_detector.py`, and the one-run record lifecycle in the Postman collection and Selenium fixtures.
