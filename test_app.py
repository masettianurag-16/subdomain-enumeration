"""
test_app.py - Automated tests for Project 5
Run with: python test_app.py
"""
import socket as socket_mod
import sys
from unittest.mock import patch

sys.path.insert(0, ".")
from app import app, dns_lookup, enumerate_subdomains, validate_domain

PASS = "PASS"
FAIL = "FAIL"
failed = 0


def mark(ok):
    global failed
    if not ok:
        failed += 1
    return PASS if ok else FAIL


print("=" * 55)
print("  AUTOMATED TESTS - Subdomain Enumeration Prototype")
print("=" * 55)

print("\n--- Validation Tests ---")
validation_cases = [
    ("", None, "Empty input"),
    ("  ", None, "Whitespace only"),
    ("http://example.com", None, "URL with http://"),
    ("https://example.com", None, "URL with https://"),
    ("example.com/test", None, "Path after domain"),
    ("not_a_domain", None, "Invalid domain"),
    ("example.com", "example.com", "Valid plain domain"),
    ("  Example.COM  ", "example.com", "Whitespace + uppercase"),
]

for raw, expected, label in validation_cases:
    domain, err = validate_domain(raw)
    ok = domain == expected
    print(f"  [{mark(ok)}] {label}")
    if not ok:
        print(f"         Expected={expected!r}  Got={domain!r}  err={err!r}")

print("\n--- DNS Lookup Tests ---")
ips, err = dns_lookup("example.com")
ok_resolve = ips is not None and len(ips) > 0
print(f"  [{mark(ok_resolve)}] example.com resolves -> {ips}")

bogus_ips, bogus_err = dns_lookup("this-totally-bogus-999xyz.invalid")
ok_bogus = bogus_ips is None
print(f"  [{mark(ok_bogus)}] Bogus hostname returns None -> {bogus_ips}")

print("\n--- DNS Timeout / Failure Tests ---")
with patch("app.socket.getaddrinfo", side_effect=socket_mod.timeout("timed out")):
    results, dns_error = enumerate_subdomains("example.com")
ok_timeout = dns_error == "DNS lookup could not be completed." and len(results) == 12
print(f"  [{mark(ok_timeout)}] All lookups timing out shows DNS error")

print("\n--- Flask Route Tests ---")
app.config["TESTING"] = True
client = app.test_client()


def check(method, path, data=None, expected=200, label=""):
    if method == "GET":
        response = client.get(path)
    else:
        response = client.post(path, data=data, follow_redirects=True)
    ok = response.status_code == expected
    print(f"  [{mark(ok)}] {label} (HTTP {response.status_code})")
    return response


check("GET", "/", label="Home page loads")
check("GET", "/results", label="Results page loads without prior scan")
check("GET", "/how-it-works", label="How It Works page loads")
check("GET", "/documentation", label="Documentation page loads")
response = check("GET", "/nonexistent-page", expected=404, label="Unknown route returns 404")
print(f"  [{mark(b'Page Not Found' in response.data)}] 404 page content")

response = check("POST", "/enumerate", data={"domain": ""}, label="Empty domain")
print(f"  [{mark(b'Please enter a valid domain.' in response.data)}] Empty domain error message")

response = check("POST", "/enumerate", data={"domain": "not_valid"}, label="Invalid domain")
print(f"  [{mark(b'Please enter a valid domain.' in response.data)}] Invalid domain error message")

response = check("POST", "/enumerate", data={"domain": "http://example.com"}, label="URL input")
print(f"  [{mark(b'Please enter a valid domain.' in response.data)}] URL error message")

response = check("POST", "/enumerate", data={"domain": "example.com/test"}, label="Path input")
print(f"  [{mark(b'Please enter a valid domain.' in response.data)}] Path error message")

response = check("POST", "/enumerate", data={"domain": "example.com"}, label="Valid domain returns results")
ok = (
    b"example.com" in response.data
    and b"Subdomains Checked" in response.data
    and b"www.example.com" in response.data
)
print(f"  [{mark(ok)}] Results page contains expected content")

home_has_notice = b"This tool is intended for educational purposes" in client.get("/").data
docs_has_notice = b"This tool is intended for educational purposes" in client.get("/documentation").data
print(f"  [{mark(home_has_notice)}] Home security notice")
print(f"  [{mark(docs_has_notice)}] Documentation security notice")

response = check(
    "POST",
    "/enumerate",
    data={"domain": "localhost.invalid"},
    label="Non-resolving domain does not crash",
)
print(f"  [{mark(response.status_code == 200)}] No crash on non-resolving domain")

with patch("app.enumerate_subdomains", side_effect=RuntimeError("boom")):
    response = client.post("/enumerate", data={"domain": "example.com"})
print(
    f"  [{mark(b'Something went wrong. Please try again.' in response.data)}] "
    "Unexpected error message"
)

with patch("app.socket.getaddrinfo", side_effect=socket_mod.timeout("timed out")):
    response = client.post("/enumerate", data={"domain": "example.com"})
print(
    f"  [{mark(b'DNS lookup could not be completed.' in response.data)}] "
    "DNS timeout message on form"
)

print("\n" + "=" * 55)
if failed:
    print(f"  Tests finished with {failed} failure(s).")
    sys.exit(1)
print("  All tests passed.")
print("=" * 55)
