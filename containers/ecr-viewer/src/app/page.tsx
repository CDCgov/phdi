"use client";
import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";
import React, { useEffect, useState } from "react";
import { Table } from "@trussworks/react-uswds";
import { noData } from "@/app/utils";
import { ListEcr, processListECR } from "@/app/services/processService";

const basePath = process.env.NODE_ENV === "production" ? "/ecr-viewer" : "";

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

export default HomePage;
