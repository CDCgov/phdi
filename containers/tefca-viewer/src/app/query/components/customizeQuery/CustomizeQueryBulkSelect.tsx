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
      <button
        className={`usa-button usa-button--unstyled ${styles.bulkSelectLink} `}
        disabled={allItemsSelected}
        onClick={(e) => {
          e.preventDefault();
          handleBulkSelectForTab(true);
        }}
      >
        Select all {activeTab}
      </button>
      <button
        className={`usa-button usa-button--unstyled ${styles.bulkSelectLink} `}
        disabled={allItemsDeselected}
        onClick={(e) => {
          e.preventDefault();
          handleBulkSelectForTab(false);
        }}
      >
        Deselect all {activeTab}
      </button>
    </div>
  );
};

export default CustomizeQueryBulkSelect;
