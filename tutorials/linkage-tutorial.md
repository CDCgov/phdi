# Tutorials: The Linkage Module

This guide serves as a tutorial overview of the functionality available in both `linkage.py` and `fhir.linkage.py`. It will cover concepts such as data type basics, imports, and common uses invocations.

## The Basics: How it links

The linkage module adds a patient identifier to each patient record in a bundle. If two hash strings are the same, that means that the two patient records are referring to the same patient. The hash string generation is a straightforward name and address combination. 


## Common Uses
Listed below are several example use cases for employing the geospatial module.

### Geocode Address In A String
Suppose a data element has an address field in which the entire address occurs in a string, e.g.

```
location = "1234 Mulholland Dr. NW Cincinnati OH 43897"
```

To precisely geocode this address, using, say, the SmartyStreets geocoder, we would write:

```
from phdi.geospatial.smarty import SmartyGeocodeClient

location = "1234 Mulholland Dr. NW Cincinnati OH 43897"
smarty_coder = SmartyGeocoderClient(YOUR_AUTH_ID, YOUR_AUTH_TOKEN, YOUR_LICENSES)
geo_result = smarty_coder.geocode_from_str(location)

print(geo_result)
    >>> GeocodeResult(
    >>>    line=["1234 Mulholland Drive], 
    >>>    city="Cincinnati",
    >>>    state="Ohio"
    >>>    postal_code="43897"
    >>>    ...
    >>> )
```

Here, the parameters in the `SmartyGeocodeClient` constructor correspond to authentication and authorization variables related to your SmartyStreets subscription. So, `YOUR_AUTH_ID` is your authorization ID to use the service and `YOUR_AUTH_TOKEN` is an access token generated to communicate with the API. The `licenses` parameter does not need to be modified if you wish to perform a search with the default license agreement (e.g. `"us-standard-cloud"`) but can be changed to a list of other license types if you wish to customize the search.

### Geocode Address From A Dictionary
Let's take the example above and now suppose that the address we wish to work with is contained in a dictionary. Because of the standardization of our Geocode Clients and `GeocodeResult`, the code is extremely similar:

```
from phdi.geospatial.smarty import SmartyGeocodeClient

# We have an address dict this time with fields distributed amongst keys
location = {
    street = "9876 Amesbury Circle",
    apartment = "221"
    city = "Green Bay"
    state = "WI"
    postal_code = "08567"
}

# We can still create and run the geocoder the same way
smarty_coder = SmartyGeocodeClient(YOUR_AUTH_ID, YOUR_AUTH_TOKEN, YOUR_LICENSES)
geo_result = smarty_coder.geocode_from_dict(location)

print(geo_result)
```

When providing input to `.geocode_from_dict()`, it is desirable to pass in as many fields as possible to ensure a high quality geocoding match. However, none of the fields are required so that you can pass in any fields you do have. For best results, we recommend providing at least `street`, `city`, and `state`. In the example above, we could have had just as successful a geocode query if we had omitted `apartment` and `postal_code` from the address.

### Geocode A Patient Resource
Now let's suppose the data we're processing is FHIR-formatted (i.e. it is a JSON dictionary with field structure and names corresponding to FHIR labels). We want to geocode the home address of an incoming patient resource. Despite the change in input type, the resulting code doesn't change all that much, since we have a convenience wrapper around the same core functionality. 

```
from phdi.fhir.geospatial.smarty import SmartyFhirGeocodeClient

# Our data element is a FHIR-formatted patient resource
 patient = {
    "id": "some-uuid",
    "name": [
        {
            "family": "doe",
            "given": ["John ", " Danger "],
            "use": "official"
        }
    ],
    "birthDate": "1983-02-01",
    "gender": "male",
    "address": [
        {
            "line": [
                "123 Fake St",
                "Unit #F"
            ],
            "city": "Faketon",
            "state": "NY",
            "postalCode": "10001-0001",
            "country": "USA",
            "use": "home"
        }
    ],
}

# Still, we can geocode it in much the same way
fhir_coder = SmartyFhirGeocodeClient(YOUR_AUTH_ID, YOUR_AUTH_TOKEN, YOUR_LICENSES)
patient = fhir_coder.geocode_resource(patient, overwrite = True)
```

The code above will geocode the single address present in the `patient` resource's address field. We could further modify this example in several ways, none of which would break the functionality of the existing code:

- We could add additional addresses to the `patient`, and the code above would geocode them all
- We could set `overwrite = False` in the `.geocode_resource` call; this would create a new, deep copy of the original patient data and store the new geocoded address information there

Regardless of whether we overwrite the input data or not, we can verify that the new geocoded information is present simply by checking whether latitude and longitude are now specified, since they weren't on the input `patient` resource:

```
lat_and_long_both_present = False

# Access the extension property of the first address in our patient,
# since that's the one we geocoded
for extension in patient.get("address", [])[0]["extension"]:

    if "geolocation" in extension.get("url"):
        lat_dict = next(
            x for x in extension.get("extension") if x.get("url") == "latitude"
        )
        lng_dict = next(
            x for x in extension.get("extension") if x.get("url") == "longitude"
        )
        lat_and_long_both_present = (
            lat_dict.get("valueDecimal") == 40.032
            and lng_dict.get("valueDecimal") == -64.987
        )

print(lat_and_long_both_present)
>>> True
```

### Geocode a FHIR Bundle Containing Multiple Patients
Finally, let's consider a scenario in which we want to geocode an entire bundle of resources. As has been the case, the structure of our code isn't really going to change; we'll just need to invoke a different `.geocode_from` method.

```
# Full definition omitted for brevity, but `bundle` is a list of JSON
# objects having FHIR format; in this case, a list of patients
bundle = [
    {
        "id": "uid-1"
        "name": [ ... ]
        ...
    },
    {
        "id": "uid-2"
        "name": [ ... ]
        ...
    },
    ...
]

fhir_coder = SmartyFhirGeocodeClient(YOUR_AUTH_ID, YOUR_AUTH_TOKEN, YOUR_LICENSES)
patient = fhir_coder.geocode_bundle(bundle, overwrite = True)
```