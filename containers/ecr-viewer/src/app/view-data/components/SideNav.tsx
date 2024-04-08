import React, { useState, useEffect } from "react";
import { SideNav as UswdsSideNav } from "@trussworks/react-uswds";

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

interface HeadingObject {
  text: string;
  level: string;
  priority: number;
}

const headingLevels = ["h1", "h2", "h3", "h4", "h5", "h6"];
const headingSelector =
  "h2:not(.unavailable-info):not(.side-nav-ignore), h3:not(.unavailable-info):not(.side-nav-ignore), h4:not(.unavailable-info):not(.side-nav-ignore)";

/**
 *
 * @param array
 */
function countObjects(array: SectionConfig[]): number {
  let count = 0;

  /**
   *
   * @param item
   */
  function countRecursively(item: SectionConfig): void {
    count++;
    if (item.subNavItems) {
      item.subNavItems.forEach((subHead) => countRecursively(subHead));
    }
  }

  array.forEach((item) => countRecursively(item));

  return count;
}

//Creates a SectionConfig list. Nests headings in each section config
export const sortHeadings = (headings: HeadingObject[]): SectionConfig[] => {
  const result: SectionConfig[] = [];
  let headingIndex = 0;
  while (headingIndex < headings.length) {
    const currentHeading = headings[headingIndex];
    const nextHeadings = headings.slice(headingIndex + 1);
    if (
      nextHeadings.length > 0 &&
      nextHeadings[0].priority > currentHeading.priority
    ) {
      const nestedResult = sortHeadings(nextHeadings);
      result.push(new SectionConfig(currentHeading.text, nestedResult));
      const nestedLength = countObjects(nestedResult);
      headingIndex += nestedLength + 1;
    } else if (
      nextHeadings.length > 0 &&
      nextHeadings[0].priority == currentHeading.priority
    ) {
      result.push(new SectionConfig(currentHeading.text));
      headingIndex++;
    } else if (
      nextHeadings.length > 0 &&
      nextHeadings[0].priority < currentHeading.priority
    ) {
      result.push(new SectionConfig(currentHeading.text));
      headingIndex += headings.length + 1;
    } else {
      result.push(new SectionConfig(currentHeading.text));
      headingIndex++;
    }
  }
  return result;
};

const SideNav: React.FC = () => {
  const [sectionConfigs, setSectionConfigs] = useState<SectionConfig[]>([]);
  const [activeSection, setActiveSection] = useState<string>("");

  useEffect(() => {
    // Select all heading tags on the page
    const headingElements = document.querySelectorAll(headingSelector);

    // Extract the text content from each heading and store it in the state
    const headings: HeadingObject[] = Array.from(headingElements).map(
      (heading) => {
        return {
          text: heading.textContent || "",
          level: heading.tagName.toLowerCase(),
          priority: headingLevels.findIndex(
            (level) => heading.tagName.toLowerCase() == level,
          ),
        };
      },
    );
    let sortedHeadings: SectionConfig[] = sortHeadings(headings);
    setSectionConfigs(sortedHeadings);

    let options = {
      root: null,
      rootMargin: "0px 0px -80% 0px",
      threshold: 0.8,
    };

    let observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          let id =
            entry.target.id || entry.target.querySelectorAll("span")[0]?.id;
          setActiveSection(id);
        }
      });
    }, options);
    headingElements.forEach((element) => observer.observe(element));
  }, []);

  /**
   *
   * @param sectionConfigs
   */
  function buildSideNav(sectionConfigs: SectionConfig[]) {
    let sideNavItems: React.ReactNode[] = [];
    for (let section of sectionConfigs) {
      let sideNavItem = (
        <a
          key={section.id}
          href={"#" + section.id}
          className={activeSection === section.id ? "usa-current" : ""}
        >
          {section.title}
        </a>
      );
      sideNavItems.push(sideNavItem);

      if (section.subNavItems) {
        let subSideNavItems = buildSideNav(section.subNavItems);
        sideNavItems.push(
          <UswdsSideNav isSubnav={true} items={subSideNavItems} />,
        );
      }
    }

    return sideNavItems;
  }

  let sideNavItems = buildSideNav(sectionConfigs);

  return <UswdsSideNav items={sideNavItems} />;
};

export default SideNav;
