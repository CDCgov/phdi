import { Icon } from "@trussworks/react-uswds";
import styles from "./customizeQuery.module.css";
import { GroupedValueSet } from "./customizeQueryUtils";

type CustomizeQueryAccordionBodyProps = {
  group: GroupedValueSet;
  toggleInclude: (groupIndex: string, itemIndex: number) => void;
  groupIndex: string;
};

/**
 * Styling component to render the body table for the customize query components
 * @param param0 - props for rendering
 * @param param0.group - Matched concept associated with the query that
 * contains valuesets to filter query on
 * @param param0.toggleInclude - Listener event to handle a valueset inclusion/
 * exclusion check
 * @param param0.groupIndex - Index corresponding to group
 * @returns JSX Fragment for the accordion body
 */
const CustomizeQueryAccordionBody: React.FC<
  CustomizeQueryAccordionBodyProps
> = ({ group, toggleInclude, groupIndex }) => {
  return (
    <div className={`${styles.customizeQueryAccordion__body}`}>
      <div className={`${styles.customizeQueryGridContainer}`}>
        <div className={`${styles.customizeQueryGridHeader} margin-top-10`}>
          <div className={`${styles.accordionTableHeader}`}>Include</div>
          <div className={`${styles.accordionTableHeader}`}>Code</div>
          <div className={`${styles.accordionTableHeader}`}>Display</div>
        </div>
        <div className="display-flex flex-column">
          {group.items.map((item, index) => (
            <div className={`${styles.customizeQueryGridRow}`} key={item.code}>
              <div
                className={`${styles.customizeQueryCheckbox} ${styles.customizeQueryCheckbox} ${styles.hideCheckboxLabel}`}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleInclude(groupIndex, index);
                }}
              >
                {item.include && (
                  <Icon.Check
                    className="usa-icon"
                    style={{ backgroundColor: "white" }}
                    size={4}
                    color="#005EA2"
                  />
                )}
              </div>
              <div>{item.code}</div>
              <div>{item.display}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CustomizeQueryAccordionBody;
