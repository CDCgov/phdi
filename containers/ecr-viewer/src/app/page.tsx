import React from "react";
import Header from "./Header";
import { EcrDisplay, listEcrData } from "@/app/api/services/listEcrDataService";
import ListECRViewer from "@/app/components/ListEcrViewer";
import EcrList from "@/app/components/EcrList";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @param props - parameters from the HomePage
 * @param props.searchParams - list of search params
 * @returns The home page JSX component.
 */
const HomePage = async ({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) => {
  const currentPage = Number(searchParams?.page) || 1;
  const itemsPerPage = Number(searchParams?.itemsPerPage) || 25;

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
          <ListECRViewer totalCount={listFhirData.length}>
            <EcrList currentPage={currentPage} itemsPerPage={itemsPerPage} />
          </ListECRViewer>
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
