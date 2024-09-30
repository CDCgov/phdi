import styles from "../customizeQuery/customizeQuery.module.css";

type CustomizeQueryBulkSelectProps = {
  allItemsDeselected: boolean;
  allItemsSelected: boolean;
  handleBulkSelectForTab: (checked: boolean) => void;
  activeTab: string;
};
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
