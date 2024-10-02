import React, { useEffect } from "react";

/**
 * Displays a message when no patients are found.
 * @param root0 - NoPatientsFound props.
 * @param root0.setMode - The function to set the mode.
 * @returns - The NoPatientsFound component.
 */
const NoPatientsFound: React.FC = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <div className="no-patients-found">
      <h1 className="font-sans-2xl text-bold margin-top-205">
        No Records Found
      </h1>
      <p className="font-sans-lg text-light margin-top-0 margin-bottom-205">
        No records were found for your search
      </p>
    </div>
  );
};

export default NoPatientsFound;
