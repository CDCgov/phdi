import EcrViewer from "@/app/view-data/components/EcrViewer";
import { processSnomedCode } from "@/app/view-data/service";
import { loadYamlConfig } from "@/app/api/services/utils";
import { getEcrData } from "@/app/api/services/ecrDataService";

/**
 * Functional component for rendering a page based on provided search parameters.
 * @param props - Component props.
 * @param props.searchParams - Search parameters object.
 * @returns - functional component for view-data
 */
export default async function Page({
  searchParams,
}: Readonly<{ searchParams: { [key: string]: string | undefined } }>) {
  const fhirId = searchParams["id"] ?? "";
  const snomedCode = searchParams["snomed-code"] ?? "";
  processSnomedCode(snomedCode);
  const fhirBundle = await getEcrData(fhirId);
  const mappings = loadYamlConfig();
  return (
    <main>
      <EcrViewer fhirBundle={fhirBundle} mappings={mappings} />
    </main>
  );
}
