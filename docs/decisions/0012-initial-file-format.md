# 12. Initial Supported File Format

Date: 2022-06-30

## Status

Accepted

## Context and Problem Statement

For data storage, the team required an initial data format to support as the solution is developed. The file format will be used by other agencies to collect and analyze data health data in their region. The file format chosen will not be the only format supported by the application; in future iterations the team will support a variety of formats. However for the initial development of the application, only a few file formats will be supported 

## Decision Drivers

**Well-supported** - The file format must be common and well-supported by many applications. The users who may eventually use our files will use their own tools to read our data files. So having a common format will help end users access the data. 

**Quick-to-implement** - Having a file format that can be easy to work with will help the development of the solution be quicker. 

**Infrastructure requirements** - Due to limited resources on the team, a solution that requires less infrastructure resources to maintain will help speed up the development process.

**Cost-effective** - With any cloud environment, storage cost considerations are necessary to scale up an application without incurring too much cost. 

## Considered Options

### Parquet
Apache parquet is a free and open source storage binary format for fast analytical querying. Because of the binary storage format, it is easier to compress the file and therefore, less costly to store. It is a columnar oriented storage format instead of row format with the format being:

<table>
  <tr>
    <td>1</td>
    <td>2</td>
    <td>3</td>
  </tr>
  <tr>
    <td>n1</td>
    <td>n2</td>
    <td>n3</td>
  </tr>
  <tr>
    <td>20</td>
    <td>35</td>
    <td>62</td>
  </tr>
</table>

The equivalent row format would be 

<table>
  <tr>
    <td>1</td>
    <td>n1</td>
    <td>20</td>
  </tr>
  <tr>
    <td>2</td>
    <td>n2</td>
    <td>35</td>
  </tr>
  <tr>
    <td>3</td>
    <td>n3</td>
    <td>62</td>
  </tr>
</table>



Pros: 
- Generally speaking, good for storing large amounts data
- Saves on cloud storage space by using highly efficient column-wise compression, and flexible encoding schemes for columns with different data types.
- Well-supported file format from analytics tools

Cons:
- Readability without transformation is not as straightforward compared to a row-based format like CSV
- Changing a schema over time is not as simple compared to CSV.


### CSV
CSV is one of the most common file format for reading data. It has a simple row-based structure that allows users to integrate easily with table readers such as Excel. 

Pros: 
- Supported by nearly all table readers a user may want to use.
- Easily readable without transformation. 
- Most developers understand how CSV files work

Cons:
- Costly to store. Because one row has multiple data types, it is harder to compress the files for storage
- Slower to read. Because of disk space needed to read the file, it is slower to read through the CSV file.  

### Fully-Managed DB
A fully managed DB would circumvent the need to export data into a file format before querying the data. With RDBMS support, analysts could query data using SQL from our DB without having to manage files on their own. The export process would create an export function to create tables and write to tables in postgresql

Pros: 
- Direct querying our data without extra steps for analytics
- More control for consumers to get the exact data that they need. 

Cons:
- High infrastructure costs by needing develops to stand up the resources and maintain it
- Likely a more complex initial setup for security for STLTs to access the data they want. 

## Decision Outcome

**Parquet** 
Because STLTs and the CDC may be storing large amounts of data. Using a file format that has advantages in storage costs will help minimize the cost of storage. In a chart from towardsdatascience.com, a CSV file of 1TB would be about a 0.25 TB file in parquet. These cost savings and performance gains outweigh the raw readability of CSV for our project. 

In future iterations, we will support exports to CSV in addition parquet. 


## Appendix (OPTIONAL)

[CSV vs Parquet](https://towardsdatascience.com/csv-files-for-storage-no-thanks-theres-a-better-option-72c78a414d1d)
[Pros and cons of parquet](https://stackoverflow.com/questions/36822224/what-are-the-pros-and-cons-of-parquet-format-compared-to-other-formats)
