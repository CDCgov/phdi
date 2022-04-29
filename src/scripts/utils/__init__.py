from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobClient
from io import StringIO
import pandas as pd


def get_blob_client(url: str, container: str, file: str) -> BlobClient:
    """
    Use whatever credentials Azure can find to get a blob client for the blob specified
    by the given account url, container, and file name.
    """
    creds = DefaultAzureCredential()
    blob_client = BlobClient(
        account_url=url, container_name=container, blob_name=file, credential=creds
    )
    return blob_client


def read_blob(url: str, container: str, file: str) -> StringIO:
    """
    Use whatever credentials Azure can find to create a blob client and download the
    blob's content as text. In the case where the blob is a CSV the output may be passed
    directly to pandas.read_csv().
    """
    blob_client = get_blob_client(url, container, file)
    return StringIO(blob_client.download_blob().content_as_text())


def write_blob(data: str, url: str, container: str, file: str):
    """
    Given a string of data to be written to a blob, use whatever credentials Azure can
    find to create a blob client and write the data.
    """
    blob_client = get_blob_client(url, container, file)
    blob_client.upload_blob(data)


def record_combination_func(x: pd.Series) -> str:
    """
    Aggregation function applied behind the scenes when performing
    de-duplicating linkage. Automatically filters for blank, null,
    and NaN values to facilitate squashing duplicates down into one
    consolidated record, such that, for any column X:
      - if records 1, ..., n-1 are empty in X and record n is not,
        then n(X) is used as a single value
      - if some number of records 1, ..., j <= n have the same value
        in X and all other records are blank in X, then the value
        of the matching columns 1, ..., j is used as a singleton
      - if some number of non-empty in X records 1, ..., j <= n have
        different values in X, then all values 1(X), ..., j(X) are
        concatenated into a list of values delimited by commas
    """
    non_nans = {x for x in x.astype(str).to_list() if x != ""}
    return ",".join(non_nans)
