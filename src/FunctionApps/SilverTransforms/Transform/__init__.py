import logging

import azure.functions as func


def transform_name(raw: str) -> str:
    """trim spaces, capitalize, etc"""
    return raw.upper()


def transform_phone(raw: str) -> str:
    """Make sure it's 10 digits, remove everything else"""
    pass


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Load ndjson from blob store into List[Dict]
    # Transform each record
    #   Name standardization
    #   Phone number standardization
    #   Maybe date standardization
    #   Geocoding home address (to lat/lng and canonical address)
    # Write the records out to a different blob store (as ndjson)
    return func.HttpResponse("ok")
