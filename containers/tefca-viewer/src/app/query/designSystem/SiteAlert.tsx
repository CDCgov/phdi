import { Mode } from "@/app/constants";
import { Alert } from "@trussworks/react-uswds";

const contactUsDisclaimer = (
  <Alert type="info" headingLevel="h4" slim className="custom-alert">
    Interested in learning more about using the TEFCA Query Connector for your
    jurisdiction? Send us an email at{" "}
    <a
      href="mailto:dibbs@cdc.gov"
      style={{
        color: "inherit",
        fontWeight: "bold",
        textDecoration: "underline",
      }}
    >
      dibbs@cdc.gov
    </a>
  </Alert>
);

const piiDisclaimer = (
  <Alert type="info" headingLevel="h4" slim className="custom-alert">
    This site is for demo purposes only. Please do not enter PII on this
    website.
  </Alert>
);

type SiteAlertProps = {
  page: Mode;
};

const PageModeToSiteAlertMap: { [page in Mode]?: React.ReactNode } = {
  search: piiDisclaimer,
  "customize-queries": piiDisclaimer,
  results: contactUsDisclaimer,
};

/**
 *
 * @param root0 - params
 * @param root0.page - the page we're currently on
 * @returns A conditionally-rendered site view page component depending on the
 * semantic context
 */
const SiteAlert: React.FC<SiteAlertProps> = ({ page }) => {
  return <>{PageModeToSiteAlertMap[page]}</>;
};

export default SiteAlert;
