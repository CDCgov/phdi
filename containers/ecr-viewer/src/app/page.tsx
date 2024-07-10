import React from "react";
import ListECRViewer from "@/app/ListEcrViewer";
import Header from "./Header";
import { Ecr, listEcrData } from "@/app/api/services/listEcrDataService";

export const dynamic = "force-dynamic";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = async () => {
  let listFhirData: Ecr[] = [];
  if (process.env.STANDALONE_VIEWER === "true") {
    listFhirData = await listEcrData();
  }

  return (
    <main>
      <Header />
      {process.env.STANDALONE_VIEWER === "true" ? (
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
