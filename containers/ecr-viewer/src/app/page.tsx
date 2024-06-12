import React from "react";
import ListECRViewer from "@/app/ListEcrViewer";
import { listEcrData } from "@/app/api/services/listEcrDataService";
import { getServerSession } from "next-auth";

export const dynamic = "force-dynamic";

/**
 * Functional component for rendering the home page that lists all eCRs.
 * @returns The home page JSX component.
 */
const HomePage: React.FC = async () => {
  const listFhirData = await listEcrData();
  const serverSession = await getServerSession();
  console.log(serverSession?.user?.email);

  return (
    <main>
      <ListECRViewer listFhirData={listFhirData} />
    </main>
  );
};

export default HomePage;
