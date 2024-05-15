import { Bundle } from "fhir/r4";
import { PathMappings } from "../utils";
import EcrViewer from "@/app/view-data/components/EcrViewer";
import { processSnomedCode } from "@/app/view-data/service";

// string constants to match with possible .env values
const basePath =
  process.env.NODE_ENV === "production"
    ? "/ecr-viewer"
    : "http://localhost:3000";

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

  type ApiResponse = {
    fhirBundle: Bundle;
    fhirPathMappings: PathMappings;
  };
  const response = await fetch(`${basePath}/api/fhir-data?id=${fhirId}`);
  const bundle: ApiResponse = await response.json();
  const fhirBundle = bundle.fhirBundle;
  if (!fhirBundle) {
    throw Error(
      "Sorry, we couldn't find this eCR ID. Please try again with a different ID.",
    );
  }
  const mappings = bundle.fhirPathMappings;

  return (
    <main>
      <EcrViewer fhirBundle={fhirBundle} mappings={mappings} />
    </main>
  );
}
