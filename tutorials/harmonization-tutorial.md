# Tutorials: The Harmonization Module

This guide serves as a tutorial overview of the functionality available in both `phdi.harmonization` and `phdi.fhir.harmonization`. It will cover concepts such as data type basics, imports, and common uses invocations.

## Module Overview: What is Harmonization?
When we say "_harmonization_," we mean **the process of smoothing out, standardizing, and normalizing either data values or entries in a data structure**. Putting timestamps in a uniform structure, standardizing strings of text with cleaning rules, and identifying country information for ISO-formatted phone numbers are all examples that would leverage the harmonization module. Indeed, the purpose of the harmonization module as a whole is to streamline the process of cleaning data and putting it into a user-friendly format. Importantly, harmonization does _not_ deal with the conversion of data between types or structures (for example, converting HL7v2 data into a FHIR-formatted data structure); that functionality can be found in the `phdi.fhir.conversion` module. Let's take a look at the two broad categories of functionality available in this module and its FHIR wrapper.

## The Basics: Sanitizing HL7 and Standardizing Inputs
The harmonization modules broadly cover two main areas of functionality:

1. Cleaning, standardizing, and applying uniform formatting to fields, segments, and messages of raw HL7v2 data, and
2. Normalizing the values and formatting of raw string data (representing text such as a name or a phone number).

The HL7 functionality of harmonization can enable pre-processing of one or more messages for storage or possible conversion to FHIR, while the normalization functionality can operate on either raw data (text strings) or FHIR resources, as appropriate. Each of these functional areas relies on several additional operations under the hood, but the PHDI module structure enables their broad use without relying on lower-level functional details. 

## Importing
To get started with the harmonization module, simply make the relevant import statement, depending on whether you want to work with raw data or FHIR-formatted data:

```python
from phdi.harmonization import function_you_want_to_import          # used for raw data
from phdi.fhir.harmonization import fhir_wrapper_of_raw_function    # used for FHIR data
```

Below, we'll explore some of the more common functions you may want to use when harmonizing your data. It's worth noting that the functions which aren't defined in the `phdi.harmonization` and `phdi.fhir.harmonization` namespaces should very likely _not_ be imported (e.g., you shouldn't find yourself needing to write `from phdi.harmonization.hl7 import _clean_hl7_batch`). These "supporting files" simply contain helper functions used by the publicly-defined API functions exposed in the `__init__.py` files of each directory; the API functions you'll want to use already invoke these under the hood.

## Common Uses
Listed below are several example use cases for employing the harmonization module.

### Normalizing the Datetime Segments in an HL7 Message

Suppose we have an HL7 message with MSH and PID segments as follows:

```python
msg = ""
msg += "MSH|^~\&|WIR11.3.2^^|WIR^^||WIRPH^^|202005140100001234567890||VXU^V04|2020051411020600-0400|P^|2.4^^|||ER"
msg += "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^|2018080800000000000|M|||||||||||||||||||||"
```

Note the datetime fields in MSH[7] and MSH[10], as well as PID[8]. If we were to attempt downstream conversion, we could run into errors, as these datetime fields feature additional digits that, while holding some HL7 information, throw off the formatting for things like a FHIR converter. Let's use harmonization to clean them:

```python
from phdi.harmonization import standardize_hl7_datetimes

cleaned_msg = standardize_hl7_datetimes(msg)
print(cleaned_msg)

>>> "MSH|^~\\&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514010000||VXU^V04|2020051411020600-0400|P^|2.4^^|||ER"
>>> "PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^|20180808000000|M|||||||||||||||||||||"
>>> ...
```

We see that the datetime segments have now been truncated appropriately for downstream use (MSH[7] had 10 digits removed, MSH[10] had none removed as its time zone information was already compliant, and PID[8] had 5 digits removed).

### Processing a Batch of HL7 Messages
Suppose now that we have a file holding a batch of HL7 messages. Here, a "batch" corresponds to a batch file having the structure 

```
[FHS] (file header segment) {
    [BHS] (batch header segment) {
        [MSH (zero or more HL7 messages)
        ....
        ....
        ....]
    }
    [BTS] (batch trailer segment)
}
[FTS] (file trailer segment)
```

In practice, such a file might look like this:

```
FHS|^~&|WIR11.3.2|WIR|||20200514||1219144.update|||
BHS|^~&|WIR11.3.2|WIR|||20200514|||||
MSH|^~&|WIR11.3.2^^|WIR^^||WIRPH^^|20200514||VXU^V04|2020051411020600|P^|2.4^^|||ER
PID|||3054790^^^^SR^~^^^^PI^||ZTEST^PEDIARIX^^^^^^|HEPB^DTAP^^^^^^|20180808|M|||||||||||||||||||||
PD1|||||||||||02^^^^^|Y||||A
NK1|1||BRO^BROTHER^HL70063^^^^^|^^NEW GLARUS^WI^^^^^^^|
...
MSH|^~&|WIR22.4.9^^|WIR^^||WIRPH^^|20180916||VXU^V04|2018092011020600|P^|2.4^^|||ER
PID|||9765130^^^^SR^~^^^^PI^||ZTEST^^^^^^^^|^^^^^^^^^|20180808|M|||||||||||||||||||||
PD1|||||||||||02^^^^^|Y||||A
NK1|1||BRO^BROTHER^HL70063^^^^^|^^NEW GLARUS^WI^^^^^^^|
...
BTS|5|
FTS|1|
```

