# Internal Energy Dashboard

A small internal tool: an operator-facing dashboard over the customer solar
and energy-usage portfolio. Ten synthetic customers, twelve months of usage
each.

This repository is the *subject* of the Cloover AI PR-review case study —
pull requests opened here are what the review agent inspects.

## Run it

Two terminals.

**API** (port 8000):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env      # then set TOOL_API_TOKEN
$env:TOOL_API_TOKEN = "<the value from .env>"
uvicorn api.main:app --reload --port 8000
```

**Dashboard** (port 5173):

```powershell
cd web
npm install
Copy-Item .env.example .env      # VITE_TOOL_API_TOKEN must match TOOL_API_TOKEN
npm run dev
```

Tests:

```powershell
python -m pytest            # all
python -m pytest tests/test_api.py::test_no_sensitive_fields_in_responses
```

## How customer data is handled

`data/customers.json` is entirely synthetic — no real person, address, IBAN
or BSN — but the service treats it with the shape and the care that the
production record would need.

The rules the code enforces, and which a change should not quietly alter:

- **One allowlist.** `api/serializers.py` defines `OPERATOR_FIELDS`, the only
  customer columns that may cross the API boundary, and `SENSITIVE_FIELDS`,
  which must never appear in a response. Routes return
  `operator_view(...)`, never a raw database row.
- **No anonymous access to customer data.** Every customer route depends on
  `require_internal_auth`. `/api/health` is the only unauthenticated route.
- **Credentials come from the environment.** `TOOL_API_TOKEN` has no default;
  the service raises rather than falling back to a built-in value.
- **CORS is pinned** to the dashboard origin.
- **Queries are parameterised.** No string-formatted SQL.

`tests/test_api.py::test_no_sensitive_fields_in_responses` is the executable
form of the first rule: it checks both the field names and the sensitive
*values* from the seed file against every response body.

Addresses are visible to an authenticated operator by design — that is the
job of the tool. Banking, contact, date-of-birth, meter-identity and precise
coordinate data are not, in any view.
