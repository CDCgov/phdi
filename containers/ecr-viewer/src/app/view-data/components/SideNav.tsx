import React, { useState, useEffect } from "react";
import { SideNav as UswdsSideNav } from "@trussworks/react-uswds";
import { formatString } from "@/app/services/formatService";
import classNames from "classnames";
import { BackButton } from "./BackButton";

export class SectionConfig {
  title: string;
  id: string;
  subNavItems?: SectionConfig[];

  constructor(title: string, subNavItems?: string[] | SectionConfig[]) {
    this.title = title;
    this.id = formatString(title);

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
 * Counts the total number of `SectionConfig` objects within a given array, including those nested
 * within `subNavItems` properties.
 * @param sectionConfigs - An array of `SectionConfig` objects, each potentially containing
 *   a `subNavItems` property with further `SectionConfig` objects.
 * @returns The total count of `SectionConfig` objects within the array, including all nested
 * objects within `subNavItems`.
 */
export function countObjects(sectionConfigs: SectionConfig[]): number {
  let count = 0;
  sectionConfigs.forEach((config) => (count += countRecursively(config, 0)));

  return count;
}

/**
 * Recursively counts the number of `SectionConfig` objects, including any nested objects within
 * `subNavItems`.
 * @param config - The `SectionConfig` object to be counted. This object may contain
 *   `subNavItems`, which are also `SectionConfig` objects and will be recursively counted.
 * @param count - The initial count of `SectionConfig` objects. Typically starts at 0 and
 *   increments as the function processes each item and its `subNavItems`.
 * @returns The total count of `SectionConfig` objects, including all nested `subNavItems`.
 */
function countRecursively(config: SectionConfig, count: number): number {
  count += 1;
  if (config.subNavItems) {
    config.subNavItems.forEach(
      (subHead) => (count += countRecursively(subHead, 0)),
    );
  }
  return count;
}

/**
 * Sorts an array of `HeadingObject` instances into a structured array of `SectionConfig` objects.
 * The sorting is based on the `priority` property of each heading, arranging them into a hierarchy
 * where headings of lower priority become nested within those of higher priority. This function
 * recursively processes headings to construct a nested structure, encapsulated as `SectionConfig`
 * instances, which may contain other `SectionConfig` objects as nested sections.
 *
 * The function evaluates each heading in sequence and determines its placement in the result based
 * on its priority relative to subsequent headings. Headings with the same priority are placed at the
 * same level, while a heading with a lower priority than its predecessor is nested within the previous
 * heading's section.
 * @param headings - An array of heading objects to be sorted. Each `HeadingObject`
 *   must have a `text` property for the section title and a
 *   `priority` property that determines the heading's hierarchical level.
 * @returns An array of `SectionConfig` objects representing the structured hierarchy
 *   of headings. Each `SectionConfig` may contain nested `SectionConfig` objects
 *   if the original headings array indicated a nested structure based on priorities.
 */
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

/**
 * Functional component for the side navigation.
 * @returns The JSX element representing the side navigation.
 */
const SideNav: React.FC = () => {
  const [sectionConfigs, setSectionConfigs] = useState<SectionConfig[]>([]);
  const [activeSection, setActiveSection] = useState<string>("");
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";

  useEffect(() => {
    // Select all heading tags on the page
    const headingElements = document.querySelectorAll(headingSelector);
    // Extract the text content from each heading and store it in the state
    const headings: HeadingObject[] = Array.from(headingElements).map(
      (heading) => {
        const sectionId =
          heading && heading.textContent
            ? formatString(heading.textContent)
            : null;
        if (sectionId) {
          heading.setAttribute("data-sectionid", sectionId);
        }
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
      rootMargin: "0px 0px -85% 0px",
      threshold: 0.9,
    };

    let observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          let id = entry.target.getAttribute("data-sectionid") || null;
          if (id) {
            setActiveSection(id);
          }
        }
      });
    }, options);
    headingElements.forEach((element) => observer.observe(element));
  }, []);

  /**
   * Constructs a side navigation menu as an array of React nodes based on the provided section configurations.
   * @param sectionConfigs - An array of `SectionConfig` objects that describe the sections
   *   and potential sub-sections of the side navigation. Each `SectionConfig`
   *   should have an `id` for linking, a `title` for display, and may have
   *   `subNavItems` for nested navigation structures.
   * @returns An array of React nodes representing the side navigation items, including any
   *   nested sub-navigation items. These nodes are ready to be rendered in a React
   *   component to display the side navigation.
   */
  function buildSideNav(sectionConfigs: SectionConfig[]) {
    let sideNavItems: React.ReactNode[] = [];
    for (let section of sectionConfigs) {
      let sideNavItem = (
        <a
          onClick={() => {
            setTimeout(() => {
              setActiveSection(section.id);
            }, 500);
          }}
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

  return (
    <nav
      className={classNames("nav-wrapper", {
        "top-0": !isNonIntegratedViewer,
        "top-550": isNonIntegratedViewer,
      })}
    >
      <BackButton />
      <UswdsSideNav items={sideNavItems} />
    </nav>
  );
};

export default SideNav;
