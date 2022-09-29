# Tutorials: The Geospatial Module

This guide serves as a tutorial overview of the functionality available in both `phdi.geospatial` and `phdi.fhir.geospatial`. It will cover concepts such as data type basics, imports, and common uses invocations.

## The Basics: Clients and Results
The basic data structures used by the geospatial model are a `BaseGeocodeClient` and a `GeocodeResult`. The former is an abstract base class (see https://docs.python.org/3/library/abc.html for more details) that provides vendor-agnostic function skeletons for use on raw data (e.g. strings and dictionaries); the latter is a dataclass (see https://docs.python.org/3/library/dataclasses.html) designed to hold address field information in a standardized fashion. The `fhir` wrapper for the geospatial module also provides a `BaseFhirGeocodeClient`, which is an abstract class that behaves like `BaseGeocodeClient` but which is designed to work with FHIR-formatted data. For clarity, we'll use `BaseGeocodeClient` to refer to implementations that deal with raw data, `BaseFhirGeocodeClient` to refer to implementations that deal with FHIR-formatted data, and "Geocode Clients" to refer the set of both types.

The Geocode Clients have the following important methods:
```
BaseGeocodeClient:
    geocode_from_str()
        '''
        Geocode an address given as a string
        '''

    geocode_from_dict()
        '''
        Geocode an address given as a dictionary (does not need to be FHIR-formatted)
        '''

BaseFhirGeocodeClient:
    geocode_resource()
        '''
        Geocode one or more addresses contained in a given FHIR resource
        '''

    geocode_bundle()
        '''
        Geocode addresses in all resources in a given FHIR bundle
        '''
```

Because the abstract base classes define these methods, all vendor-specific Geocode Clients will implement and have access to the data-processing methods of their parent (FHIR data or raw data).

A `GeocodeResult` has the following attributes:

```
line: List[str]
city: str
state: str
postal_code: str
county_fips: str
lat: float
lng: float
district: Optional[str] = None
country: Optional[str] = None
county_name: Optional[str] = None
precision: Optional[str] = None
geoid: Optional[str] = None
census_tract: Optional[str] = None
census_block: Optional[str] = None
```

All attributes which are `Optional`-typed may or may not be included in the results of a specific geocoding search, depending on whether a vendor implements returning data of that type. `district`, `country`, and `precision` are available only through the Smarty API; `geoid`, `census_tract`, and `census_block` are only available through the Census API.

## Importing
Using the geospatial module's functionality begins with simple imports. The Geocode Client abstract classes and `GeocodeResult` likely do not need to be imported (see the common uses section below), but can be used directly from the relevant package:

```
from phdi.geospatial.core import BaseGeocodeClient, GeocodeResult
from phdi.fhir.geospatial.core import BaseFhirGeocodeClient
```

Of more relevance are the vendor-specific implementations of the Geocode Client classes, which can be imported from the specific `.py` file of the desired vendor. For example, to import a geocoder that uses the SmartyStreets API:

```
from phdi.geospatial.smarty import SmartyGeocodeClient
from phdi.fhir.geospatial.smarty import SmartyFhirGeocodeClient
```

## Common Uses
Listed below are several example use cases for employing the geospatial module.

### Geocode Address In A String
Suppose a data element has an address field in which the entire address occurs in a string, e.g.

```python
location = "5905 Wilshire Blvd Los Angeles CA 90036"
```

To precisely geocode this address, using, say, the SmartyStreets geocoder, we would write:

```python
from phdi.geospatial.smarty import SmartyGeocodeClient

location = "5905 Wilshire Blvd Los Angeles CA 90036"
smarty_coder = SmartyGeocoderClient(YOUR_AUTH_ID, YOUR_AUTH_TOKEN, YOUR_LICENSES)
geo_result = smarty_coder.geocode_from_str(location)

print(geo_result)
    >>> GeocodeResult(
    >>>    line=["5905 Wilshire Blvd"], 
    >>>    city="Los Angeles",
    >>>    state="CA"
    >>>    postal_code="90036"
    >>>    ...
    >>> )
```

Here, the parameters in the `SmartyGeocodeClient` constructor correspond to authentication and authorization variables related to your SmartyStreets subscription. So, `YOUR_AUTH_ID` is your authorization ID to use the service and `YOUR_AUTH_TOKEN` is an access token generated to communicate with the API. The `licenses` parameter does not need to be modified if you wish to perform a search with the default license agreement (e.g. `"us-standard-cloud"`) but can be changed to a list of other license types if you wish to customize the search.

To precisely geocode this address, using, say, the Census geocoder, we would write:

```python
from phdi.geospatial.census import CensusGeocodeClient

location = "5905 Wilshire Blvd Los Angeles CA 90036"
geo_result = census_coder.geocode_from_str(location)

print(geo_result)
    >>> GeocodeResult(
    >>>    line=["5905 Wilshire Blvd"], 
    >>>    city="Los Angeles",
    >>>    state="CA"
    >>>    postal_code="90036"
    >>>    geoid="060372151011004"
    >>>    census_tract="2151.01"
    >>>    census_block="1004"
    >>>    ...
    >>> )
```

### Geocode Address From A Dictionary
Let's take the example above and now suppose that the address we wish to work with is contained in a dictionary. Because of the standardization of our Geocode Clients and `GeocodeResult`, the code is extremely similar:

```python
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

```python
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

```python
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

```python
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