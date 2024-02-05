import React from "react";
import { SideNav } from "@trussworks/react-uswds";

export class SectionConfig {
  title: string;
  id: string;
  subNavItems?: SectionConfig[];

  constructor(title: string, subNavItems?: string[] | SectionConfig[]) {
    this.title = title;
    this.id = title.toLowerCase().replace(/\s+/g, "-");

    if (subNavItems) {
      this.subNavItems = subNavItems.map((item) => {
        if (typeof item === "string") {
          return new SectionConfig(item);
        } else {
          return item;
        }
      });
    }
  }
}

const sideNav = ({ sectionConfigs }: { sectionConfigs: SectionConfig[] }) => {
  function buildSideNav(sectionConfigs: SectionConfig[]) {
    let sideNavItems: React.ReactNode[] = [];
    for (let section of sectionConfigs) {
      let sideNavItem = <a href={"#" + section.id}>{section.title}</a>;
      sideNavItems.push(sideNavItem);

      if (section.subNavItems) {
        let subSideNavItems = buildSideNav(section.subNavItems);
        sideNavItems.push(<SideNav isSubnav={true} items={subSideNavItems} />);
      }
    }

    return sideNavItems;
  }

  function createSubSideNavItem(sectionConfig: SectionConfig[]) {
    let subItems: React.ReactNode[] = sectionConfig.map((item) => {
      return <a href={"#" + item.id}>{item.title}</a>;
    });

    return <SideNav isSubnav={true} items={subItems} />;
  }

  let sideNavItems = buildSideNav(sectionConfigs);

  return <SideNav items={sideNavItems} />;
};

export default sideNav;
