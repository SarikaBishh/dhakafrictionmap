# Known limitations and unfinished work

- Only synthetic data; no real-data ingestion yet (see sources.md).
- Map is a schematic SVG, not Leaflet with tiles. Leaflet and tiles were dropped because the preview host blocks external stylesheets and images; they can be added when served from your own host.
- No PDF export. CSV is shown as copyable text in the page; add a download button when self-hosting.
- No Playwright/browser tests; the page's rendering and keyboard behaviour have not been tested in a browser by me.
- Python tests use `unittest` style (pytest also collects them). pytest itself could not be installed in the build environment, so they were run with `python -m unittest`.
- The Python and JavaScript scoring implementations are separate; a test cross-checks them on the sample data only.
- No deployment has been performed.
