"use client";

import React, { useState } from "react";
import CustomizeQuery from "./components/CustomizeQuery"; // Adjust the path if necessary
import { Mode } from "../constants";

const dummyLabs = [
  {
    code: "24111-7",
    display:
      "Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection",
    system: "LOINC",
    include: true,
    author: "CSTE Steward",
  },
  {
    code: "72828-7",
    display:
      "Chlamydia trachomatis and Neisseria gonorrhoeae DNA panel - Specimen",
    system: "LOINC",
    include: true,
    author: "CSTE Steward",
  },
  {
    code: "21613-5",
    display:
      "Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection",
    system: "LOINC",
    include: true,
    author: "CSTE Steward",
  },
];

const dummyMedications = [
  {
    code: "12345-6",
    display: "Medication A",
    system: "LOINC",
    include: true,
    author: "Author A",
  },
  {
    code: "67890-1",
    display: "Medication B",
    system: "LOINC",
    include: true,
    author: "Author B",
  },
];

const dummyConditions = [
  {
    code: "11111-1",
    display: "Condition A",
    system: "LOINC",
    include: true,
    author: "Author A",
  },
  {
    code: "22222-2",
    display: "Condition B",
    system: "LOINC",
    include: true,
    author: "Author B",
  },
];

/**
 * PreviewCustomizeQuery component for previewing the CustomizeQuery component.
 * @returns The PreviewCustomizeQuery component.
 */
const PreviewCustomizeQuery: React.FC = () => {
  const [mode, setMode] = useState<Mode>("customize-queries");

  if (mode === "search") {
    return (
      <div>
        <p>Uh...I didn't want to develop this functionality further...</p>
      </div>
    );
  }

  return (
    <div>
      <CustomizeQuery
        queryType="Chlamydia case investigation"
        ValueSet={{
          labs: dummyLabs,
          medications: dummyMedications,
          conditions: dummyConditions,
        }}
        setMode={setMode}
      />
    </div>
  );
};

export default PreviewCustomizeQuery;