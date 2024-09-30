import { ValueSetType } from "@/app/constants";
import styles from "./customizeQuery.module.css";
import CustomizeQueryBulkSelect from "./CustomizeQueryBulkSelect";
import { GroupedValueSet } from "./customizeQueryUtils";

type CustomizeQueryNavProps = {
  activeTab: ValueSetType;
  handleTabChange: (tabName: ValueSetType) => void;
  handleSelectAllForTab: (checked: boolean) => void;
  valueSetOptions: {
    [key in ValueSetType]: { [vsNameAuthorSystem: string]: GroupedValueSet };
  };
};

/**
 * Nav component for customize query page
 * @param param0 - props for rendering
 * @param param0.handleTabChange - listener event for tab selection
 * @param param0.activeTab - currently active tab
 * @param param0.handleSelectAllForTab - Listener function to grab all the
 * returned labs when the select all button is hit
 * @param param0.valueSetOptions - the selected ValueSet items
 * @returns Nav component for the customize query page
 */
const CustomizeQueryNav: React.FC<CustomizeQueryNavProps> = ({
  handleTabChange,
  activeTab,
  handleSelectAllForTab,
  valueSetOptions,
}) => {
  const hasSelectableItems = Object.values(valueSetOptions[activeTab]).some(
    (group) => group.items.length > 0,
  );
  const allItemsDeselected = Object.values(valueSetOptions[activeTab])
    .flatMap((groupedValSets) => groupedValSets.items.flatMap((i) => i.include))
    .every((p) => !p);

  const allItemsSelected = Object.values(valueSetOptions[activeTab])
    .flatMap((groupedValSets) => groupedValSets.items.flatMap((i) => i.include))
    .every((p) => p);

  return (
    <>
      <nav className={`${styles.customizeQueryNav}`}>
        <ul className="usa-sidenav">
          <li className={`usa-sidenav_item`}>
            <a
              href="#labs"
              className={`${
                activeTab === "labs" ? `${styles.currentTab}` : ""
              }`}
              onClick={() => handleTabChange("labs")}
            >
              Labs
            </a>
          </li>
          <li className={`usa-sidenav_item`}>
            <a
              className={`${
                activeTab === "medications" ? `${styles.currentTab}` : ""
              }`}
              href="#medications"
              onClick={() => handleTabChange("medications")}
            >
              Medications
            </a>
          </li>
          <li className={`usa-sidenav_item`}>
            <a
              className={`${
                activeTab === "conditions" ? `${styles.currentTab}` : ""
              }`}
              href="#conditions"
              onClick={() => handleTabChange("conditions")}
            >
              Conditions
            </a>
          </li>
        </ul>
      </nav>

      <ul className="usa-nav__primary usa-accordion"></ul>
      <hr className="custom-hr"></hr>
      {hasSelectableItems ? (
        <CustomizeQueryBulkSelect
          allItemsDeselected={allItemsDeselected}
          allItemsSelected={allItemsSelected}
          handleBulkSelectForTab={handleSelectAllForTab}
          activeTab={activeTab}
        />
      ) : (
        <div className="font-sans-sm text-light padding-y-3">
          No {activeTab} available for this query.
        </div>
      )}
    </>
  );
};

export default CustomizeQueryNav;
