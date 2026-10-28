# Subdomain Enumeration – Authorized Security Assessment Tool

A beginner-friendly Flask web application that performs **basic, DNS-based subdomain enumeration** using a small predefined list of common subdomain names.

This is an **educational cybersecurity prototype** for a college assignment. It is intended only for domains you own or have explicit permission to assess. It does not use paid APIs, brute-force wordlists, port scanning, or attack techniques.

---

## 1. Overview

During an authorized security assessment, analysts often start by identifying public hostnames related to a domain. This project demonstrates that idea in a simple way:

1. The user enters a plain domain such as `example.com`.
2. The application validates the input.
3. It builds 12 candidate hostnames (for example, `www.example.com` and `mail.example.com`).
4. It uses Python’s `socket` library to check whether each hostname resolves in DNS.
5. It displays **Found** or **Not Found**, plus the IP address when a lookup succeeds.

The interface includes Home, Results, How It Works, and Documentation pages, with authorization warnings and friendly error messages.

---

## 2. Problem Statement

Organizations often expose services on subdomains such as `www`, `mail`, `api`, or `staging`. Students learning cybersecurity need a **safe, easy-to-explain tool** that shows how DNS lookups can reveal whether those names exist.

Many professional enumeration tools are large, aggressive, or difficult to present in a classroom. This project solves that gap by providing:

- a small, fixed candidate list
- local DNS resolution only (no third-party enumeration APIs)
- clear validation and error handling
- in-app explanation pages suitable for a viva or demonstration

---

## 3. Objectives

- Demonstrate the concept of subdomain enumeration in an authorized, educational setting.
- Accept a domain name, validate it, and reject empty input, full URLs, and paths.
- Check a short list of common subdomain prefixes using DNS hostname resolution.
- Show results in a table with status and IP address.
- Explain the process in simple language on a How It Works page.
- Document the project, its limits, and authorized-use rules.
- Handle common errors without showing Python stack traces to the user.

---

## 4. Features Implemented

These features exist in the current codebase:

- **Home page** with title *Subdomain Enumeration*, subtitle *Authorized Security Assessment Prototype*, and an authorized-use warning.
- **Domain input form** (`example.com`) and an **Enumerate Subdomains** button.
- **Input validation** that rejects:
  - empty or whitespace-only input
  - URLs such as `http://example.com` or `https://example.com`
  - paths such as `example.com/test`
  - other invalid domain formats (spaces, ports/colons, names that do not match the domain pattern)
- **Safe enumeration** of exactly 12 prefixes:  
  `www`, `mail`, `api`, `dev`, `test`, `staging`, `portal`, `blog`, `shop`, `support`, `cdn`, `vpn`
- **DNS lookup** with `socket.getaddrinfo()`, a 3-second socket timeout, and handling for “not found”, timeout, and OS-level lookup failure.
- **Results page** showing:
  - domain tested
  - number of subdomains checked
  - number of subdomains found
  - table columns: Subdomain | Status | IP Address
  - note that results are prototype DNS results and should be verified
- **Session storage** of the last successful scan so the Results navigation item can show it again.
- **How It Works** page (what a subdomain is, what enumeration is, step-by-step flow).
- **Documentation** page (objective, features, technologies, how to run, testing notes, limitations, authorized use).
- **Custom 404 and 500 pages**.
- **Navigation** (Home, Results, How It Works, Documentation) and a footer authorization reminder.
- **Optional test script** `test_app.py` covering validation, DNS lookup, routes, and error messages.

The project does **not** implement brute-force wordlists, port scanning, vulnerability exploitation, authentication bypass, stealth/evasion, or cloud deployment.

---

## 5. Technologies and Libraries

| Item | Role in this project |
|---|---|
| Python 3 | Application language |
| Flask (`flask>=2.3.0`) | Web framework, routing, templates, sessions |
| Jinja2 (installed with Flask) | HTML templates |
| Werkzeug (installed with Flask) | HTTP exceptions used in error handling |
| HTML | Page structure |
| CSS (`static/style.css`) | Layout and styling |
| `socket` (Python standard library) | DNS / hostname resolution |
| `re` (Python standard library) | Domain format validation |
| `logging` (Python standard library) | Terminal logs for found/not found lookups |

**Declared dependency** (`requirements.txt`):

```
flask>=2.3.0
```

No paid APIs or external enumeration services are required. Lookups use the computer’s normal DNS resolver.

---

## 6. Project Folder Structure

```
project5_subdomain_enumeration/
├── app.py                 # Flask app: validation, DNS enumeration, routes
├── requirements.txt       # Python dependency (Flask)
├── README.md              # This file
├── test_app.py            # Optional automated checks
├── templates/
│   ├── base.html          # Shared header, navigation, footer
│   ├── index.html         # Home page and domain form
│   ├── results.html       # Enumeration results table
│   ├── how_it_works.html  # Process explanation
│   ├── documentation.html # In-app documentation
│   ├── 404.html           # Page not found
│   └── 500.html           # Server error
└── static/
    └── style.css          # Stylesheet
```

---

## 7. Installation and Setup

### Prerequisites

- Python 3 installed and available as `python` on the command line
- Internet access for DNS lookups (and for the first `pip` install of Flask)

### Steps

Open a terminal in this folder (`project5_subdomain_enumeration`).

Optional virtual environment (recommended):

```
python -m venv venv
```

Windows:

