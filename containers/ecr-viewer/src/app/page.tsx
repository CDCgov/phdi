import { ListObjectsV2CommandOutput } from "@aws-sdk/client-s3";
import React from "react";
import { processListECR } from "@/app/services/processService";
import ListECRViewer from "@/app/ListEcrViewer";
import { listEcrData } from "@/app/api/services/listEcrDataService";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = async () => {
  type ListApiResponse = {
    data: any[] | ListObjectsV2CommandOutput;
    source: string;
  };

  const response = await listEcrData();
  const responseBody: ListApiResponse = await response.json();
  // TODO: move to API?
  const listFhirData = processListECR(responseBody.data, responseBody.source);

  return (
    <main>
      <ListECRViewer listFhirData={listFhirData} />
    </main>
  );
};

export default HomePage;