A batch file like this is a cumbersome way to hold and work with data, particularly if we wish to convert, extract, or manipulate one or more of the messages in the batch file. The harmonization module allows us to quickly and easily convert this batch file into a list of HL7 messages, one entry in the list per message:

```python
from phdi.harmonization import convert_hl7_batch_messages_to_list

batch = [definition above]
msg_list = convert_hl7_batch_messages_to_list(batch)

assert len(msg_list) == 2
>>> True
assert msg_list[0].startswith("MSH|")
>>> True
```

### Standardizing One or More Names
Let's now say we want to work with some raw text data, in the form of strings. Perhaps we have a database of patient names, or perhaps a CSV file of provider organizations. Whatever the case, we want to perform text cleaning on one or more entity names. This is easily accomplished using the raw data standardization functionality of harmonization:

```python
from phdi.harmonization import standardize_name

raw_name = " Mi9Ke "
cleaned_name = standardize_name(raw_name)
print(cleaned_name)
>>> "MIKE"
```

Note here the default settings used if no parameter options are specified: conversion to upper case, removal of leading and trailing white space, and elimination of numeric characters. We can adjust these parameters to fit our liking if we wish to, for example, use a different casing and preserve white spaces. Further, `standardize_name` also allows us to pass in an entire list of names in one call, rather than requiring us to invoke the function once on each name in a list individually:

```python

from phdi.harmonization import standardize_name

raw = [" joHn", "phil", "Shepard 89 "]
clean = standardize_name(raw, trim=False, case="title")
print(clean)
>>> "[' John', 'Phil', 'Shepard  ']"
```

### Standardizing One or More Phone Numbers
The functionality to standardize either a single phone number or a list of phone numbers is analogous to standardizing names above. Here, the standardization employed is ISO E.164, the International Public Telecommunications Numbering Plan.

```python
from phdi.harmonization import standardize_phone

raw_1 = "123-234-6789"
clean_1 = standardize_phone(raw_1)
print(clean_1)
>>> "+11232346789"

raw_2 = "798.612.3456"
clean_2 = standardize_phone(raw_2, ["GB"])
print(clean_2)
>>> "+447986123456"
```

If we choose not to pass in a parameter of countries, the standardization function will automatically attempt to parse using the United States' country code. If we wish to attempt standardizing using a parsing scheme for another country, as in our second example using Great Britain, we must pass in a list of countries to attempt to parse with. The standardization function will always append the US to the back of this list as a fallback country to parse with. Further, if an input phone number begins with a `+` and an identifiable country code (such as `+1` for US phones), the `countries` parameter will be ignored in favor of the provided country code. Note that the standardization function is robust to the use of delimiters separating the chunks of a phone number—functionality remains unchanged whether a `.`, `-`, or even ` ` is used (e.g., passing in `123 456 7890` will parse to the same result as `123-456-7890`). We can also standardize an entire list of phone numbers at once, as with names:

```python
from phdi.harmonization import standardization

phones = ["555-654-1234", "919876543210", "648.324 687878965"]
cleaned_phones = standardize_phone(phones, ["IN"])
print(cleaned_phones)
>>> "['+915556541234', '+919876543210', '+916483246878']"
```

### Standardizing All Names in a Patient Resource
While the harmonization modules provide diverse functionality to operate on raw text strings, they also allow us to process more complex, richly-structured FHIR resource data. The `phdi.fhir.harmonization` package contains wrappers for all functions used in the base `phdi.harmonization` package, so that the same standardization can be performed (with the same options) on FHIR data. Suppose we have a patient resource that looks as follows:

```python
patient = {
    "id": "some-uuid",
    "name": [
        {
            "family": "doe",
            "given": ["John ", " Dan123456789ger "],
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
    "telecom": [
        {
            "use": "home",
            "system": "phone",
            "value": "123-456-7890"
        },
        {
            "use": "mobile",
            "system": "phone",
            "value": "555-666-1234"
        }
    ]
}
```

We can see there are multiple names within this resource corresponding to different use capacities. The harmonization module gives us an easy way to standardize and process all the names within a resource using the same kinds of normalization that we could on raw text. For example:

```python
from phdi.fhir.harmonization import standardize_names

cleaned_patient = standardize_names(patient, trim=True, case="upper", remove_numbers=True, overwrite=True)
assert cleaned_patient.get("name").get("family") == "DOE
>>> True
assert cleaned_patient.get("name").get("given") == ["JOHN", "DANGER"]
>>> True
```

We spelled out the parameter options in this example, but we could just as easily have omitted them all, since they're using the default settings. Of particular interest is the `overwrite` parameter, which specifies whether the standardization function should overwrite the information in the provided input resource (`overwrite=True`) or whether the function should create a copy of the input first and only modify the copy (`overwrite=False`).

### Standardizing All Phone Numbers in a Bundle of Resources
Now let's suppose that instead of a single resource, we have a whole bundle of FHIR data (recall that a bundle is simply a list of FHIR-formatted JSON resources). This data structure would look like:

```python
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
```

Let's also suppose that the first patient resource in the bundle is the sample `patient` we defined above, John Doe. We can invoke phone number standardization on this whole bundle just as we would for a single resource (analogous to how raw string standardization could operate on a single value or a list of values):

```python
from phdi.fhir.harmonization import standardize_phones

cleaned_bundle = standardize_phones(bundle)
john_doe = cleaned_bundle[0]
print(john_doe.get("telecom")[0].get("value"))
>>> "+1123456789"
print(john_doe.get("telecom")[1].get("value"))
>>> "+15556661234"
```
