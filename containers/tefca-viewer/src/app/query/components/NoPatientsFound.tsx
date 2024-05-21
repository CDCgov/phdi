import React, { useEffect } from "react";
import { Mode } from "../page";

interface NoPatientsFoundProps {
  setMode: (mode: Mode) => void;
}

/**
 * Displays a message when no patients are found.
 * @param root0 - NoPatientsFound props.
 * @param root0.setMode - The function to set the mode.
 * @returns - The NoPatientsFound component.
 */
const NoPatientsFound: React.FC<NoPatientsFoundProps> = ({ setMode }) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <div className="no-patients-found">
      <h1 className="font-sans-2xl text-bold">No Patients Found</h1>
      <p className="font-sans-lg text-light">
        There are no patient records that match your search criteria.
      </p>
      <a href="#" onClick={() => setMode("search")}>
        Search for a new patient
      </a>
    </div>
  );
};

export default NoPatientsFound;
