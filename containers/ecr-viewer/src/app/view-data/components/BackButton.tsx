import React from "react";
import { Icon } from "@trussworks/react-uswds";
import Link from "next/link";

/**
 * Back button component for returning users from the eCR Viewer page to the eCR Library home page
 * @returns <BackButton/> a react component back button
 */
export const BackButton = () => {
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";

  return (
    <div className="display-flex back-button-wrapper">
      {isNonIntegratedViewer ? (
        <Link href={"/"} className={"back-button display-flex"}>
          <Icon.ArrowBack aria-label={"Back Arrow"} size={3} />
          Back to eCR Library
        </Link>
      ) : (
        ""
      )}
    </div>
  );
};
