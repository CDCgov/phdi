"use client";
import EcrSummary from "@/app/view-data/components/EcrSummary";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Bundle } from "fhir/r4";
import { Accordion, SideNav } from "@trussworks/react-uswds";
import {
  PathMappings,
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
  evaluateDemographicsData,
  evaluateEcrMetadata,
} from "../utils";
import Demographics from "./components/Demographics";
import SocialHistory from "./components/SocialHistory";
import UnavailableInfo from "./components/UnavailableInfo";
import EcrMetadata from "./components/EcrMetadata";

const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error | unknown>(null);
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";
  const accordionItems: any[] = [
    {
      content: null,
      expanded: true,
      id: "1",
      headingLevel: "h2",
      link: [
        <a href="#ecr-summary">eCR Summary</a>,
        <SideNav
          isSubnav={true}
          items={[
            <a href="#about-the-patient">About the Patient</a>,
            <a href="#about-the-encounter">About the Encounter</a>,
            <a href="#about-the-condition">About the Condition</a>,
          ]}
        />,
      ],
    },
    {
      content: null,
      expanded: true,
      id: "1",
      headingLevel: "h2",
      link: [<a href="#ecr-document">eCR Document</a>],
    },
    {
      content: null,
      expanded: true,
      id: "1",
      headingLevel: "h2",
      link: [
        <a href="#patient-info">Patient Info</a>,
        <SideNav
          isSubnav={true}
          items={[<a href="#demographics">Demographics</a>]}
        />,
      ],
    },
    {
      content: null,
      expanded: true,
      id: "2",
      headingLevel: "h2",
      link: [
        <a href="#ecr-metadata">eCR Metadata</a>,
        <SideNav
          isSubnav={true}
          items={[
            <a href="#rr-details">RR Details</a>,
            <a href="#eicr-details">eICR Details</a>,
            <a href="#ecr-sender-details">eCR Sender Details</a>,
          ]}
        />,
      ],
    },
    {
      title: "Unavailable Info",
      content: null,
      expanded: true,
      id: "2",
      headingLevel: "h2",
      link: <a href="#unavailable-info">Unavailable Info</a>,
    },
  ];

  type ApiResponse = {
    fhirBundle: Bundle;
    fhirPathMappings: PathMappings;
  };

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/fhir-data?id=${fhirId}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "Internal Server Error");
        } else {
          const bundle: ApiResponse = await response.json();
          setFhirBundle(bundle.fhirBundle);
          setMappings(bundle.fhirPathMappings);
        }
      } catch (error) {
        setErrors(error);
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  const renderAccordion = () => {
    const demographicsData = evaluateDemographicsData(fhirBundle, mappings);
    const social_data = evaluateSocialData(fhirBundle, mappings);
    const encounterData = evaluateEncounterData(fhirBundle, mappings);
    const providerData = evaluateProviderData(fhirBundle, mappings);
    const ecrMetadata = evaluateEcrMetadata(fhirBundle, mappings);
    const accordionItems: any[] = [
      {
        title: <span id="patient-info">Patient Info</span>,
        content: (
          <>
            <Demographics demographicsData={demographicsData.availableData} />
            {social_data.availableData.length > 0 && (
              <SocialHistory socialData={social_data.availableData} />
            )}
          </>
        ),
        expanded: true,
        id: "1",
        headingLevel: "h2",
      },
      {
        title: <span id="ecr-metadata">eCR Metadata</span>,
        content: (
          <>
            <EcrMetadata
              eicrDetails={ecrMetadata.eicrDetails.availableData}
              eCRSenderDetails={ecrMetadata.ecrSenderDetails.availableData}
              rrDetails={ecrMetadata.rrDetails.availableData}
            />
          </>
        ),
        expanded: true,
        id: "2",
        headingLevel: "h2",
      },
      {
        title: <span id="unavailable-info">Unavailable Info</span>,
        content: (
          <div className="padding-top-105">
            <UnavailableInfo
              demographicsUnavailableData={demographicsData.unavailableData}
              socialUnavailableData={social_data.unavailableData}
              encounterUnavailableData={encounterData.unavailableData}
              providerUnavailableData={providerData.unavailableData}
            />
          </div>
        ),
        expanded: true,
        id: "4",
        headingLevel: "h2",
      },
    ];

    return (
      <Accordion
        className="info-container"
        items={accordionItems}
        multiselectable={true}
      />
    );
  };

  if (errors) {
    return <div>{`${errors}`}</div>;
  } else if (fhirBundle && mappings) {
    return (
      <div>
        <header>
          <h1 className={"page-title"}>EZ eCR Viewer</h1>
        </header>
        <div
          className="main-container"
          style={{ display: "flex", justifyContent: "center" }}
        >
          <div
            style={{
              display: "flex",
              maxWidth: "1440px",
              justifyContent: "center",
              gap: "48px",
            }}
          >
            {" "}
            {/* Wrapper div with gap */}
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                width: "100%",
              }}
            >
              {" "}
              {/* Wrapper for right-justifying nav */}
              <nav style={{ maxWidth: "170px" }}>
                <SideNav items={accordionItems.map((item) => item.link)} />
              </nav>
            </div>
            <div
              className="ecr-viewer-container"
              style={{
                flexBasis: "auto",
                display: "flex",
                justifyContent: "left",
              }}
            >
              <div style={{ maxWidth: "1222px" }}>
                {" "}
                {/* Adjusted for 170px nav + 48px gap */}
                <h2 className="margin-bottom-3" id="ecr-summmary">
                  eCR Summary
                </h2>
                <EcrSummary
                  fhirPathMappings={mappings}
                  fhirBundle={fhirBundle}
                />
                <div className="margin-top-6">
                  <h2 className="margin-bottom-3" id="ecr-document">
                    eCR Document
                  </h2>
                  {renderAccordion()}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  } else {
    return (
      <div>
        <h1>Loading...</h1>
      </div>
    );
  }
};

export default ECRViewerPage;
