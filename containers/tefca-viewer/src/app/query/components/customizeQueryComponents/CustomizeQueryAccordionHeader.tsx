import { Icon } from "@trussworks/react-uswds";
import { DefinedValueSetCollection } from "../CustomizeQuery";
import customAccordionStyles from "./customizeQueryAccordion.module.css";

type CustomizeQueryAccordionProps = {
  selectedCount: number;
  handleSelectAllChange: (groupIndex: number, checked: boolean) => void;
  handleToggleExpand: () => void;
  groupIndex: number;
  group: DefinedValueSetCollection;
  isExpanded: boolean;
};

const CustomizeQueryAccordionHeader: React.FC<CustomizeQueryAccordionProps> = ({
  selectedCount,
  handleSelectAllChange,
  handleToggleExpand,
  groupIndex,
  group,
  isExpanded,
}) => {
  return (
    <div
      className="accordion-header display-flex flex-no-wrap flex-align-start"
      onClick={handleToggleExpand}
    >
      <div
        id="select-all"
        className={`hide-checkbox-label ${customAccordionStyles.checkboxLabel}`}
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
        {`${group.items[0].display}`}

        <span className="accordion-subtitle margin-top-2">
          <strong>Author:</strong> {group.author}{" "}
          <strong style={{ marginLeft: "20px" }}>System:</strong> {group.system}
        </span>
      </div>
      <span className="margin-left-auto">{`${selectedCount} selected`}</span>
      <div
        onClick={handleToggleExpand}
        className={`${customAccordionStyles.caret}`}
      >
        {isExpanded ? (
          <Icon.ExpandLess size={4} />
        ) : (
          <Icon.ExpandMore size={4} />
        )}
      </div>
    </div>
  );
};

export default CustomizeQueryAccordionHeader;
