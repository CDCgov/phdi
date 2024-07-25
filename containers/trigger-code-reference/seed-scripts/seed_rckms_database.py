#!/usr/bin/env python
"""
seed_rckms_database.py
===========

This script parses an archive of RCKMS reporting specifications and extracts
the ValueSets for each condition.  The ValueSets are then queried against the
NIH UMLS API to retrieve the specific CodeSets related to the ValueSets.  Which
are then stored in a SQLite database for use in the API.

The RCKMS reporting specifications archive can be manually downloaded from the
following sharepoint website (hover over the directory and its associated
ellipses, then click the download icon).

https://cste-my.sharepoint.com/personal/dbarter_cste_org/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fdbarter%5Fcste%5Forg%2FDocuments%2FRCKMS%2FContent%20Releases%2FRCKMS%20Content%20Release%2011

The NIH UMLS API key is required to query the API.  The key can be obtained by
registering at the following website using your CDC email address:
    https://uts.nlm.nih.gov/uts/login


Example:
    $ python seed_rckms_database.py <archive.zip> <database.db>
"""

import argparse
import asyncio
import base64
import concurrent.futures
import dataclasses
import itertools
import json
import os
import re
import sqlite3
import sys
import typing
import urllib.parse
import urllib.request
import zipfile

import bs4
import mammoth

UMLS_API_KEY = os.getenv("UMLS_API_KEY", default=None)
OID_RE = re.compile(r"^(?:[0-9]+\.)+[0-9]+$")
CONCURRENT_REQUESTS = 20


# FIXME: Determine a way to download the archive programmatically
# TODO: store the CodeSets in a SQLite database


@dataclasses.dataclass
class Condition:
    """
    A Condition extracted from an RCKMS docx file
    """

    name: str
    version: str
    snomed: str
    system: str = "https://www.rckms.org/content-repository/"

    def __str__(self):
        """A string representation of the Condition object."""
        return f"{self.name} [{self.snomed}]"


@dataclasses.dataclass
class ValueSet:
    """
    A ValueSet extracted from an RCKMS docx file
    """

    oid: str
    category: str
    title: str = ""
    version: str = ""
    author: str = ""
    conditions: list[Condition] = dataclasses.field(default_factory=list)

    def __str__(self):
        """A string representation of the ValueSet object."""
        return f"{self.oid} [{self.version}]"


@dataclasses.dataclass
class CodeSet:
    """
    A CodeSet retrieved from the NIH UMLS API
    """

    code: str
    display: str
    system: str
    version: str
    valueset: ValueSet

    def __str__(self):
        """A string representation of the CodeSet object."""
        return f"{self.code} [{self.system}]"


def batched(iterable, n):
    """
    Backport of the itertools 'batched' function from Python 3.12.
    """
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        yield batch


def arg_dir_path(path):
    """
    Validate that the given path is a directory.
    """
    if os.path.isdir(path):
        return path
    raise argparse.ArgumentTypeError(f"Not a valid directory: {path}")


