"""
app.py - Subdomain Enumeration Tool
=====================================
A beginner-friendly Flask web application that demonstrates
basic subdomain enumeration using DNS resolution.

EDUCATIONAL PURPOSE ONLY.
Only test domains you own or have explicit permission to assess.
"""

import logging
import re
import socket

from flask import Flask, render_template, request, session
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.secret_key = "college-project5-educational-only"
app.config["PROPAGATE_EXCEPTIONS"] = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# Small, predefined list of common subdomain prefixes.
# This is NOT a brute-force tool.
COMMON_SUBDOMAINS = [
    "www",
    "mail",
    "api",
    "dev",
    "test",
    "staging",
    "portal",
    "blog",
    "shop",
    "support",
    "cdn",
    "vpn",
]

# Prevent the app from hanging on slow DNS lookups
DNS_TIMEOUT = 3


def validate_domain(domain: str):
    """
    Validate that the input looks like a plain domain name (e.g. example.com).

    Returns:
        (cleaned_domain, None)  if valid
        (None, error_message)   if invalid
    """
    if domain is None:
        return None, "Please enter a valid domain."

    domain = domain.strip().lower()

    if not domain:
        return None, "Please enter a valid domain."

    if "://" in domain or domain.startswith("http://") or domain.startswith("https://"):
        return None, (
            "Please enter a valid domain. "
            "Do not include http:// or https://. Example: example.com"
        )

    if "/" in domain or "\\" in domain:
        return None, (
            "Please enter a valid domain. "
            "Do not include a path such as example.com/test."
        )

    if ":" in domain:
        return None, "Please enter a valid domain."

    if " " in domain:
        return None, "Please enter a valid domain."

    # Labels separated by dots; TLD at least 2 letters
    pattern = r"^(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$"
    if not re.match(pattern, domain):
        return None, "Please enter a valid domain."

    return domain, None


def dns_lookup(hostname: str):
    """
    Resolve a hostname to IP addresses.

    Returns:
        (ips, error_type)
        ips is a list of IP strings, or None if not found / failed
        error_type is None, "timeout", or "failure"
    """
    try:
        results = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
        ips = list(dict.fromkeys(r[4][0] for r in results))
        if ips:
            return ips, None
        return None, None
    except socket.timeout:
        logger.warning("DNS timeout for %s", hostname)
        return None, "timeout"
    except socket.gaierror:
        return None, None
    except OSError as exc:
        logger.warning("DNS lookup failure for %s: %s", hostname, exc)
        return None, "failure"


def enumerate_subdomains(domain: str):
    """
    Check each candidate prefix against the given domain via DNS.

    Returns:
        (results, dns_error)
        results is a list of row dicts
        dns_error is a user-facing message if lookups could not be completed
    """
    results = []
    timeout_or_failure_count = 0

    for prefix in COMMON_SUBDOMAINS:
        hostname = f"{prefix}.{domain}"
        ips, error_type = dns_lookup(hostname)

        if error_type in ("timeout", "failure"):
            timeout_or_failure_count += 1

        if ips:
            results.append(
                {
                    "subdomain": hostname,
                    "status": "Found",
                    "ip": ", ".join(ips),
                }
            )
            logger.info("Found: %s -> %s", hostname, ips)
        else:
            results.append(
                {
                    "subdomain": hostname,
                    "status": "Not Found",
                    "ip": "-",
                }
            )
            logger.info("Not found: %s", hostname)

    dns_error = None
    if timeout_or_failure_count == len(COMMON_SUBDOMAINS):
        dns_error = "DNS lookup could not be completed."

    return results, dns_error


@app.route("/", methods=["GET"])
def index():
    """Home page with the domain input form."""
    return render_template("index.html")


@app.route("/enumerate", methods=["POST"])
def enumerate_route():
    """Validate input, run DNS enumeration, and show results."""
    raw_domain = request.form.get("domain", "")

    domain, error = validate_domain(raw_domain)
    if error:
        return render_template("index.html", error=error, previous_input=raw_domain)

    try:
        socket.setdefaulttimeout(DNS_TIMEOUT)
        results, dns_error = enumerate_subdomains(domain)
    except Exception as exc:
        logger.error("Unexpected error during enumeration: %s", exc)
        return render_template(
            "index.html",
            error="Something went wrong. Please try again.",
            previous_input=raw_domain,
        )

    if dns_error:
        return render_template(
            "index.html",
            error=dns_error,
            previous_input=raw_domain,
        )

    total_checked = len(results)
    total_found = sum(1 for row in results if row["status"] == "Found")

    session["last_results"] = {
        "domain": domain,
        "results": results,
        "total_checked": total_checked,
        "total_found": total_found,
    }

    return render_template(
        "results.html",
        domain=domain,
        results=results,
        total_checked=total_checked,
        total_found=total_found,
        has_results=True,
    )


@app.route("/results")
def results_page():
    """Show the last enumeration results, or a prompt if none exist yet."""
    last = session.get("last_results")
    if not last:
        return render_template("results.html", has_results=False)

    return render_template(
        "results.html",
        domain=last["domain"],
        results=last["results"],
        total_checked=last["total_checked"],
        total_found=last["total_found"],
        has_results=True,
    )


@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


@app.route("/documentation")
def documentation():
    return render_template("documentation.html")


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error("500 error: %s", e)
    return render_template("500.html"), 500


@app.errorhandler(Exception)
def unexpected_error(e):
    if isinstance(e, HTTPException):
        return e
    logger.error("Unhandled error: %s", e)
    return render_template("500.html"), 500


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Subdomain Enumeration - Educational Prototype")
    print("  Open: http://127.0.0.1:5000")
    print("  Only test domains you own or have permission to assess.")
    print("=" * 60 + "\n")
    # debug=False so users never see Python stack traces
    app.run(debug=False, host="127.0.0.1", port=5000)
