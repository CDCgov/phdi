import React from "react";
import ListECRViewer from "@/app/ListEcrViewer";
import Header from "./Header";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";

export const dynamic = "force-dynamic";

const isStandaloneViewer = process.env.NEXT_PUBLIC_STANDALONE_VIEWER === "true";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = async () => {
  let listFhirData: EcrDisplay[] = [];
  if (isStandaloneViewer) {
    listFhirData = await listEcrData();
  }

  return (
    <main>
      <Header />
      {isStandaloneViewer ? (
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
