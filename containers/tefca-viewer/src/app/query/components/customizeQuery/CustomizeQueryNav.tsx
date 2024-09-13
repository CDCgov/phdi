import { GroupedValueSetKey } from "../CustomizeQuery";
import styles from "./customizeQuery.module.css";

type CustomizeQueryNavProps = {
  activeTab: string;
  handleTabChange: (tabName: GroupedValueSetKey) => void;
  handleSelectAllForTab: (checked: boolean) => void;
};
/**
 *
 * @param root0
 * @param root0.handleTabChange
 * @param root0.activeTab
 * @param root0.handleSelectAllForTab
 */
const CustomizeQueryNav: React.FC<CustomizeQueryNavProps> = ({
  handleTabChange,
  activeTab,
  handleSelectAllForTab,
}) => {
  return (
    <>
      <nav className={`${styles.usaNav} ${styles.customizeQueryNav}`}>
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
      <a
        href="#"
        className="include-all-link"
        onClick={(e) => {
          e.preventDefault();
          handleSelectAllForTab(true);
        }}
      >
        Include all {activeTab}
      </a>
    </>
  );
};

export default CustomizeQueryNav;
