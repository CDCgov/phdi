import {
  evaluateSocialData,
  evaluateDemographicsData,
  PathMappings,
} from "../../utils";
import Demographics from "./Demographics";
import SocialHistory from "./SocialHistory";
import ObservationTable, {ObservationTableProps} from "./Observations";
import { Bundle, FhirResource, Observation } from "fhir/r4";
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
    "resourceType": "Observation",
    "id": "1",
    "status": "final",
    "code": {
      "coding": [
        {
          "system": "http://loinc.org",
          "code": "8302-2",
          "display": "Body Height"
        }
      ],
      "text": "Body Height",
    },
    "valueQuantity": {
      "value": 180,
      "unit": "cm",
      "system": "http://unitsofmeasure.org",
      "code": "cm"
    },
    "interpretation": [
      {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "N",
          "display": "Normal"
        }
      ],
      "text": "Normal"
    }
  ],
    "effectiveDateTime": "2021-01-01",
    "referenceRange": [
      {
        "low": {
          "value": 160,
          "unit": "cm",
          "system": "http://unitsofmeasure.org",
          "code": "cm"
        },
        "high": {
          "value": 200,
          "unit": "cm",
          "system": "http://unitsofmeasure.org",
          "code": "cm"
        }
      }
    ]
  }
]
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
