import React from "react";
import { listEcrData } from "@/app/api/services/listEcrDataService";

import { EcrTableClient } from "@/app/components/EcrTableClient";

const basePath =
  process.env.NODE_ENV === "production" ? process.env.NEXT_PUBLIC_BASEPATH : "";

/**
 * eCR Table
 * @param props - The properties passed to the component.
 * @param props.currentPage - The current page to be displayed
 * @param props.itemsPerPage - The number of items to be displayed in the table
 * @returns - eCR Table element
 */
const EcrTable = async ({
  currentPage,
  itemsPerPage,
}: {
  currentPage: number;
  itemsPerPage: number;
}) => {
  const startIndex = (currentPage - 1) * itemsPerPage;
  const initialData = await listEcrData(startIndex, itemsPerPage);
  const defaultSort = { columnId: "received-date", direction: "desc" };

  return (
    <div className="ecr-client-wrapper width-full overflow-auto">
      <EcrTableClient data={initialData} defaultSort={defaultSort} />
    </div>
  );
};

export default EcrTable;
