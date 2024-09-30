import { ValueSetType } from "@/app/constants";
import styles from "./customizeQuery.module.css";

type CustomizeQueryNavProps = {
  activeTab: string;
  handleTabChange: (tabName: ValueSetType) => void;
  handleSelectAllForTab: (checked: boolean) => void;
  hasItemsInTab: boolean;
};

/**
 * Nav component for customize query page
 * @param param0 - props for rendering
 * @param param0.handleTabChange - listener event for tab selection
 * @param param0.activeTab - currently active tab
 * @param param0.handleSelectAllForTab - Listener function to grab all the
 * returned labs when the select all button is hit
 * @param param0.hasItemsInTab - Boolean indicating if there are items in the current tab
 * @returns Nav component for the customize query page
 */
const CustomizeQueryNav: React.FC<CustomizeQueryNavProps> = ({
  handleTabChange,
  activeTab,
  handleSelectAllForTab,
  hasItemsInTab,
}) => {
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
      {hasItemsInTab ? (
        <a
          href="#"
          type="button"
          className="include-all-link"
          onClick={(e) => {
            e.preventDefault();
            handleSelectAllForTab(true);
          }}
        >
          Include all {activeTab}
        </a>
      ) : (
        <div className="font-sans-sm text-light padding-y-3">
          No {activeTab} available for this query.
        </div>
      )}
    </>
  );
};

export default CustomizeQueryNav;
