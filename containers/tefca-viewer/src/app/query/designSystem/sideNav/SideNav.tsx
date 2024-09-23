import { SideNav as UswdsSideNav } from "@trussworks/react-uswds";
import { formatIdForAnchorTag } from "../../components/resultsViewAccordion/ResultsViewTable";
import { ReactNode } from "react";
import styles from "./sidenav.module.css";

export type NavItem = {
  title: string;
  activeItem: boolean;
  isSubNav?: boolean;
  navItemClassName?: string;
};

export type SideNavProps = {
  items: NavItem[];
  containerClassName?: string;
  sticky?: boolean;
};

/**
 *
 * @param root0
 * @param root0.items
 * @param root0.containerClassName
 * @param root0.sticky
 */
const SideNav: React.FC<SideNavProps> = ({
  items,
  containerClassName,
  sticky = false,
}) => {
  const sideNavItems: ReactNode[] = [];
  for (let item of items) {
    const sideNavItem = buildSectionMarkUp(
      item.title,
      item.activeItem,
      item.navItemClassName,
    );
    sideNavItems.push(
      <div className={styles.subItem}>
        <UswdsSideNav items={[sideNavItem]} isSubnav={item.isSubNav} />
      </div>,
    );
  }
  return (
    <nav
      className={`${styles.container} ${containerClassName ?? ""} ${
        sticky ? styles.sticky : ""
      }`}
    >
      <UswdsSideNav items={sideNavItems} />
    </nav>
  );
};

function buildSectionMarkUp(
  title: string,
  activeItem: boolean,
  className?: string,
): ReactNode {
  let sectionId = formatIdForAnchorTag(title);
  let sideNavItem = (
    <a
      key={sectionId}
      href={"#" + sectionId}
      className={`${styles.item} ${className} ${
        activeItem ? `usa-current` : ""
      }`}
    >
      {title}
    </a>
  );
  return sideNavItem;
}

export default SideNav;
