"""Playwright route-interception mocks for third-party services.

External calls to stub for deterministic customer-facing tests:
  - Web3Forms  (api.web3forms.com)   -> order + contact email submissions
  - ipapi.co                          -> geo/country detection (pins currency)
  - open.er-api.com                   -> FX rates (pins displayed prices)

To be implemented later as opt-in fixtures toggled per test via markers.
"""

# TODO: implement mock_web3forms(), mock_geo(), mock_fx() route handlers.
