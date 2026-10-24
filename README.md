# Drone Manager

A web-based drone fleet management and analytics application built with **HTML, CSS, JavaScript, Bootstrap 5, FastAPI, and Firebase Cloud Firestore**.

The frontend is a single-page-style dashboard served as static files. The backend exposes a REST API for fleet records and analytics. This project intentionally has **no login, registration, password-reset, Firebase Authentication, or API-token flow**.

> **Security notice:** The API has no built-in authentication. Run it locally during development. Do not expose it to the public internet or deploy it as a public API unless you first add an appropriate access-control layer. CORS is not authentication.

## Contents

- [Features](#features)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [1. Get the project ready](#1-get-the-project-ready)
- [2. Configure Firebase Firestore](#2-configure-firebase-firestore)
- [3. Configure environment variables](#3-configure-environment-variables)
- [4. Install Python dependencies](#4-install-python-dependencies)
- [5. Run automated tests](#5-run-automated-tests)
- [6. Start the backend API](#6-start-the-backend-api)
- [7. Start the frontend](#7-start-the-frontend)
- [8. Verify the application](#8-verify-the-application)
- [API overview](#api-overview)
- [Firestore collections](#firestore-collections)
- [Configuration notes](#configuration-notes)
- [Troubleshooting](#troubleshooting)
- [Security and deployment checklist](#security-and-deployment-checklist)
- [Known limitations](#known-limitations)

## Features

- Professional, responsive fleet-management interface.
- Dashboard metrics and fleet status visualization.
- Manage drone, battery, mission, flight-log, and maintenance records through the API and frontend.
- Battery history endpoint and battery-status analytics.
- Mission cancellation and maintenance completion/cancellation actions.
- Flight-duration and battery-consumption calculations.
- Analytics endpoints for dashboard KPIs, missions, flights, batteries, maintenance, and trends.
- Health and configuration endpoints.
- Automated API tests using a test store; those tests do not by themselves prove that a live Firebase project is configured correctly.
- No sign-in screen or Settings page.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript |
| UI framework | Bootstrap 5 |
| Icons and charts | Bootstrap Icons and Plotly via CDN |
| Backend | Python, FastAPI, Pydantic |
| Database | Firebase Cloud Firestore |
| Firebase server SDK | Firebase Admin SDK |
| Tests | pytest, FastAPI/Starlette TestClient |

The frontend loads Bootstrap, Bootstrap Icons, and Plotly from external CDNs, so an internet connection is needed for those assets unless you change the project to serve them locally.

## Project structure

```text
Drone_Manager_Rebuilt/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── analytics.py
│   │   │   └── resources.py
│   │   ├── services/
│   │   │   └── store.py
│   │   ├── config.py
│   │   ├── main.py
│   │   └── schemas.py
│   └── __init__.py
├── frontend/
│   ├── assets/
│   │   ├── app.js
│   │   └── style.css
│   └── index.html
├── docs/
│   ├── DATA_MODEL.md
│   └── LOCAL_SETUP.md
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── netlify.toml
├── pytest.ini
├── requirements.txt
├── TEST_REPORT.md
└── README.md
```

## Prerequisites

- Windows, macOS, or Linux.
- Python **3.12 recommended**.
- A Firebase project with Cloud Firestore enabled.
- A Firebase Admin service-account JSON key for backend access.
- VS Code or another editor (recommended).
- Internet access for installing Python packages and loading frontend CDN assets.

## 1. Get the project ready

Extract the ZIP archive, then open the `Drone_Manager_Rebuilt` folder in VS Code.

Open a terminal at the project root. The following commands are for **Windows PowerShell**.

Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use a terminal session permitted by your device policy or run the project using the virtual environment's Python executable directly. Do not weaken system security settings just to activate a virtual environment.

Copy the sample environment file:

```powershell
Copy-Item .env.example .env
```

On macOS/Linux, the equivalent is:

```bash
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
```

## 2. Configure Firebase Firestore

1. Open the [Firebase Console](https://console.firebase.google.com/).
2. Create a Firebase project or select an existing project.
3. Open **Build → Firestore Database** and create a database if one does not already exist.
4. In the project settings, open the **Service accounts** section.
5. Generate a private key for the Firebase Admin SDK.
6. Save the downloaded JSON file at the project root using this filename:

   ```text
   firebase-service-account.json
   ```

7. Confirm that `.env` points to this file and contains the correct project ID (see the next section).

**Keep the service-account JSON private.** Never put it in `frontend/`, include it in a public repository, paste its contents into an issue, or commit it. The included `.gitignore` excludes the default filename, but still check `git status` before committing.

The Firebase Admin SDK runs on the backend. The browser frontend must not receive the service-account key.

## 3. Configure environment variables

Open `.env` in the project root. A typical local configuration is:

```dotenv
APP_NAME=Drone Manager API
APP_VERSION=1.0.0
ENVIRONMENT=development
FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id
FRONTEND_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

Replace `your-firebase-project-id` with the actual Firebase project ID.

Notes:

- `FIREBASE_CREDENTIALS_PATH` is interpreted relative to the process's working directory unless the application configuration specifies otherwise. Start Uvicorn from the project root.
- `FRONTEND_ORIGINS` must include the exact origin(s) used by the frontend. An origin includes the scheme, hostname, and port.
- Do not add secrets to frontend JavaScript or HTML.
- No authentication environment variables are required because authentication is intentionally not implemented.

## 4. Install Python dependencies

With the virtual environment activated and the terminal at the project root:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Check the Python version and installed dependencies if installation fails:

```powershell
python --version
pip --version
```

## 5. Run automated tests

From the project root:

```powershell
python -m pytest -q
```

The tests use a test/dummy data store for API behavior. A passing test suite is useful evidence that covered routes and validation work, but it does **not** confirm that your service-account key is valid, Firestore is reachable, the browser UI works end-to-end, or deployment is secure.

Deprecation warnings may appear from dependencies or test fixtures. Warnings are not automatically test failures, but investigate them when updating dependencies.

## 6. Start the backend API

In the first terminal, from the project root:

```powershell
uvicorn backend.app.main:app --reload
```

Keep this terminal open while using the application.

Useful local endpoints:

- Health check: <http://127.0.0.1:8000/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Alternative API documentation: <http://127.0.0.1:8000/redoc>
- API configuration: <http://127.0.0.1:8000/api/v1/config>

The health response includes database-readiness information. If Firestore credentials are missing or invalid, the data endpoints may return HTTP `503` with a configuration-related diagnostic.

## 7. Start the frontend

Open a **second terminal** at the project root. Do not stop the backend terminal.

Run the static file server:

```powershell
python -m http.server 5500 --bind 127.0.0.1 --directory frontend
```

Then open:

<http://127.0.0.1:5500/>

The frontend is served separately from the FastAPI backend. Opening `frontend/index.html` directly with a `file://` URL is not recommended; use the local HTTP server above.

### Changing the API base URL

The Settings page has been removed. If the backend URL changes, update the API base URL constant in:

```text
frontend/assets/app.js
```

For local development, the expected API base URL is:

```text
http://127.0.0.1:8000/api/v1
```

If you change the frontend host or port, update `FRONTEND_ORIGINS` in `.env` and restart the backend.

## 8. Verify the application

1. Confirm `http://127.0.0.1:8000/health` responds.
2. Confirm `http://127.0.0.1:8000/docs` displays the API documentation.
3. Confirm the health response reports that the database is ready after Firebase is configured.
4. Open `http://127.0.0.1:5500/`.
5. Check that the dashboard loads and that the browser developer console has no uncaught JavaScript errors.
6. Try creating or editing a test record, then refresh the page to verify persistence.
7. Check the backend terminal and browser Network panel if a request fails.

Use non-sensitive test records while validating the application.

## API overview

The API is versioned under `/api/v1`.

| Area | Routes |
|---|---|
| Health | `GET /health` |
| Configuration | `GET /api/v1/config` |
| Drones | `/api/v1/drones` |
| Batteries | `/api/v1/batteries` |
| Missions | `/api/v1/missions` |
| Flights | `/api/v1/flights` |
| Maintenance | `/api/v1/maintenance` |
| Battery history | `GET /api/v1/batteries/{battery_id}/history` |
| Cancel a mission | `POST /api/v1/missions/{mission_id}/cancel` |
| Complete maintenance | `POST /api/v1/maintenance/{item_id}/complete` |
| Cancel maintenance | `POST /api/v1/maintenance/{item_id}/cancel` |
| Dashboard analytics | `GET /api/v1/analytics/dashboard` |
| Analytics KPIs | `GET /api/v1/analytics/kpis` |
| Mission analytics | `GET /api/v1/analytics/missions` |
| Flight analytics | `GET /api/v1/analytics/flights` |
| Battery analytics | `GET /api/v1/analytics/batteries` |
| Maintenance analytics | `GET /api/v1/analytics/maintenance` |
| Trends | `GET /api/v1/analytics/trends` |

For exact request schemas and response examples, run the backend and visit <http://127.0.0.1:8000/docs>. The interactive API documentation is the source of truth if an endpoint's details differ from this overview.

## Firestore collections

The application uses these collection names:

- `drones`
- `batteries`
- `missions`
- `flights`
- `maintenance`
- `battery_history`

The application may create documents as records are added. Review `docs/DATA_MODEL.md` and the API schemas before manually editing documents or writing external integrations.

## Configuration notes

- The backend uses the Firebase Admin SDK and service-account credentials.
- The frontend uses a configurable API base URL in `frontend/assets/app.js`.
- CORS is configured using `FRONTEND_ORIGINS`.
- Bootstrap, Bootstrap Icons, and Plotly are loaded from CDNs.
- There is deliberately no login, registration, password reset, Firebase Authentication, or API-token mechanism.
- The Settings page is not included.

## Troubleshooting

### The frontend says “Failed to fetch”

- Confirm the backend terminal is still running.
- Visit <http://127.0.0.1:8000/health>.
- Confirm the API base URL in `frontend/assets/app.js` is `http://127.0.0.1:8000/api/v1`.
- Confirm the frontend's origin is listed in `FRONTEND_ORIGINS` in `.env`.
- Restart the backend after changing `.env`.

### Data endpoints return HTTP 503

- Confirm `firebase-service-account.json` exists in the project root.
- Confirm `FIREBASE_CREDENTIALS_PATH` and `FIREBASE_PROJECT_ID` in `.env` are correct.
- Confirm the service account belongs to the intended Firebase project and has appropriate access.
- Read the `/health` response and backend terminal output for diagnostics.
- Confirm Firestore has been enabled for the project.

### The page loads but charts or icons are missing

The frontend uses external CDNs. Check your internet connection and the browser's developer console for blocked or failed asset requests.

### Changes are not saved

- Inspect the browser Network panel for failed API requests.
- Check the backend terminal for validation or database errors.
- Confirm Firestore readiness at `/health`.
- Verify that the UI is using the correct API base URL.

### PowerShell cannot activate `.venv`

Use a terminal/session allowed by your device policy, or invoke the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

### Port 8000 or 5500 is already in use

Stop the process using the port or choose another port. If you change the frontend port, update `FRONTEND_ORIGINS` in `.env` to match it exactly.

## Security and deployment checklist

Before deploying or sharing the application:

- [ ] Do not commit `.env` or `firebase-service-account.json`.
- [ ] Review `git status` and staged files before every commit.
- [ ] Do not place service-account credentials in frontend files.
- [ ] Do not expose the unauthenticated API publicly.
- [ ] Add an appropriate access-control layer before public deployment.
- [ ] Configure production CORS origins explicitly; do not use permissive origins as a security substitute.
- [ ] Use HTTPS for public traffic.
- [ ] Set secrets through the deployment platform's secret/environment-variable settings.
- [ ] Test against a separate development Firestore project before touching production data.
- [ ] Verify CRUD operations and analytics in a browser after deployment.
- [ ] Review Firestore IAM permissions and application logging.

A static frontend host alone cannot securely host the Python API or protect Firebase Admin credentials. The frontend and backend need separate hosting/configuration unless the chosen platform supports both workloads. Do not deploy this unauthenticated backend publicly in its current state.

## Known limitations

- Authentication and authorization are intentionally absent.
- Automated tests do not establish live Firestore connectivity or full end-to-end browser correctness.
- Frontend CDN assets require internet access.
- Production hosting, access control, and operational monitoring must be configured separately.
- Review `TEST_REPORT.md` for the checks recorded for this package.