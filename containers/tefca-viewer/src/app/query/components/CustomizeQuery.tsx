import React from "react";

interface Lab {
  code: string;
  display: string;
  system: string;
  include: boolean;
}

interface Medication {
  code: string;
  display: string;
  system: string;
  include: boolean;
}

interface Condition {
  code: string;
  display: string;
  system: string;
  include: boolean;
}

interface CustomizeQueryProps {
  queryType: string;
  labs: Lab[];
  medications: Medication[];
  conditions: Condition[];
  onBack: () => void;
}

/**
 *
 * @param root0 -CustomizeQuerys
 * @param root0.queryType -Query
 * @param root0.labs - labs
 * @param root0.medications -meds
 * @param root0.conditions - conditions
 * @param root0.onBack -back
 * @returns - The CustomizeQuery component.
 */
const CustomizeQuery: React.FC<CustomizeQueryProps> = ({
  queryType,
  labs,
  medications,
  conditions,
  onBack,
}) => {
  return (
    <div>
      <h2>Customize query</h2>
      <h3>Query: {queryType}</h3>
      <div>
        <h4>Labs ({labs.length})</h4>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Display</th>
              <th>System</th>
              <th>Include</th>
            </tr>
          </thead>
          <tbody>
            {labs.map((lab, index) => (
              <tr key={index}>
                <td>{lab.code}</td>
                <td>{lab.display}</td>
                <td>{lab.system}</td>
                <td>
                  <input type="checkbox" checked={lab.include} readOnly />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div>
        <h4>Medications ({medications.length})</h4>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Display</th>
              <th>System</th>
              <th>Include</th>
            </tr>
          </thead>
          <tbody>
            {medications.map((med, index) => (
              <tr key={index}>
                <td>{med.code}</td>
                <td>{med.display}</td>
                <td>{med.system}</td>
                <td>
                  <input type="checkbox" checked={med.include} readOnly />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div>
        <h4>Conditions ({conditions.length})</h4>
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Display</th>
              <th>System</th>
              <th>Include</th>
            </tr>
          </thead>
          <tbody>
            {conditions.map((cond, index) => (
              <tr key={index}>
                <td>{cond.code}</td>
                <td>{cond.display}</td>
                <td>{cond.system}</td>
                <td>
                  <input type="checkbox" checked={cond.include} readOnly />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button onClick={onBack}>Back to Search</button>
    </div>
  );
};

export default CustomizeQuery;