```
venv\Scripts\activate
```

macOS / Linux:

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## 8. How to Run the Project

From the `project5_subdomain_enumeration` folder:

```
python app.py
```

Then open a browser at:

**http://127.0.0.1:5000**

The application listens on `127.0.0.1` (localhost) on port `5000`, with Flask debug mode turned **off**.

### Optional tests

```
python test_app.py
```

This script checks domain validation, DNS lookup helpers, Flask routes, 404 handling, and selected error messages. It is not required to use the web app.

### Authorized demonstration input

Use only a domain you own or have permission to assess. For classroom explanation, a documentation-style name such as `example.com` is a typical demo input.

---

## 9. How the Code Works

### Main files

- **`app.py`** – all server logic: constants, validation, DNS checks, Flask routes, and error handlers.
- **`templates/`** – HTML pages that extend `base.html`.
- **`static/style.css`** – visual styling.
- **`test_app.py`** – command-line checks that import functions from `app.py`.

### Important functions in `app.py`

1. **`validate_domain(domain)`**  
   Cleans the input (trim, lowercase) and rejects empty values, URL schemes, paths, colons, spaces, and names that do not match a simple domain regex. On failure it returns a user-friendly message such as “Please enter a valid domain.”

2. **`dns_lookup(hostname)`**  
   Calls `socket.getaddrinfo()`.  
   - Success → list of unique IP addresses  
   - Hostname not found (`socket.gaierror`) → treated as not found  
   - Timeout or other `OSError` → recorded as timeout/failure  

3. **`enumerate_subdomains(domain)`**  
   For each prefix in `COMMON_SUBDOMAINS`, builds `prefix.domain` and looks it up.  
   Each row has `subdomain`, `status` (`Found` / `Not Found`), and `ip` (addresses or `-`).  
   If **all 12** lookups time out or fail at the OS level, it returns:  
   “DNS lookup could not be completed.”

### Request flow

```
User enters domain on Home (/)
        ↓
POST /enumerate
        ↓
validate_domain()
        ↓
enumerate_subdomains() → dns_lookup() for each candidate
        ↓
results.html
        ↓
Last results stored in the Flask session
        ↓
GET /results can show the same table again
```

### Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Home form |
| `/enumerate` | POST | Validate, enumerate, show results |
| `/results` | GET | Last results, or a “no results yet” message |
| `/how-it-works` | GET | Explanation page |
| `/documentation` | GET | Documentation page |

Unknown URLs render `404.html`. Unhandled exceptions render `500.html` instead of a Python traceback.

---

## 10. Screenshots

Screenshots are not stored in this repository. After you run the app, you can capture these pages and replace the placeholders.

### Home page

![Home page – domain input and authorized-use warning](screenshots/home.png)

*Add a screenshot of the Home page showing the form and security notice.*

### Results page

![Results page – subdomain table](screenshots/results.png)

*Add a screenshot of a completed scan with Found / Not Found rows.*

### How It Works page

![How It Works page](screenshots/how-it-works.png)

*Add a screenshot of the step-by-step explanation.*

### Documentation page

![Documentation page](screenshots/documentation.png)

*Add a screenshot of the in-app documentation and security notice.*

### 404 page

![404 page](screenshots/404.png)

*Optional: visit a non-existent URL such as http://127.0.0.1:5000/does-not-exist*

**Tip:** Create a `screenshots` folder in this project, save PNG files with the names above, and the images will appear in this README on GitHub.

---

## 11. Security Considerations and Limitations

### Authorized use

This tool is intended for **educational purposes and authorized security assessments only**. Do not test domains without permission. Only test domains that you own or have explicit permission to assess.

### Design choices that keep the prototype limited

- Only **12** common names are checked. Many real subdomains will not appear.
- Lookups are ordinary DNS queries, not stealth, evasion, or exploitation.
- There is no port scanning, login testing, or vulnerability scanning.
- Results are prototype DNS answers and **should be verified**.
- Wildcard DNS records can make many names appear as **Found** even when they are not distinct services.
- DNS answers can change over time.

### Application notes (from the current code)

- Flask runs on **localhost** (`127.0.0.1:5000`) with **debug mode disabled**, so users should not see Python stack traces in the browser.
- A **3-second** socket timeout reduces the chance of the app hanging on slow DNS.
- Invalid input is handled with messages on the Home page rather than crashing.
- The Flask `secret_key` is a fixed string in `app.py` for this college prototype. That is acceptable for local demo use, but it is not a production secret-management practice.
- The Results page stores the last scan in the **browser session cookie**. Closing the browser or using a new session will clear those results.

---

## 12. Future Improvements

Possible extensions (not implemented now):

- Load the candidate list from a small local text file so the list can be updated without editing `app.py`.
- Let the user export the results table as CSV for a lab report.
- Move the Flask secret key into an environment variable.
- Add per-lookup timeout that does not rely only on the global socket timeout.
- Show a clearer distinction on the results table when a single lookup times out versus “name does not exist”.
- Add screenshots to this README after a recorded demonstration.
- Add a simple “authorized domain” reminder on the results page before each scan (the warnings already exist on Home, Documentation, and the footer).

Any future change should remain **authorized-use only** and should not add aggressive scanning or attack features.

---

## License / Academic use

This repository is a college cybersecurity assignment prototype. Use it to learn and to demonstrate DNS-based enumeration on systems you are allowed to test.
