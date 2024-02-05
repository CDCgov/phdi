"use client";
import EcrSummary, {
  ecrSummaryConfig,
} from "@/app/view-data/components/EcrSummary";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { Bundle } from "fhir/r4";
import { Accordion } from "@trussworks/react-uswds";
import {
  PathMappings,
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
  evaluateDemographicsData,
  evaluateEcrMetadata,
  evaluateClinicalData,
} from "../utils";
import Demographics, { demographicsConfig } from "./components/Demographics";
import SocialHistory, { socialHistoryConfig } from "./components/SocialHistory";
import UnavailableInfo from "./components/UnavailableInfo";
import EcrMetadata, { ecrMetadataConfig } from "./components/EcrMetadata";
import SideNav, { SectionConfig } from "./components/SideNav";
import ClinicalInfo from "./components/Clinical";
import EncounterDetails, { encounterConfig } from "./components/Encounter";

const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error | unknown>(null);
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";

  const sideNavConfigs = [
    ecrSummaryConfig,
    new SectionConfig("eCR Document", [
      new SectionConfig("Patient Info", [
        demographicsConfig,
        socialHistoryConfig,
      ]),
      ecrMetadataConfig,
      encounterConfig,
    ]),
    new SectionConfig("Unavailable Info"),
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
    const clinicalData = evaluateClinicalData(fhirBundle, mappings);
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
        title: <span id="encounter-info">Encounter Info</span>,
        content: (
          <div>
            <EncounterDetails
              encounterData={encounterData.availableData}
              providerData={providerData.availableData}
            />
          </div>
        ),
        expanded: true,
        id: "3",
        headingLevel: "h2",
      },
      {
        title: <span id="clinical-info">Clinical Info</span>,
        content: (
          <div>
            <ClinicalInfo
              activeProblemsDetails={
                clinicalData.activeProblemsDetails.availableData
              }
              vitalData={clinicalData.vitalData.availableData}
            />
          </div>
        ),
        expanded: true,
        id: "4",
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
              activeProblemsUnavailableData={
                clinicalData.activeProblemsDetails.unavailableData
              }
              vitalUnavailableData={clinicalData.vitalData.unavailableData}
            />
          </div>
        ),
        expanded: true,
        id: "5",
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
          <h1 className="page-title">EZ eCR Viewer</h1>
        </header>
        <div className="main-container">
          <div className="content-wrapper">
            <div className="nav-wrapper">
              <nav className="sticky-nav">
                <SideNav sectionConfigs={sideNavConfigs} />
              </nav>
            </div>
            <div className="ecr-viewer-container">
              <div className="ecr-content">
                <h2 className="margin-bottom-3" id="ecr-summary">
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
