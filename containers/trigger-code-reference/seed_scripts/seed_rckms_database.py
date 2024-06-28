#!/usr/bin/env python
"""
seed_rckms_database.py
===========

This script parses an archive of RCKMS reporting specifications and extracts
the ValueSets for each condition.  The ValueSets are then queried against the
NIH UMLS API to retrieve the specific CodeSets related to the ValueSets.  Which
are then stored in a SQLite database for use in the API.


Example:
    $ python seed_rckms_database.py archive.zip
"""
import dataclasses
import os
import sys
import typing
import zipfile

import bs4
import mammoth


@dataclasses.dataclass
class Identifiers:
    """
    Summary identifiers extracted from an RCKMS docx file
    """
    data: dict[str, str]

@dataclasses.dataclass
class ValueSet:
    """
    A ValueSet extracted from an RCKMS docx file
    """
    oid: str
    category: str
    in_trigger_set: bool


def list_condition_files(
    archive: str,
) -> typing.Iterable[typing.Tuple[str, typing.IO[bytes]]]:
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


def extract_identifiers_from_rckms_doc(filename: str, tree: bs4.BeautifulSoup) -> Identifiers:
    """
    Given a RCKMS docx file, iterate through items specified in the summary and extract the identifiers.

    :param filename: The filename of the docx file.
    :param tree: The file object as a BeautifulSoup object

    :return: An Identifiers object.
    """
    # extract the condition from the filename
    condition = os.path.basename(filename).rsplit('.', 2)[0]
    # add a default condition, in case its not found in the identifiers list
    result: typing.Dict[str, str] = {"condition": condition}
    # for each item in the summary list (first ul in the document)
    for ident in tree.find('ul').find_all('li'):
        # split the key and value, using the first '=' as the delimiter
        parts = ident.text.split('=', 1)
        # some items may not have a '=' delimiter, so skip them
        if len(parts) == 2:
            # convert the key to lowercase and strip any whitespace
            key = parts[0].strip().lower()
            # split the value and take the first part, then strip any whitespace
            val = parts[1].strip().lower().split('|')[0].strip()
            # if the first part of the value is numeric, use only that
            if val.split()[0].isnumeric():
                val = val.split()[0]
            result[key] = val
    return Identifiers(result)


def extract_valuesets_from_rckms_doc(tree: bs4.BeautifulSoup) -> typing.List[ValueSet]:
    """
    Given a RCKMS docx file, iterate through the tables and extract the Value Set data.
    Return a list of ValueSet objects for each row in the table.

    :param tree: The file object as a BeautifulSoup object

    :return: A list of ValueSet objects.
    """
    results: typing.List[ValueSet] = []
    for table in tree.find_all('table'):
        category = ""
        headers = [th.text.strip() for th in table.find_all('th')]
        # only process tables with the first header of 'Value Set Name'
        if headers and headers[0] == 'Value Set Name':
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                # only process rows with the same number of cells as headers
                if len(cells) == len(headers):
                    # create a dictionary of the row data, mapping the header to the cell value
                    data = {header: cell.text for header, cell in zip(headers, row.find_all('td'))}
                    # find the first key that contains 'trigger set'
                    trigger_key = next((s for s in data.keys() if "trigger set" in s.lower()), None)
                    # check if the valueset is included in the trigger set
                    in_trigger_set = data.get(trigger_key, '').lower().startswith('yes')
                    # store the row data in a dictionary, using the OID as the key
                    results.append(ValueSet(data['OID'], category, in_trigger_set))
                elif cells:
                    # if the row has cells, but not the same number as headers, set the category
                    # based on the first word of the first cell
                    category = cells[0].text.split()[0].lower()
    return results


def parse_archive(archive: str) -> dict[str, typing.Tuple[Identifiers, typing.List[ValueSet]]]:
    """
    Given an archive of RCKMS reporting specifications, extract the ValueSets for each condition.

    :param archive: The path to the archive file.

    :return: A dictionary mapping the condition filename to a tuple of Identifiers and ValueSets.
    """
    results: dict[str, typing.Tuple[Identifiers, typing.List[ValueSet]]] = {}
    for fname, fobj in list_condition_files(archive):
        # convert microsoft docx to html
        html = mammoth.convert_to_html(fobj)
        # convert HTML string into a BeautifulSoup tree
        tree = bs4.BeautifulSoup(html.value, 'lxml')
        identifiers = extract_identifiers_from_rckms_doc(fname, tree)
        valuesets = extract_valuesets_from_rckms_doc(tree)
        results[fname] = (identifiers, valuesets)
    return results


if __name__ == "__main__":
    # Validate the command line arguments
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <archive.zip>")
        sys.exit(1)

    # Validate the archive exists
    archive = sys.argv[1]
    if not os.path.exists(archive):
        print(f"Error: {archive} not found.")
        sys.exit(1)

    parse_archive(archive)
    # TODO: for each ValueSet, use the NIH UMLS API to retrieve the CodeSets
    # TODO: store the CodeSets in a SQLite database
