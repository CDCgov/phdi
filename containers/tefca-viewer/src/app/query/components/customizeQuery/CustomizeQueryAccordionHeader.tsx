import { Icon } from "@trussworks/react-uswds";
import styles from "./customizeQuery.module.css";
import { GroupedValueSet } from "./customizeQueryUtils";

type CustomizeQueryAccordionProps = {
  handleSelectAllChange: (groupIndex: string, checked: boolean) => void;
  groupIndex: string;
  group: GroupedValueSet;
};

/**
 * Rendering component for customize query header
 * @param param0 - props for rendering
 * @param param0.handleSelectAllChange
 * Listner function to include all valuesets when checkbox is selected
 * @param param0.groupIndex - index corresponding to group
 * @param param0.group - matched concept containing all rendered valuesets
 * @returns A component that renders the customization query body
 */
const CustomizeQueryAccordionHeader: React.FC<CustomizeQueryAccordionProps> = ({
  handleSelectAllChange,
  groupIndex,
  group,
}) => {
  const selectedTotal = group.items.length;
  const selectedCount = group.items.filter((item) => item.include).length;

  return (
    <div
      className={`${styles.accordionHeader} display-flex flex-no-wrap flex-align-start customize-query-header`}
    >
      <div
        id="select-all"
        className={`hide-checkbox-label ${styles.customizeQueryCheckbox}`}
        onClick={(e) => {
          e.stopPropagation();
          handleSelectAllChange(
            groupIndex,
            selectedCount !== group.items.length,
          );
        }}
      >
        {selectedCount === group.items.length && (
          <Icon.Check
            className="usa-icon bg-base-lightest"
            size={4}
            color="#565C65"
            aria-label="Checkmark icon indicating addition"
          />
        )}
        {selectedCount > 0 && selectedCount < group.items.length && (
          <Icon.Remove
            className="usa-icon bg-base-lightest"
            size={4}
            color="#565C65"
            aria-label="Minus icon indicating removal"
          />
        )}
      </div>
      <div className={`${styles.accordionButtonTitle}`}>
        {`${group.valueSetName}`}

        <span className={`${styles.accordionSubtitle} margin-top-2`}>
          <strong>Author:</strong> {group.author}{" "}
          <strong style={{ marginLeft: "20px" }}>System:</strong> {group.system}
        </span>
      </div>
      <span className="margin-left-auto">{`${selectedCount} of ${selectedTotal} selected`}</span>
    </div>
  );
};

export default CustomizeQueryAccordionHeader;