async def exec_async(executor, func, *args, **kwargs):
    """
    Execute a function asynchronously using the given executor.

    :param executor: The executor to use.
    :param func: The function to execute.
    :param args: The positional arguments to pass to the function.
    :param kwargs: The keyword arguments to pass to the function.

    :return: The result of the function.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, func, *args, **kwargs)


def initialize_database(db: str, migrations: str, reset: bool = True) -> None:
    """
    Initialize the SQLite database with the starting schema.

    :param db: The path to the SQLite database.
    :param migrations: The path to the directory containing the SQL migrations.
    :param reset: Whether to reset the database by removing the existing file.

    :return: None
    """
    if reset and os.path.exists(db):
        # remove the existing database file if it exists to start fresh
        os.remove(db)
    with sqlite3.connect(db) as con:
        # for each SQL file in the migrations directory, execute the SQL in order
        for fname in sorted(os.listdir(migrations)):
            if fname.endswith(".sql"):
                with open(os.path.join(migrations, fname)) as f:
                    con.executescript(f.read())
        con.commit()


def list_docx_files(archive: str) -> typing.Iterable[tuple[str, typing.IO[bytes]]]:
    """
    Unzip the archive and list all the docx files nested within.  For each docx file,
    extract the file name and file object and yield a tuple of the two.

    :param archive: The path to the archive file.

    :return: An iterable of tuples containing the filename and file object.
    """
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.endswith(".docx"):
                with z.open(name) as f:
                    yield name, f


def extract_condition_from_rckms_doc(
    filename: str, tree: bs4.BeautifulSoup
) -> Condition:
    """
    Given a RCKMS docx file, iterate through items specified in the summary and extract
    data from the file name to construct a Condition object.

    :param filename: The filename of the docx file.
    :param tree: The file object as a BeautifulSoup object

    :return: A Condition object.
    """
    # extract the basename minus the extension
    basename = os.path.basename(filename).rsplit(".", 1)[0]
    # determine the split character based on the presence of a '.' or '_'
    split = "." if "." in basename else "_"
    # split the basename into the condition and version
    name, version = basename.rsplit(split, 1)
    snomed = ""
    # find the first list in the tree
    first_list = tree.find("ul")
    if first_list:
        for ident in first_list.find_all("li"):
            # split the key and value, using the first '=' as the delimiter
            parts = ident.text.split("=", 1)
            # some items may not have a '=' delimiter, so skip them
            if len(parts) == 2:
                # convert the key to lowercase and strip any whitespace
                key = parts[0].strip().lower()
                # split the value and take the first part, then strip any whitespace
                val = parts[1].strip().lower().split("|")[0].strip()
                # if the first part of the value is numeric, use only that
                if val.split()[0].isnumeric():
                    val = val.split()[0]
                if key == "condition":
                    name = val
                elif "snomed" in key:
                    snomed = val
    return Condition(name=name, version=version, snomed=snomed)


def extract_valuesets_from_rckms_doc(tree: bs4.BeautifulSoup) -> list[ValueSet]:
    """
    Given a RCKMS docx file, iterate through the tables and extract the Value Set data.
    Return a list of ValueSet objects for each row in the table.

    :param tree: The file object as a BeautifulSoup object

    :return: A list of ValueSet objects.
    """
    results: list[ValueSet] = []

    for table in tree.find_all("table"):
        # initialize the category variable to distinguish between clinical and
        # laboratory ValueSets.  As we iterate through the table rows, a category
        # change will be defined by the first word in rows that only have one cell
        category = ""
        headers = [th.text.strip() for th in table.find_all("th")]
        if not headers:
            # headers are missing, use the first row as the headers
            headers = [td.text.strip() for td in table.find("tr").find_all("td")]
        # only process tables with the first header of 'Value Set Name'
        if headers and headers[0] == "Value Set Name":
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                # only process rows with the same number of cells as headers
                if len(cells) == len(headers):
                    # create a dictionary of the row data, mapping the header to the cell value
                    data = {
                        header: cell.text
                        for header, cell in zip(headers, row.find_all("td"))
                    }
                    if OID_RE.match(data["OID"]):
                        # store the row data in a dictionary, using the OID as the key
                        results.append(ValueSet(data["OID"], category))
                elif cells:
                    # if the row has cells, but not the same number as headers, set the category
                    # based on the first word of the first cell
                    category = cells[0].text.split()[0].lower()
    return results


def query_valueset_api(oid: str, retries: int = 2) -> dict:
    """
    Query the NIH UMLS RetrieveValueSet API with the given OID.

    :param oid: The OID to query.
    :param retries: The number of retries to attempt if the request fails.

    :return: The response from the API.
    """
    # encode the API key as a base64 string
    b64auth = base64.b64encode(f"apikey:{UMLS_API_KEY}".encode()).decode()
    # create a urllib request with the path and parameters
    req = urllib.request.Request(f"https://cts.nlm.nih.gov/fhir/ValueSet/{oid}/$expand")
    # add the authorization header to the request
    req.add_header("Authorization", f"Basic {b64auth}")
    req.add_header("Accept", "application/fhir+json; fhirVersion=4.0.1")
    try:
        # open the request and read the response
        with urllib.request.urlopen(req) as f:
            # parse the response as JSON
            return json.loads(f.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"OID not found: {oid}")
            return {}
        if retries > 0:
            # retries are enabled, attempt to query the API again
            return query_valueset_api(oid, retries - 1)
        # the request failed and retries are disabled, raise an exception
        # and add a note to the exception with the error message
        # obtained from the API response
        err = str(e.fp.read())
        msg = f"Error querying UMLS API: [{e.code}] {err}"
        e.add_note(msg)
        raise


def parse_archive(
    archive: str, limit: int | None = None
) -> tuple[list[Condition], dict[str, ValueSet]]:
    """
    Given an archive of RCKMS reporting specifications, extract the ValueSets for
    each condition.

    :param archive: The path to the archive file.
    :param limit: The maximum number of files to extract. If None, extract all files.

    :return: A 2-tuple of a Conditions extracted and a dictionary mapping them
        OID to ValueSets found.
    """
    conditions: list[Condition] = []
    mapping: dict[str, ValueSet] = {}

    count = 0
    for fname, fobj in list_docx_files(archive):
        if limit is not None and count >= limit:
            break
        count += 1
        # convert microsoft docx to html
        html = mammoth.convert_to_html(fobj)
        # convert HTML string into a BeautifulSoup tree
        tree = bs4.BeautifulSoup(html.value, "lxml")
        # extract the Condition from the RCKMS docx file
        condition = extract_condition_from_rckms_doc(fname, tree)
        # extract the ValueSets from the RCKMS docx file
        valuesets = extract_valuesets_from_rckms_doc(tree)
        for vs in valuesets:
            # for each ValueSet, add it the OID/ValueSet mapping
            # and update the ValueSet with the Condition
            if vs.oid not in mapping:
                mapping[vs.oid] = vs
            mapping[vs.oid].conditions.append(condition)
        conditions.append(condition)
    return (conditions, mapping)


def retrieve_codesets(data: dict[str, ValueSet]) -> dict[str, list[CodeSet]]:
    """
    Given a dictionary of OIDs, query the NIH UMLS API to retrieve the CodeSets.

    :param data: A dictionary mapping the OID to a ValueSet

    :return: A dictionary mapping the OID to a list of CodeSets.
    """
    results: dict[str, list[CodeSet]] = {}

    async def retrieve_codesets(oids: typing.Iterable[str]):
        """
        Retrieve the CodeSets for the given OIDs asynchronously.  Async calls are
        preferred since the API calls are I/O bound, and we should be able to increase
        performance by making multiple requests concurrently.

        :param oids: An iterable of OIDs to retrieve the CodeSets for.

        :return: A list of dict responses.
        """
        # create a ThreadPoolExecutor to run the async calls, this is necessary since
        # the urllib.request.urlopen() call is blocking and will not work with the default
        # event loop, which is single-threaded. Wrapping the blocking call in a
        # ThreadPoolExecutor, will give us the ability to run multiple requests concurrently.
        with concurrent.futures.ThreadPoolExecutor() as e:
            # create async tasks for querying the UMLS API, one for each OID to query
            tasks = [exec_async(e, query_valueset_api, o) for o in oids]
            # gather the responses from the async tasks
            responses = await asyncio.gather(*tasks)
        return responses

    # process the OIDs in batches to avoid making too many requests at once
    for oids in batched(data.keys(), CONCURRENT_REQUESTS):
        # run the async function to retrieve the CodeSets for the OIDs
        for response in asyncio.run(retrieve_codesets(oids)):
            try:
                # attempt to parse the OID, title, version, author and concept list from
                # the response. If any of these keys are missing, skip the response.
                oid = response["id"]
                title = response["title"]
                version = response["version"]
                author = response["publisher"]
                concept = response["expansion"]["contains"]
            except (KeyError, IndexError):
                continue
            valueset = data[oid]
            # update the original ValueSet with title, version and author information
            # obtained from the API
            valueset.title = title
            valueset.version = version
            valueset.author = author
            # create a list of CodeSet values based on the concept list data
            results[oid] = [CodeSet(valueset=valueset, **c) for c in concept]
    return results


def load_database(
    db: str,
    conditions: typing.Collection[Condition],
    valuesets: typing.Collection[ValueSet],
    codesets: typing.Collection[CodeSet],
) -> tuple[int, int, int]:
    """
    Load the CodeSets into the SQLite database.

    :param db: The path to the SQLite database.
    :param conditions: A collection of Condition objects.
    :param valuesets: A collection of ValueSet objects.
    :param codesets: A collection of CodeSet objects.

    :return: A tuple of the number of conditions, valuesets and codesets loaded.
    """
    counts = {
        "conditions": 0,
        "valuesets": 0,
        "codesets": 0,
    }
    with sqlite3.connect(db) as con:
        cur = con.cursor()
        for vs in valuesets:
            # insert the ValueSet Type into the database if it does not exist
            cur.execute(
                "INSERT INTO value_set_type (id, clinical_service_type) "
                "VALUES (:category, :category) "
                "ON CONFLICT DO NOTHING",
                vs.__dict__,
            )
            # insert the ValueSet into the database if it does not exist
            cur.execute(
                "INSERT INTO value_sets (id, version, value_set_name, author, clinical_service_type_id) "
                "VALUES (:oid, :version, :title, :author, :category) "
                "ON CONFLICT DO NOTHING",
                vs.__dict__,
            )
            counts["valuesets"] += cur.rowcount
            cond = {**{"oid": vs.oid}, **vs.conditions[0].__dict__}
            # insert the Condition into the database if it does not exist
            cur.execute(
                "INSERT INTO conditions (id, value_set_id, system, name) "
                "VALUES (:snomed, :oid, 'http://snomed.info/sct', :name) "
                "ON CONFLICT DO NOTHING",
                cond,
            )
            counts["conditions"] += cur.rowcount
        for cs in codesets:
            oid = cs.valueset.oid
            data = {**{"id": f"{oid}_{cs.code}", "oid": oid}, **cs.__dict__}
            # insert the CodeSet into the database if it does not exist
            cur.execute(
                "INSERT INTO clinical_services (id, value_set_id, code, code_system, display, version) "
                "VALUES (:id, :oid, :code, :system, :display, :version) "
                "ON CONFLICT DO NOTHING",
                data,
            )
            counts["codesets"] += cur.rowcount
        con.commit()

        # return the counts of conditions, valuesets and codesets loaded
        return (counts["conditions"], counts["valuesets"], counts["codesets"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "archive", type=argparse.FileType(), help="The archive file to process"
    )
    parser.add_argument(
        "database",
        type=argparse.FileType("wb"),
        help="The database file to store the data",
    )
    parser.add_argument(
        "--migrations",
        type=arg_dir_path,
        help="A directory containing database migrations to apply before seeding",
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of condition files to process"
    )

    args = parser.parse_args()

    if not UMLS_API_KEY:
        print("Error: UMLS_API_KEY environment variable not set.")
        sys.exit(1)

    if args.migrations:
        print("Initializing database...")
        initialize_database(args.database.name, migrations=args.migrations)

    print("Processing archive...")
    conditions, valuesets = parse_archive(args.archive.name, limit=args.limit)
    print(f"Extracted {len(conditions)} conditions")
    print(f"Extracted {len(valuesets)} valuesets")
    print("Retrieving codesets...")
    codeset_map = retrieve_codesets(valuesets)
    codesets = [cs for _list in codeset_map.values() for cs in _list]
    # iterate through nested
    print(f"Retrieved {len(codesets)} codesets")
    print("Loading data into database...")
    loaded = load_database(args.database.name, conditions, valuesets.values(), codesets)
    print(f"Loaded {loaded[0]} conditions")
    print(f"Loaded {loaded[1]} valuesets")
    print(f"Loaded {loaded[2]} codesets")
