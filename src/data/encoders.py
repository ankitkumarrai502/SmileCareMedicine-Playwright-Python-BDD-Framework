"""Single source of truth for the AUT's packed-field encodings.

The SmileCareMedicine backend overloads several fields; tests must decode them rather
than hardcoding the quirk in every assertion:

  - product ``strength``      ->  ``strength || packaging || JSON(additionalCategories)``  (``||``)
  - review  ``userLocation``  ->  ``Name ||| Location``                                    (``|||``)
  - order   ``shippingAddress`` is a JSON TEXT blob holding ``status`` (pending ->
    confirmed -> shipped -> delivered), plus customer name/email/phone/actualAddress.

To be implemented later: decode_* / encode_* helpers reused by both data setup and asserts.
"""

# TODO: implement decode_strength, decode_review_location, decode_order_shipping (and encoders).
