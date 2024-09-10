import { ValueSetItem } from "@/app/constants";
import { Icon } from "@trussworks/react-uswds";

import styles from "./customQueryResultsTable.module.scss";

type CustomQueryResultTableProps = {
  items: ValueSetItem[];
  toggleInclude: (index: number) => void;
};

const CustomQueryResultTable: React.FC<CustomQueryResultTableProps> = ({
  items,
  toggleInclude,
}) => {
  return (
    <>
      <div className={`${styles.customizeQueryContainer} border-0"`}>
        <div className={`${styles.customizeQueryGridHeader} margin-top-10`}>
          <div className={styles.accordionTableHeader}>Include</div>
          <div className={styles.accordionTableHeader}>Code</div>
          <div className={styles.accordionTableHeader}>Display</div>
        </div>
        <div className={styles.customizeQueryGridBody}>
          {items.map((item, index) => (
            <div className={styles.customizeQueryGridRow} key={item.code}>
              <div
                className={`hide-checkbox-label ${styles.valueSetCheckbox}`}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleInclude(index);
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
    </>
  );
};

export default CustomQueryResultTable;
