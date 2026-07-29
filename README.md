# python-world

A deliberately outdated one-page Flask app, for testing dependency scanners and
practising upgrade/remediation work.

## Run

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. The page works offline; only the HTTP section
needs network.

## The four packages

| Package | Pinned | Role | Latest |
|---|---|---|---|
| Flask | 2.2.2 | web server, routing, template rendering | 3.1.3 |
| requests | 2.25.1 | HTTP client (the `axios` here) | 2.34.2 |
| arrow | 1.2.3 | dates + `humanize()` (the `moment` here) | 1.4.0 |
| Jinja2 | 3.1.2 | templating, used directly in `app.py` | 3.1.6 |

Transitives (`Werkzeug`, `urllib3`, `certifi`, `idna`, ...) are pinned old too,
so a scan produces findings beyond the direct four.

## Known CVEs

Each pin below is flagged by `pip-audit`, Dependabot, Trivy, Snyk, etc.

| Package | CVE | Note |
|---|---|---|
| Flask 2.2.2 | CVE-2023-30861 | session cookie cached by a proxy, served to another client |
| requests 2.25.1 | CVE-2023-32681 | `Proxy-Authorization` leaked across an HTTPS redirect |
| requests 2.25.1 | CVE-2024-35195 | `verify=False` on one call disables verification session-wide |
| Jinja2 3.1.2 | CVE-2024-22195 | XSS via the `xmlattr` filter |
| Jinja2 3.1.2 | CVE-2024-34064 | `xmlattr` accepts keys containing `/` |
| Werkzeug 2.2.2 | CVE-2023-25577 | multipart DoS via many parts |
| Werkzeug 2.2.2 | CVE-2023-46136 | DoS via a large file in a multipart body |
| Werkzeug 2.2.2 | CVE-2024-34069 | debugger PIN bypass &rarr; RCE (needs `debug=True`) |
| urllib3 1.26.5 | CVE-2023-43804 | `Cookie` header leaked across cross-origin redirect |
| urllib3 1.26.5 | CVE-2023-45803 | request body retained on a 303 redirect |
| certifi 2020.12.5 | CVE-2023-37920 | removed-but-trusted e-Tugra root CA |
| idna 2.10 | CVE-2024-3651 | ReDoS in `idna.encode()` |
| click 8.1.3 | PYSEC-2026-2132 | fixed in 8.3.3 |

`arrow` 1.2.3 is the only pin with no findings — the old-but-clean control, so
you can tell "outdated" apart from "vulnerable".

## Scan it

```powershell
pip install pip-audit
pip-audit -r requirements.txt --no-deps
```

Verified 2026-07-29 against the PyPI advisory DB: **42 vulnerabilities across 8
packages** (flask, requests, urllib3, idna, jinja2, werkzeug, certifi, click).
`pip-audit` exits non-zero when it finds anything, which is correct here.

## Remediating

Upgrading is not just bumping numbers. Expect these:

- **Flask 2.2 &rarr; 3.x** drops `before_first_request` and needs
  `Werkzeug` on the matching major.
- **requests 2.25 &rarr; 2.32** drops `chardet` for `charset-normalizer` and
  requires `idna>=3`, so the `idna==2.10` pin must go with it.
- **arrow 1.2.3 &rarr; 1.4.0** requires `types-python-dateutil`.
- `MarkupSafe`, `itsdangerous`, `six` are pinned only to keep the install
  reproducible; they carry no findings.

A clean upgrade target to diff against:

```
Flask==3.1.3
requests==2.34.2
arrow==1.4.0
Jinja2==3.1.6
```

Drop every transitive pin and let pip resolve them &mdash; the old
`urllib3`/`idna`/`certifi`/`click` pins are what generate most of the 42
findings, and leaving any of them behind blocks the fix.
