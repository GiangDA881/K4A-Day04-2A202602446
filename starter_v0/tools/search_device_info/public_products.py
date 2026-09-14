"""Reviewed public names only, never populated from user or tool output.

CONFLICT NOTE (B): extend products/aliases here when adding Tavily support.
Do not build this allowlist dynamically from internal inventory.
"""
PUBLIC_PRODUCTS = {
    "Lenovo": ("ThinkPad T14", "ThinkPad T14 Gen 4", "ThinkPad P1 Gen 6"),
    "Dell": ("Dell Latitude 7440", "OptiPlex 7010 Plus"),
    "HP": ("HP EliteDesk 800 G9", "Color LaserJet Enterprise M555dn"),
    "Apple": ("MacBook Pro 14-inch M3", "iPhone 15"),
    "Logitech": ("Rally Bar",),
}
MANUFACTURER_ALIASES = {"hewlett-packard": "HP", "hewlett packard": "HP"}
MODEL_ALIASES = {("Dell", "latitude 7440"): "Dell Latitude 7440",
                 ("HP", "elitedesk 800 g9"): "HP EliteDesk 800 G9"}


def public_product(manufacturer: str, model: str) -> tuple[str, str] | None:
    vendor_key = " ".join(manufacturer.split()).casefold()
    model_key = " ".join(model.split()).casefold()
    vendor = MANUFACTURER_ALIASES.get(vendor_key)
    if vendor is None:
        vendor = next((name for name in PUBLIC_PRODUCTS if name.casefold() == vendor_key), None)
    if vendor is None:
        return None
    canonical_model = MODEL_ALIASES.get((vendor, model_key))
    if canonical_model is None:
        canonical_model = next((name for name in PUBLIC_PRODUCTS[vendor]
                                if name.casefold() == model_key), None)
    return (vendor, canonical_model) if canonical_model else None
