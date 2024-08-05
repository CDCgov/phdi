"use client";
import {
  ProcessList,
  ProcessListItem,
  ProcessListHeading,
  Button,
  Modal,
  ModalHeading,
  ModalFooter,
  ModalToggleButton,
  ModalRef,
} from "@trussworks/react-uswds";
import { useRouter } from "next/navigation";
import {
  useEffect,
  useRef,
  useState,
  MutableRefObject,
  createRef,
} from "react";

/**
 * The landing page for the TEFCA Viewer.
 * @returns The LandingPage component.
 */
export default function LandingPage() {
  const router = useRouter();
  const modalRef = useRef<ModalRef>(null);
  const [isClient, setIsClient] = useState(false);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const handleClick = () => {
    if (selectedOption) {
      router.push(`/query?useCase=${encodeURIComponent(selectedOption)}`);
    } else {
      router.push(`/query`);
    }
  };

  useEffect(() => {
    setIsClient(true);
  }, []);

  const optionRef = useRef<HTMLButtonElement | null>(null);
  const handleOptionClick = (
    option: string,
    ref: MutableRefObject<HTMLButtonElement | null>,
  ) => {
    console.log("option", option);
    console.log("ref", ref);
    ref.current?.focus();
    setSelectedOption(option);
  };

  return (
    <div>
      <div className="display-flex flex-justify-center flex-column">
        <div className="gradient-blue-background">
          <div className="container">
            <div className="text-holder">
              <h1 className="font-sans-2xl text-bold">
                Data collection made easier
              </h1>
              <h2 className="font-sans-md text-light margin-top-2">
                The TEFCA Query Connector allows your jurisdiction to query a
                wide network of healthcare organizations (HCOs) enabled by
                TEFCA, giving you access to more complete and timely data.
              </h2>
            </div>
            <img src="/tefca-viewer/tefca-graphic.svg" />
          </div>
        </div>
        <div className="home">
          <h3 className="font-sans-l text-bold margin-top-5">What is it?</h3>
          <h2 className="font-sans-md text-light margin-top-0">
            The TEFCA Query Connector aims to streamline the collection of
            health data using an intuitive querying process that leverages
            Qualified Health Information Networks (QHINs) within the Trusted
            Exchange Framework and Common Agreement (TEFCA). This tool
            demonstrates how public health jurisdictions can leverage TEFCA to
            quickly retrieve patient records and relevant case information from
            HCOs without requiring direct connection and onboarding.
          </h2>
          <h3 className="font-sans-l text-bold margin-top-5">
            How does it work?
          </h3>
          <h2 className="font-sans-md text-light margin-top-0">
            Public health staff can interact with the TEFCA Query Connector
            manually by entering simple patient details — such as name, date of
            birth, or medical identifiers — along with a query use case, into
            the TEFCA Viewer. The TEFCA Viewer surfaces patient data relevant to
            the use case in an easily readable format, making data more usable
            for case investigation.
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
                Easily gather additional patient information tied to your
                specific use case
              </p>
            </ProcessListItem>
          </ProcessList>
        </div>
      </div>
      <div className="blue-background-container">
        <div className="display-flex flex-justify-center flex-column">
          <div className="text-holder">
            <h2 className="font-sans-xs text-light margin-top-0">
              Check out the TEFCA Viewer demo to try out features using sample
              data. See how the TEFCA Viewer could work for you.
            </h2>
            {isClient && (
              <ModalToggleButton
                modalRef={modalRef}
                opener
                title="Go to the demo"
              >
                Go to the demo
              </ModalToggleButton>
            )}
          </div>
        </div>
      </div>

      {isClient && (
        <Modal
          isLarge={true}
          ref={modalRef}
          className="custom-modal"
          id="example-modal-2"
          aria-labelledby="modal-2-heading"
          aria-describedby="modal-2-description"
          isInitiallyOpen={false}
          placeholder={undefined}
          onPointerEnterCapture={undefined}
          onPointerLeaveCapture={undefined}
        >
          <ModalHeading id="data-usage-policy-modal-heading">
            Customize your demo experience
          </ModalHeading>
          <div className="usa-prose">
            <p id="modal-2-description">
              Select a scenario to see what kinds of data you can gather using
              the TEFCA Query Connector.
            </p>
            <div className="modal-options">
              <Button
                type="button"
                className={`modal-option ${
                  selectedOption === "demo-sti-chlamydia"
                }`}
                ref={optionRef}
                onClick={() =>
                  handleOptionClick("demo-sti-chlamydia", optionRef)
                }
              >
                Chlamydia case investigation
              </Button>
              <Button
                type="button"
                className={`modal-option ${
                  selectedOption === "demo-sti-gonorrhea"
                }`}
                onClick={() =>
                  handleOptionClick("demo-sti-gonorrhea", createRef())
                }
              >
                Gonorrhea case investigation
              </Button>
              <Button
                type="button"
                className={`modal-option ${
                  selectedOption === "demo-sti-syphilis"
                }`}
                onClick={() =>
                  handleOptionClick("demo-sti-syphilis", createRef())
                }
              >
                Syphilis case investigation
              </Button>
              <Button
                type="button"
                className={`modal-option ${selectedOption === "demo-cancer"}`}
                onClick={() => handleOptionClick("demo-cancer", createRef())}
              >
                Cancer case investigation
              </Button>
              <Button
                type="button"
                className={`modal-option ${
                  selectedOption === "demo-newborn-screening"
                }`}
                onClick={() =>
                  handleOptionClick("demo-newborn-screening", createRef())
                }
              >
                Newborn screening follow-up
              </Button>
              <Button
                type="button"
                className={`modal-option ${
                  selectedOption === "demo-social-determinants"
                    ? "selected"
                    : ""
                }`}
                onClick={() =>
                  handleOptionClick("demo-social-determinants", createRef())
                }
              >
                Gather social determinants of health for a patient
              </Button>
            </div>
          </div>
          <ModalFooter>
            <Button
              className="get-started-button"
              type="button"
              onClick={handleClick}
            >
              Next
            </Button>
          </ModalFooter>
        </Modal>
      )}
    </div>
  );
}
