import { Alert, HeadingLevel } from "@trussworks/react-uswds";
import { toast } from "react-toastify";

import styles from "./redirectToast.module.css";

export type AlertType = "info" | "success" | "warning" | "error";

type RedirectToastProps = {
  toastVariant: AlertType;
  heading: string;
  body: string;
  headingLevel?: HeadingLevel;
};
/**
 * Redirection toast to be invoked when there's a need to confirm with the user
 * something has occurred
 * @param root0 - The config object to specify content / styling of the toast
 * @param root0.toastVariant - A string from the enum set "info" | "success" | "warning" | "error"
 * indicating what type of toast variant we want. Will style the USWDS component accordingly
 * @param root0.heading - The heading / title of the alert
 * @param root0.body - The body content of the alert
 * @param root0.headingLevel - string of h1-6 indicating which heading level the alert will be.
 * defaults to h4
 * @returns A toast component using the USWDS alert
 */
const RedirectToast: React.FC<RedirectToastProps> = ({
  toastVariant,
  heading,
  body,
  headingLevel,
}) => {
  return (
    <Alert
      type={toastVariant}
      heading={heading}
      headingLevel={headingLevel ? headingLevel : "h4"}
    >
      {body}
    </Alert>
  );
};

const options = {
  hideProgressBar: false,
  position: "bottom-left" as const,
  closeOnClick: true,
  closeButton: false,
  className: styles.noPaddingImportant,
  bodyClassName: styles.noPaddingImportant,
  pauseOnFocusLoss: false,
};

/**
 *
 * @param content - content object to configure the redirect confirmation toast
 * @param content.heading - heading of the redirect toast
 * @param content.body - body text of the redirect toast
 * @param content.headingLevel - h1-6 level of the heading tag associated with
 * content.heading. defaults to h4
 */
export function showRedirectConfirmation(content: {
  heading: string;
  body: string;
  headingLevel?: HeadingLevel;
}) {
  toast.success(
    <RedirectToast
      toastVariant="success"
      heading={content.heading}
      headingLevel={content.headingLevel}
      body={content.body}
    />,
    options,
  );
}

export default RedirectToast;
