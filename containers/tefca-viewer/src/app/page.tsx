"use client";
import {
  ProcessList,
  ProcessListItem,
  ProcessListHeading,
  Button,
} from "@trussworks/react-uswds";
import { useRouter } from "next/navigation";

/**
 * The landing page for the TEFCA Viewer.
 * @returns The LandingPage component.
 */
export default function LandingPage() {
  const router = useRouter();

  // useEffect(() => {
  //   if (window.location.pathname === "/" || window.location.pathname === "") {
  //     router.replace("/tefca-viewer");
  //   }
  // }, [router]);

  const handleClick = () => {
    router.push("/query");
  };

  return (
    <div className="display-flex flex-justify-center margin-top-5">
      <div className="home">
        <h1 className="font-sans-2xl text-bold">
          Case investigation made easier
        </h1>
        <h2 className="font-sans-lg text-light">
          The TryTEFCA Viewer provides a low-effort and zero-cost method for you
          to see the benefit from joining a TEFCA QHIN. This demo viewer is an
          easy demonstration of the benefits of TEFCA.
        </h2>
        <ProcessList className="padding-top-4">
          <ProcessListItem>
            <ProcessListHeading type="h4">
              Search for a patient
            </ProcessListHeading>
            <p className="margin-top-05 font-sans-xs">
              Based on name, date of birth, and other demographic information
            </p>
          </ProcessListItem>
          <ProcessListItem>
            <ProcessListHeading type="h4">
              View information tied to your case investigation
            </ProcessListHeading>
            <p className="font-sans-xs">
              Easily gather additional patient information tied to your specific
              use case
            </p>
          </ProcessListItem>
        </ProcessList>
        <Button
          className="get-started-button"
          type="button"
          onClick={handleClick}
        >
          Get started
        </Button>
      </div>
    </div>
  );
}
