"""PocketBase API client for fast test-data setup & teardown.

The AUT proxies PocketBase under ``http://localhost:3000/hcgi/platform`` (and PocketBase
itself listens on ``:8090``). Using the API for arrange/cleanup is far faster and less
flaky than driving the UI.

To be implemented later:
  - auth as a user (``users`` collection) via authWithPassword
  - create/cleanup throwaway test users, cart items, orders, reviews
  - decode/encode the packed fields (see ``src/data/encoders.py``)

NOTE: customer-facing scope only — no admin-collection operations.
"""

# TODO: implement PocketBaseClient (httpx/requests) for setup/teardown helpers.
