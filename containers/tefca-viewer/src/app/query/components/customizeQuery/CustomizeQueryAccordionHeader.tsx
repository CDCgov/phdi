import { Icon } from "@trussworks/react-uswds";
import styles from "./customizeQuery.module.css";
import { DefinedValueSetCollection } from "../CustomizeQuery";

type CustomizeQueryAccordionProps = {
  selectedCount: number;
  handleSelectAllChange: (groupIndex: number, checked: boolean) => void;
  groupIndex: number;
  group: DefinedValueSetCollection;
};

/**
 * Rendering component for customize query header
 * @param param0 - props for rendering
 * @param param0.selectedCount - stateful tally of the number of selected valuesets
 * @param param0.handleSelectAllChange
 * Listner function to include all valuesets when checkbox is selected
 * @param param0.groupIndex - index corresponding to group
 * @param param0.group - matched concept containing all rendered valuesets
 * @returns A component that renders the customization query body
 */
const CustomizeQueryAccordionHeader: React.FC<CustomizeQueryAccordionProps> = ({
  selectedCount,
  handleSelectAllChange,
  groupIndex,
  group,
}) => {
  return (
    <div className="accordion-header display-flex flex-no-wrap flex-align-start customize-query-header">
      <div
        id="select-all"
        className={`hide-checkbox-label ${styles.customizeQueryCheckbox}`}
        onClick={(e) => {
          e.stopPropagation();
          handleSelectAllChange(
            groupIndex,
            selectedCount !== group.items.length
          );
        }}
      >
        {selectedCount === group.items.length && (
          <Icon.Check
            className="usa-icon bg-base-lightest"
            size={4}
            color="#565C65"
          />
        )}
        {selectedCount > 0 && selectedCount < group.items.length && (
          <Icon.Remove
            className="usa-icon bg-base-lightest"
            size={4}
            color="#565C65"
          />
        )}
      </div>
      <div>
        {`${group.valueset_name}`}

        <span className="accordion-subtitle margin-top-2">
          <strong>Author:</strong> {group.author}{" "}
          <strong style={{ marginLeft: "20px" }}>System:</strong> {group.system}
        </span>
      </div>
      <span className="margin-left-auto">{`${selectedCount} selected`}</span>
    </div>
  );
};

export default CustomizeQueryAccordionHeader;
