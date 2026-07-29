"""python-world — a one-page Flask app built on deliberately outdated packages.

Exists so dependency scanners have something to flag and so upgrades have
something to break. Run it, don't ship it.

    python app.py   ->  http://127.0.0.1:5000
"""

import arrow
import requests
from flask import Flask, render_template, request
from jinja2 import Template

app = Flask(__name__)

# Public, no-auth endpoint. Kept small so the page stays fast.
API_URL = "https://api.github.com/repos/pallets/flask"

# Rendered with a bare jinja2.Template so Jinja2 is a direct dependency,
# not just something Flask happens to drag in.
SUMMARY = Template(
    "{{ name }} has {{ stars }} stars and was last pushed {{ pushed }}."
)


def fetch_repo(timeout=5):
    """Return a small dict about the repo, or an error string."""
    try:
        response = requests.get(API_URL, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        return None, str(exc)

    data = response.json()
    pushed = arrow.get(data["pushed_at"])
    return {
        "name": data["full_name"],
        "stars": f"{data['stargazers_count']:,}",
        "pushed": pushed.humanize(),
        "pushed_exact": pushed.format("YYYY-MM-DD HH:mm ZZ"),
        "language": data["language"],
    }, None


@app.route("/")
def index():
    now = arrow.now()
    repo, error = fetch_repo()

    return render_template(
        "index.html",
        now_iso=now.format("YYYY-MM-DD HH:mm:ss ZZ"),
        now_human=now.humanize(arrow.get("2020-01-01"), granularity="year"),
        weekday=now.format("dddd"),
        repo=repo,
        error=error,
        summary=SUMMARY.render(**repo) if repo else None,
        client=request.headers.get("User-Agent", "unknown"),
    )


if __name__ == "__main__":
    app.run(debug=True)
