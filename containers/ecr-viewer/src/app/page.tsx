"use client";
import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";
import React, { useEffect, useState } from "react";
import { formatDateTime } from "./format-service";
import { Table } from "@trussworks/react-uswds";
import { noData } from "@/app/utils";

// string constants to match with possible .env values
const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";
const basePath = process.env.NODE_ENV === "production" ? "/ecr-viewer" : "";

type ListEcr = {
  ecr_id: string;
  dateModified: string;
}[];

// TODO: Should this call the health check API route?

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
          console.log("REPSONSE", response);
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

// TODO: Add JSDoc
function renderListECRViewer(listFhirData: any[]): JSX.Element {
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

// TODO: Add JSDoc
// TODO: Maybe refactor into different # functions / files?
const processListECR = (
  responseBody: any[] | ListObjectsV2CommandOutput,
  source: string,
): ListEcr => {
  let returnBody: ListEcr;
  if (source === S3_SOURCE) {
    console.log("S3 SOURCE");
    returnBody = processListS3(responseBody as ListObjectsV2CommandOutput);
  } else if (source === POSTGRES_SOURCE) {
    console.log("POSTGRES SOURCE");
    returnBody = processListPostgres(responseBody as any[]);
  } else {
    console.log("ERROR Invalid data source");
    throw new Error("Invalid data source");
  }
  return returnBody;
};

// TODO: Add JSDoc
const processListS3 = (responseBody: ListObjectsV2CommandOutput): ListEcr => {
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

// TODO: Add JSDoc
const processListPostgres = (responseBody: any[]) => {
  return responseBody.map((object) => {
    return {
      ecr_id: object.ecr_id || "",
      dateModified: "N/A",
    };
  });
};

export default HomePage;
