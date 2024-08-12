import React from "react";
import ListECRViewer from "@/app/components/ListEcrViewer";
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
    <div className="display-flex flex-column height-viewport">
      <Header />
      <main className="overflow-auto height-full">
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
