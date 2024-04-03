import { DataDisplay, DisplayData, DataTableDisplay } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";
import classNames from "classnames";
import { Table } from "@trussworks/react-uswds";

type TableEntry = {
  Name: string;
  Type: string;
  Priority: string;
  AssociatedDiagnoses?: string;
  DateTime?: string;
  OrderSchedule?: string;
};

interface ClinicalProps {
  reasonForVisitDetails: DisplayData[];
  activeProblemsDetails: DisplayData[];
  vitalData: DisplayData[];
  immunizationsDetails: DisplayData[];
  treatmentData: DisplayData[];
  clinicalNotes: DisplayData[];
  planOfTreatment: {
    value: TableEntry[];
  }[];
}

export const clinicalInfoConfig: SectionConfig = new SectionConfig(
  "Clinical Info",
  [
    "Symptoms and Problems",
    "Immunizations",
    "Diagnostics and Vital Signs",
    "Treatment Details",
    "Clinical Notes",
  ],
);

export const ClinicalInfo = ({
  reasonForVisitDetails,
  activeProblemsDetails,
  immunizationsDetails,
  vitalData,
  treatmentData,
  clinicalNotes,
  planOfTreatment,
}: ClinicalProps) => {
  const renderTableDetails = (tableDetails: DisplayData[]) => {
    return (
      <div>
        {tableDetails.map((item, index) => (
          <div key={index}>
            <div className="grid-col-auto text-pre-line">{item.value}</div>
            <div className={"section__line_gray"} />
          </div>
        ))}
      </div>
    );
  };

  const renderClinicalNotes = () => {
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[4].id}>
            {clinicalInfoConfig.subNavItems?.[4].title}
          </span>
        </AccordianH4>
        <AccordianDiv className={"clinical_info_container"}>
          {clinicalNotes.map((item, index) => {
            let className = "";
            if (
              React.isValidElement(item.value) &&
              item.value.type == "table"
            ) {
              className = "maxw-full grid-col-12 margin-top-1";
            }
            return (
              <DataDisplay item={item} key={index} className={className} />
            );
          })}
        </AccordianDiv>
      </>
    );
  };

  const renderSymptomsAndProblems = () => {
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[0].id}>
            {clinicalInfoConfig.subNavItems?.[0].title}
          </span>
        </AccordianH4>
        <AccordianDiv>
          <div data-testid="reason-for-visit">
            {reasonForVisitDetails.map((item, index) => (
              <DataDisplay item={item} key={index} />
            ))}
          </div>
          <div data-testid="active-problems">
            {renderTableDetails(activeProblemsDetails)}
          </div>
        </AccordianDiv>
      </>
    );
  };

  const renderImmunizationsDetails = () => {
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[1].id}>
            {clinicalInfoConfig.subNavItems?.[1].title}
          </span>
        </AccordianH4>
        <AccordianDiv>
          <div data-testid="immunization-history">
            {renderTableDetails(immunizationsDetails)}
          </div>
        </AccordianDiv>
      </>
    );
  };

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[2].id}>
            {clinicalInfoConfig.subNavItems?.[2].title}
          </span>
        </AccordianH4>
        <AccordianDiv>
          <div className="lh-18" data-testid="vital-signs">
            {vitalData.map((item, index) => (
              <DataDisplay item={item} key={index} />
            ))}
          </div>
        </AccordianDiv>
      </>
    );
  };

  const renderTreatmentDetails = () => {
    const data = treatmentData.filter((item) => !React.isValidElement(item));
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[3].id}>
            {clinicalInfoConfig.subNavItems?.[3].title}
          </span>
        </AccordianH4>
        <AccordianDiv>
          <div data-testid="treatment-details">
            {data.map((item, index) => (
              <DataTableDisplay item={item} key={index} />
            ))}
          </div>
          <div className={"section__line_gray margin-y-2"} />
        </AccordianDiv>
      </>
    );
  };

  const renderPlanOfTreatmentDetails = () => {
    console.log("planOfTreatment", planOfTreatment);

    const header = [
      "Name",
      "Type",
      "Priority",
      "Associated Diagnoses",
      "Date/Time",
    ];

    const cellClassNames = classNames("table-caption-margin margin-y-0", {
      "border-top border-left border-right": true,
    });

    const myTable = (
      <Table
        fixed={true}
        bordered={false}
        fullWidth={true}
        caption={"Pending Results"}
        className={classNames("table-caption-margin margin-y-0", {})}
        data-testid="table"
      >
        <thead>
          <tr>
            {header.map((column, index) => (
              <th
                key={`${column}${index}`}
                scope="col"
                className="bg-gray-5 minw-15"
              >
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {planOfTreatment[0].value.map((entry: TableEntry, index) => {
            console.log("entry", entry);
            return (
              <tr key={`table-row-${index}`}>
                <td className={cellClassNames}>{entry.Name}</td>
                <td className={cellClassNames}>{entry.Type}</td>
                <td className={cellClassNames}>{entry.Priority}</td>
                <td className={cellClassNames}>{entry.AssociatedDiagnoses}</td>
                <td className={cellClassNames}>{entry.DateTime}</td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    );

    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[3].id}>
            {clinicalInfoConfig.subNavItems?.[3].title}
          </span>
        </AccordianH4>
        <AccordianDiv>{myTable}</AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {clinicalNotes?.length > 0 && renderClinicalNotes()}
      {(reasonForVisitDetails.length > 0 || activeProblemsDetails.length > 0) &&
        renderSymptomsAndProblems()}
      {planOfTreatment.length > 0 && renderPlanOfTreatmentDetails()}
      {treatmentData.length > 0 && renderTreatmentDetails()}
      {immunizationsDetails.length > 0 && renderImmunizationsDetails()}
      {vitalData.length > 0 && renderVitalDetails()}
    </AccordianSection>
  );
};

export default ClinicalInfo;
