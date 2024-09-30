import styles from "../customizeQuery/customizeQuery.module.css";

type CustomizeQueryBulkSelectProps = {
  allItemsDeselected: boolean;
  allItemsSelected: boolean;
  handleBulkSelectForTab: (checked: boolean) => void;
  activeTab: string;
};
/**
 *
 * @param root0
 * @param root0.allItemsDeselected
 * @param root0.allItemsSelected
 * @param root0.handleBulkSelectForTab
 * @param root0.activeTab
 */
const CustomizeQueryBulkSelect: React.FC<CustomizeQueryBulkSelectProps> = ({
  allItemsDeselected,
  allItemsSelected,
  handleBulkSelectForTab,
  activeTab,
}) => {
  return (
    <div className="display-flex">
      {!allItemsSelected && (
        <button
          className={`usa-button usa-button--unstyled ${styles.bulkSelectLink} `}
          onClick={(e) => {
            e.preventDefault();
            handleBulkSelectForTab(true);
          }}
        >
          Select all {activeTab}
        </button>
      )}
      {!allItemsDeselected && (
        <button
          className={`usa-button usa-button--unstyled ${styles.bulkSelectLink} `}
          onClick={(e) => {
            e.preventDefault();
            handleBulkSelectForTab(false);
          }}
        >
          Deselect all {activeTab}
        </button>
      )}
    </div>
  );
};

export default CustomizeQueryBulkSelect;
