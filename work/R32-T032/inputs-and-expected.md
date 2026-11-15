# R32-T032 — Input and Expected Output

## Source contract

- Line 4: URL identifies the page requested.
- Line 5: `requests.get(URL)` fetches the page.
- Line 7: response content is parsed as HTML.
- Line 8: scraper searches for `ResultsContainer`.
- Lines 10–11: only headings containing "python" (case-insensitive) are selected.
- Lines 14–16: each matching heading is mapped to its card using three parent levels.
- Lines 19–26: title, company, location and the second link are printed.

## Public behavior

The script has no function arguments or return value. It fetches a webpage, parses it, and prints matching job details. It does not mutate local data. Its external dependency is an HTTP request through `requests.get`.

## Test cases

### 1. Empty boundary
Input: `<div id="ResultsContainer"></div>`

Expected output: empty string.

Reason: the container exists but contains no matching headings.

### 2. Smallest tested valid job
Input: one ResultsContainer containing one Python heading, its three-level card structure, title, company, location, and two links.

Expected output:
Python Developer
Acme
Remote
Apply here: /apply

Reason: one matching job is selected and its fields are printed.

### 3. Ordinary filtering case
Input: one mixed-case Python heading and one Java heading, each inside a job card.

Expected output:
pYtHoN Engineer
Example Co
London
Apply here: /python-apply

Reason: matching is case-insensitive; the Java heading is excluded.

## Boundary classification

| Case | Classification | Evidence |
|---|---|---|
| Existing empty ResultsContainer | Supported boundary | Lines 8–11 |
| Matching Python heading with expected card structure | Supported interior | Lines 10–24 |
| Mixed-case Python heading | Supported interior | Line 11 |
| Missing ResultsContainer or malformed card fields | Undefined by source | Lines 8–25; no explicit validation |

No exception behavior is asserted for undefined inputs.
