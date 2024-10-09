import { USE_CASES, demoQueryOptions } from "@/app/constants";
import fhirServers from "@/app/fhir-servers";
import { Select, Button } from "@trussworks/react-uswds";
import { RETURN_TO_STEP_ONE_LABEL } from "../PatientSearchResults";
import Backlink from "../backLink/Backlink";
import styles from "./selectQuery.module.css";
import { useState } from "react";

type SelectSavedQueryProps = {
  goBack: () => void;
  setSelectedQuery: (selectedQuery: USE_CASES) => void;
  selectedQuery: string;
  setShowCustomizedQuery: (showCustomize: boolean) => void;
  handleSubmit: () => void;
};
/**
 *
 * @param root0
 * @param root0.goBack
 * @param root0.selectedQuery
 * @param root0.setSelectedQuery
 * @param root0.setShowCustomizedQuery
 * @param root0.handleSubmit
 */
const SelectSavedQuery: React.FC<SelectSavedQueryProps> = ({
  goBack,
  selectedQuery,
  setSelectedQuery,
  setShowCustomizedQuery,
  handleSubmit,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <form className="content-container-smaller-width">
      {/* Back button */}
      <div className="text-bold">
        <Backlink onClick={goBack} label={RETURN_TO_STEP_ONE_LABEL} />
      </div>
      <h1 className={`${styles.selectQueryHeaderText}`}>
        Step 3: Select a query
      </h1>
      <div
        className={`font-sans-md text-light ${styles.selectQueryExplanationText}`}
      >
        We will request all data related to your selected patient and query. By
        only showing relevant data for your query, we decrease the burden on our
        systems and protect patient privacy. If you would like to customize the
        query response, click on the "customize query" button.
      </div>
      <h3 className="margin-bottom-3">Query</h3>
      <div className={styles.queryRow}>
        {/* Select a query drop down */}
        <Select
          id="querySelect"
          name="query"
          value={selectedQuery}
          onChange={(e) => setSelectedQuery(e.target.value as USE_CASES)}
          className={`${styles.queryDropDown}`}
          required
        >
          <option value="" disabled>
            Select query
          </option>
          {demoQueryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
        <Button
          type="button"
          className={`usa-button--outline bg-white ${styles.customizeButton}`}
          onClick={() => setShowCustomizedQuery(true)}
        >
          Customize query
        </Button>
      </div>

      {showAdvanced && (
        <div>
          <h3 className="margin-bottom-3">Health Care Organization (HCO)</h3>
          <Select
            id="fhir_server"
            name="fhir_server"
            // value={selectedHCO} // Use selectedHCO for the selected value
            // onChange={handleHCOChange}
            required
            defaultValue=""
            className={`${styles.queryDropDown}`}
          >
            <option value="" disabled>
              Select HCO
            </option>
            {Object.keys(fhirServers).map((fhirServer: string) => (
              <option key={fhirServer} value={fhirServer}>
                {fhirServer}
              </option>
            ))}
          </Select>
        </div>
      )}

      {!showAdvanced && (
        <div>
          <Button
            className={`usa-button--unstyled margin-left-auto ${styles.searchCallToActionButton}`}
            type="button"
            onClick={() => setShowAdvanced(true)}
          >
            Advanced...
          </Button>
        </div>
      )}

      {/* Submit Button */}
      <div className="padding-top-6">
        <Button
          type="button"
          disabled={!selectedQuery}
          className={selectedQuery ? "usa-button" : "usa-button disabled"}
          onClick={handleSubmit}
        >
          Submit
        </Button>
      </div>
    </form>
  );
};

export default SelectSavedQuery;
