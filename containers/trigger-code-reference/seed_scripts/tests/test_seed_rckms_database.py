"""
Test cases for the seed_rckms_database.py script.
"""
import bs4

from .. import seed_rckms_database as srd

def test_extract_identifiers_from_rckms_doc():
    """
    Test the extract_identifiers_from_rckms_doc function.
    """
    # Create a mock docx file
    docx = bs4.BeautifulSoup("""
    <html>
        <body>
            <ul>
                <li>A summary of the document</li>
                <li>Condition = Test Condition</li>
                <li> Organism=Virus</li>
                <li>SNOWMED Code = 12345 | Condition</li>
                <li>NNDSS Event Code = 54321|virus</li>
            </ul>
        </body>
    </html>
    """, "lxml")

    result = srd.extract_identifiers_from_rckms_doc("test.docx", docx)
    assert result.data == {
        "condition": "test condition",
        "organism": "virus",
        "snowmed code": "12345",
        "nndss event code": "54321",
    }


def test_extract_valuesets_from_rckms_doc_skip_table():
    """
    Test the extract_valuesets_from_rckms_doc function with a table that should be skipped.
    """
    # Create a mock docx file
    docx = bs4.BeautifulSoup("""
    <html>
        <body>
            <table>
                <tr>
                    <td><p><strong>Release Date</strong></p></td>
                    <td><p><strong>Release</strong></p></td>
                    <td><p><strong>Latest Revision Date</strong></p></td>
                </tr>
                <tr>
                    <td><p>01/29/2021</p></td>
                    <td><p>20210129</p></td>
                    <td><p>11/19/2020</p></td>
                </tr>
                <tr>
            </table>
        </body>
    </html>
    """, "lxml")

    result = srd.extract_valuesets_from_rckms_doc(docx)
    assert result == []


def test_extract_valuesets_from_rckms_doc():
    """
    Test the extract_valuesets_from_rckms_doc function.
    """
    # Create a mock docx file
    docx = bs4.BeautifulSoup("""
    <html>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>
                            <p><a id="_Hlk505106886"></a><strong>Value Set Name</strong></p>
                        </th>
                        <th>
                            <p><strong>OID</strong></p>
                        </th>
                        <th>
                            <p><strong>Description</strong></p>
                            <p><strong>(informational for drafting rules, but not as explicit as documented in VSAC)</strong></p>
                        </th>
                        <th>
                            <p><strong>Include in Trigger set</strong></p>
                            <p><strong>(Yes/No)</strong></p>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="3">
                            <p><strong>Clinical (Diagnoses, Problems, Symptoms, and Clinical Findings)</strong></p>
                        </td>
                        <td></td>
                    </tr>
                    <tr>
                        <td><p>Alpha gal syndrome (Disorders) (SNOMED)</p></td>
                        <td><p>2.16.840.1.113762.1.4.1146.1418</p></td>
                        <td><p>SNOMED codes for Alpha gal syndrome (as a diagnosis or active problem)</p></td>
                        <td><p>Yes: Diagnosis_problem</p></td>
                    </tr>
                    <tr>
                        <td><p>Alpha gal syndrome (Disorders) (ICD10CM)</p></td>
                        <td><p>2.16.840.1.113762.1.4.1146.1419</p></td>
                        <td><p>ICD10CM codes for Alpha gal syndrome (as a diagnosis or active problem)</p></td>
                        <td><p>Yes: Diagnosis_problem</p></td>
                    </tr>
                    <tr>
                        <td colspan="4">
                            <p><strong>Laboratory Test Names that are Organism or Substance Specific</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td><p>Alpha gal syndrome (Tests for Alpha gal IgE Antibody [Quantitative])</p></td>
                        <td><p>2.16.840.1.113762.1.4.1146.1420</p></td>
                        <td><p>Set of lab test names that may be ordered or ‘observed’ for detection of Alpha gal IgE quantitative antibody by any method</p></td>
                        <td><p>Yes: Lab obs test name</p></td>
                    </tr>
                    <tr>
                        <td><p>Alpha gal syndrome (Mammalian Meat Allergy Skin Test)</p></td>
                        <td><p>Not implemented – No codes available</p></td>
                        <td><p>Set of lab test names that may be ordered or ‘observed’ for detection of mammalian meat allergy by skin test method</p></td>
                        <td><p>N/A</p></td>
                    </tr>
                    <tr>
                        <td colspan="4">
                            <p><a id="_Hlk38525514"></a><strong>Laboratory (Result Values, Abnormal Interpretation, Specimen Type, or Status)</strong></p>
                        </td>
                    </tr>
                    <tr>
                        <td><p>Present or Positive Lab Result Value</p></td>
                        <td><p>2.16.840.1.113762.1.4.1146.272</p></td>
                        <td><p>Coded values for positive test results in the OBX-5 field, such as present, detected, positive, and reactive.</p></td>
                        <td><p>No: Common</p></td>
                    </tr>
                    <tr>
                        <td><p>Abnormal Interpretation of an Observation</p></td>
                        <td><p>2.16.840.1.113762.1.4.1146.295</p></td>
                        <td>
                            <p>
                                Set of HL7 Observation Interpretation codes (OID: [2.16.840.1.113883.5.83) that are indicative of 'abnormal' or 'outside normal range', or intermediate or resistant microbiology susceptibility results, all of
                                which may be reportable.
                            </p>
                        </td>
                        <td><p>No: Common</p></td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """, "lxml")

    result = srd.extract_valuesets_from_rckms_doc(docx)
    assert result == [
        srd.ValueSet(oid='2.16.840.1.113762.1.4.1146.1418', category='clinical', in_trigger_set=True),
        srd.ValueSet(oid='2.16.840.1.113762.1.4.1146.1419', category='clinical', in_trigger_set=True),
        srd.ValueSet(oid='2.16.840.1.113762.1.4.1146.1420', category='laboratory', in_trigger_set=True),
        srd.ValueSet(oid='Not implemented – No codes available', category='laboratory', in_trigger_set=False),
        srd.ValueSet(oid='2.16.840.1.113762.1.4.1146.272', category='laboratory', in_trigger_set=False),
        srd.ValueSet(oid='2.16.840.1.113762.1.4.1146.295', category='laboratory', in_trigger_set=False),
    ]
