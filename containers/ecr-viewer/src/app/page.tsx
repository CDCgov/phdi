import React from "react";
import ListECRViewer from "@/app/ListEcrViewer";
import Header from "./Header";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";

export const dynamic = "force-dynamic";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = async () => {
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";
  let listFhirData: EcrDisplay[] = [];
  if (isNonIntegratedViewer) {
    listFhirData = await listEcrData();
  }

  return (
    <div className="ecr-library-viewer-container">
      <Header />
      <main className="ecr-library-main">
        {isNonIntegratedViewer ? (
          <ListECRViewer listFhirData={listFhirData} />
        ) : (
          <div>
            <h1>Sorry, this page is not available.</h1>
          </div>
        )}
      </main>
    </div>
  );
};

export default HomePage;
