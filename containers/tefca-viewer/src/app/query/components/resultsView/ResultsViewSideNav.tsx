import React, { useCallback, useEffect, useState } from "react";
import { formatIdForAnchorTag } from "./ResultsViewTable";
import SideNav, { NavItem } from "../../designSystem/sideNav/SideNav";

export type NavSection = {
  title: string;
  subtitle?: string;
};

type ResultsViewSideNavProps = {
  items: NavSection[];
};
/**
 * ResultsViewSideNav component
 * @param root0 - params
 * @param root0.items - a list of nav items to display in the sidenav
 * @returns - The ResultsViewSideNav component
 */
const ResultsViewSideNav: React.FC<ResultsViewSideNavProps> = ({ items }) => {
  const [activeItem, setActiveItem] = useState(
    window.location.hash || formatIdForAnchorTag(items[0]?.title),
  );
  const hashChangeHandler = useCallback(() => {
    setActiveItem(window.location.hash);
  }, [window.location.hash]);
  useEffect(() => {
    window.addEventListener("hashchange", hashChangeHandler);
    return () => {
      window.removeEventListener("hashchange", hashChangeHandler);
    };
  }, []);

  const sideNavItems: NavItem[] = items.flatMap((item) => {
    const sectionId = formatIdForAnchorTag(item.title);
    if (item.subtitle) {
      const subSectionId = formatIdForAnchorTag(item.subtitle);
      return [
        {
          title: item.title,
          activeItem: activeItem.includes(sectionId),
        },
        {
          title: item.subtitle,
          activeItem: activeItem.includes(subSectionId),
          isSubNav: true,
        },
      ];
    } else {
      return {
        ...item,
        activeItem: activeItem.includes(sectionId),
      };
    }
  });

  return (
    <SideNav
      items={sideNavItems}
      containerClassName="resultsViewSideNav"
      sticky
    />
  );
};

export default ResultsViewSideNav;
