import React from "react";
import ListECRViewer from "@/app/ListEcrViewer";
import { ListEcr, listEcrData } from "@/app/api/services/listEcrDataService";

export const dynamic = "force-dynamic";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = async () => {
  let listFhirData: ListEcr = [];
  if (
    process.env.STANDALONE_VIEWER &&
    process.env.STANDALONE_VIEWER === "true"
  ) {
    listFhirData = await listEcrData();
  }

  return (
    <main>
      {process.env.STANDALONE_VIEWER &&
      process.env.STANDALONE_VIEWER === "true" ? (
        <ListECRViewer listFhirData={listFhirData} />
      ) : (
        <div>
          <h1>Sorry, this page is not available.</h1>
        </div>
      )}
    </main>
  );
};

export default HomePage;
