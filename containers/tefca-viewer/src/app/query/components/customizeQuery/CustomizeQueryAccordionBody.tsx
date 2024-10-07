import { Icon } from "@trussworks/react-uswds";
import styles from "./customizeQuery.module.css";
import { GroupedValueSet } from "./customizeQueryUtils";
import Table from "../../designSystem/Table";

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
    <Table className={`${styles.customizeQueryGridContainer}`}>
      <thead className={` margin-top-10`}>
        <tr className={styles.customizeQueryGridHeader}>
          <th className={`${styles.accordionTableHeader}`}>Include</th>
          <th className={`${styles.accordionTableHeader}`}>Code</th>
          <th className={`${styles.accordionTableHeader}`}>Display</th>
        </tr>
      </thead>
      <tbody className="display-flex flex-column">
        {group.items.map((item, index) => (
          <tr className={`${styles.customizeQueryGridRow}`} key={item.code}>
            <td
              className={`${styles.customizeQueryCheckbox}`}
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
            </td>
            <td className={styles.noBorderNoBackgroundNoPadding}>
              {item.code}
            </td>
            <td className={styles.noBorderNoBackgroundNoPadding}>
              {item.display}
            </td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default CustomizeQueryAccordionBody;
