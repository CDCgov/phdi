import styles from "../customizeQuery/customizeQuery.module.css";

type CustomizeQueryBulkSelectProps = {
  allItemsDeselected: boolean;
  allItemsSelected: boolean;
  handleBulkSelectForTab: (checked: boolean) => void;
  activeTab: string;
};
/**
 *
 * @param root0 - params
 * @param root0.allItemsDeselected - boolean used for the deselect toggle
 * @param root0.allItemsSelected - boolean used for the select toggle
 * @param root0.handleBulkSelectForTab - handler function for the link toggles
 * @param root0.activeTab - which tab is currently selected
 * @returns bulk select link selection
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
