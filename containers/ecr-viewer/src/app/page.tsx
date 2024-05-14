"use client";
import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";
import React, { useEffect, useState } from "react";
import { Table } from "@trussworks/react-uswds";
import { formatDateTime } from "@/app/services/formatService";
import { noData } from "@/app/utils";

// string constants to match with source values
const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const basePath = process.env.NODE_ENV === "production" ? "/ecr-viewer" : "";

export type ListEcr = {
  ecr_id: string;
  dateModified: string;
}[];

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = () => {
  const [listFhirData, setListFhirData] = useState<ListEcr>();
  const [errors, setErrors] = useState<Error>();

  type ListApiResponse = {
    data: any[] | ListObjectsV2CommandOutput;
    source: string;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${basePath}/api/list-fhir-data`);
        if (!res.ok) {
          const errorData = res.statusText;
          throw new Error(errorData || "Internal Server Error");
        } else {
          const response: ListApiResponse = await res.json();
          setListFhirData(processListECR(response.data, response.source));
        }
      } catch (error: any) {
        setErrors(error);
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  if (errors) {
    return (
      <div>
        <pre>
          <code>{`${errors}`}</code>
        </pre>
      </div>
    );
  } else if (listFhirData) {
    return renderListECRViewer(listFhirData);
  } else {
    return (
      <div>
        <h1>Loading...</h1>
      </div>
    );
  }
};

/**
 * Renders a list of eCR data with viewer.
 * @param listFhirData - The list of eCRs to render.
 * @returns The JSX element (table) representing the rendered list of eCRs.
 */
function renderListECRViewer(listFhirData: ListEcr): JSX.Element {
  const header = ["eCR ID", "Stored Date"];
  return (
    <div className="content-wrapper">
      <Table
        bordered={false}
        fullWidth={true}
        className={"table-homepage-list"}
        data-testid="table"
      >
        <thead>
          <tr>
            {header.map((column) => (
              <th key={`${column}`} scope="col">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {listFhirData.map((item, index) => {
            return (
              <tr key={`table-row-${index}`}>
                <td>
                  <a href={`${basePath}/view-data?id=${item.ecr_id}`}>
                    {item.ecr_id ?? noData}
                  </a>
                </td>
                <td>{item.dateModified ?? noData}</td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    </div>
  );
}

/**
 * Directs processing a given list of eCRs from different sources based on the source.
 * It supports fetching from S3 and Postgres. If the source is not `postgres` or `s3`,
 * it throws an error stating invalid source.
 * @param responseBody - Response body containing the list of eCRs from either source.
 * @param source - Source of the eCR list (postgres or s3)
 * @returns The array of objects representing the processed list of eCR data.
 * @throws {Error} If the data source is invalid.
 */
const processListECR = (
  responseBody: any[] | ListObjectsV2CommandOutput,
  source: string,
): ListEcr => {
  let returnBody: ListEcr;
  if (source === S3_SOURCE) {
    returnBody = processListS3(responseBody as ListObjectsV2CommandOutput);
  } else if (source === POSTGRES_SOURCE) {
    returnBody = processListPostgres(responseBody as any[]);
  } else {
    throw new Error("Invalid data source");
  }
  return returnBody;
};

/**
 * Processes a list of eCR data retrieved from an S3 bucket.
 * @param responseBody - The response body containing eCR data from S3.
 * @returns - The processed list of eCR IDs and dates.
 */
export const processListS3 = (
  responseBody: ListObjectsV2CommandOutput,
): ListEcr => {
  return (
    responseBody.Contents?.map((object) => {
      return {
        ecr_id: object.Key?.replace(".json", "") || "",
        dateModified: object.LastModified
          ? formatDateTime(object.LastModified.toString())
          : "",
      };
    }) || []
  );
};

/**
 * Processes a list of eCR data retrieved from Postgres.
 * @param responseBody - The response body containing eCR data from Postgres.
 * @returns - The processed list of eCR IDs and dates.
 */
export const processListPostgres = (responseBody: any[]): ListEcr => {
  return responseBody.map((object) => {
    return {
      ecr_id: object.ecr_id || "",
      dateModified: "N/A",
    };
  });
};

export default HomePage;
