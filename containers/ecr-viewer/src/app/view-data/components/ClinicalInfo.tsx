import { DisplayData, renderData } from "../../utils";
import { AccordianDiv, AccordianH3, AccordianSection } from "@/app/view-data/component-utils";

interface ClinicalInfoProps {
  clinicalNotes: DisplayData[];
}

const ClinicalInfo = ({ clinicalNotes }: ClinicalInfoProps) => {
  return(
    <AccordianSection>
      <AccordianH3>Clinical Notes</AccordianH3>
      <AccordianDiv>
        {renderData(clinicalNotes)}
      </AccordianDiv>
    </AccordianSection>
  )
}

export default ClinicalInfo;