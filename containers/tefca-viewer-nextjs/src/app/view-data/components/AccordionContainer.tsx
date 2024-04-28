import {
  evaluateSocialData,
  evaluateDemographicsData,
  PathMappings,
} from "../../utils";
import Demographics from "./Demographics";
import SocialHistory from "./SocialHistory";
import ObservationTable from "./Observations";
import {Observation} from "./Observations";
import {ObservationTableProps} from "./Observations";
import { Bundle, FhirResource } from "fhir/r4";
import React, { ReactNode } from "react";
import { Accordion } from "@trussworks/react-uswds";
import { formatString } from "@/app/format-service";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";


const fakeObservations: Observation[] = [
  {
    id: "1",
    typeDisplay: "Blood Pressure",
    typeCode: "Blood Pressure",
    typeSystem: "http://loinc.org",
    valueString: "120/80",
    valueQuantity: "120",
    valueUnit: "mm[Hg]",
    valueDisplay: "120/80",
    valueCode: "120/80",
    valueSystem: "http://loinc.org",
    interpDisplay: "Normal",
    interpCode: "Normal",
    interpSystem: "http://snomed.info/sct",
    effectiveDateTime: "2021-09-01",
    referenceRangeHigh: "120",
    referenceRangeLow: "80",
    referenceRangeHighUnit: "mm[Hg]",
    referenceRangeLowUnit: "mm[Hg]",
  },
  {
    id: "2",
    typeDisplay: "Temperature",
    typeCode: "Temperature",
    typeSystem: "http://loinc.org",
    valueString: "98.6",
    valueQuantity: "98.6",
    valueUnit: "F",
    valueDisplay: "98.6",
    valueCode: "98.6",
    valueSystem: "http://loinc.org",
    interpDisplay: "Normal",
    interpCode: "Normal",
    interpSystem: "http://snomed.info/sct",
    effectiveDateTime: "2021-09-01",
    referenceRangeHigh: "98.6",
    referenceRangeLow: "98.6",
    referenceRangeHighUnit: "F",
    referenceRangeLowUnit: "F",
  },
];

const fakeObservationTableProps: ObservationTableProps = {
  observations: fakeObservations,
};

type AccordionContainerProps = {
  children?: ReactNode;
  fhirBundle: Bundle<FhirResource>;
  fhirPathMappings: PathMappings;
};

const AccordianContainer: React.FC<AccordionContainerProps> = ({
  fhirBundle,
  fhirPathMappings,
}) => {
  const demographicsData = evaluateDemographicsData(
    fhirBundle,
    fhirPathMappings,
  );
  const social_data = evaluateSocialData(fhirBundle, fhirPathMappings);
  const accordionItems: any[] = [
    {
      title: "Patient Info",
      content: (
        <>
          <Demographics demographicsData={demographicsData.availableData} />
          {social_data.availableData.length > 0 && (
            <SocialHistory socialData={social_data.availableData} />
          )}
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Observations",
      content: (
        <>
          <AccordianSection>
            <AccordianH4>
              <span id="observations">Observations</span>
            </AccordianH4>
            <AccordianDiv>
              <ObservationTable {...fakeObservationTableProps} />
            </AccordianDiv>   
          </AccordianSection>
        </>
      ),
      expanded: true,
      headingLevel: "h3",

    }
  ];

  //Add id, adjust title
  accordionItems.forEach((item, index) => {
    let formattedTitle = formatString(item["title"]);
    item["id"] = `${formattedTitle}_${index + 1}`;
    item["title"] = <span id={formattedTitle}>{item["title"]}</span>;
    accordionItems[index] = item;
  });

  return (
    <Accordion
      className="info-container"
      items={accordionItems}
      multiselectable={true}
    />
  );
};
export default AccordianContainer;
