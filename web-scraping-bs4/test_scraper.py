import contextlib
import io
import runpy
import unittest
from unittest.mock import patch


def run_scraper(html):
    response = type("Response", (), {"content": html.encode()})()
    output = io.StringIO()

    with patch("requests.get", return_value=response):
        with contextlib.redirect_stdout(output):
            runpy.run_path("web-scraping-bs4/scraper.py")

    return output.getvalue()


class ScraperTests(unittest.TestCase):
    # Source lines 8-11: ResultsContainer lookup and heading selection.
    def test_empty_results_container(self):
        html = '<div id="ResultsContainer"></div>'
        self.assertEqual(run_scraper(html), "")

    # Source lines 14-25: card structure, fields and second link.
    def test_minimal_valid_python_job(self):
        html = """
        <div id="ResultsContainer">
          <div>
            <div>
              <div>
                <h2 class="title">Python Developer</h2>
              </div>
            </div>
            <h3 class="company">Acme</h3>
            <p class="location">Remote</p>
            <a href="/details">Details</a>
            <a href="/apply">Apply</a>
          </div>
        </div>
        """
        expected = (
            "Python Developer\n"
            "Acme\n"
            "Remote\n"
            "Apply here: /apply\n\n"
        )
        self.assertEqual(run_scraper(html), expected)

    # Source line 11: case-insensitive Python heading filter.
    def test_case_insensitive_matching_and_non_python_exclusion(self):
        html = """
        <div id="ResultsContainer">
          <div>
            <div>
              <div>
                <h2 class="title">pYtHoN Engineer</h2>
              </div>
            </div>
            <h3 class="company">Example Co</h3>
            <p class="location">London</p>
            <a href="/details">Details</a>
            <a href="/python-apply">Apply</a>
          </div>
          <div>
            <div>
              <div>
                <h2 class="title">Java Developer</h2>
              </div>
            </div>
            <h3 class="company">Other Co</h3>
            <p class="location">Paris</p>
            <a href="/details">Details</a>
            <a href="/java-apply">Apply</a>
          </div>
        </div>
        """
        expected = (
            "pYtHoN Engineer\n"
            "Example Co\n"
            "London\n"
            "Apply here: /python-apply\n\n"
        )
        self.assertEqual(run_scraper(html), expected)


if __name__ == "__main__":
    unittest.main()
