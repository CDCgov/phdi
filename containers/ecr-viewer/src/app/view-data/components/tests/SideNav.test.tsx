import sideNav, { SectionConfig } from "@/app/view-data/components/SideNav";
import { render } from "@testing-library/react";
import { axe } from "jest-axe";

describe("SectionConfig", () => {
  it("should create an instance with correct title and id", () => {
    const section = new SectionConfig("Test Section");
    expect(section.title).toBe("Test Section");
    expect(section.id).toBe("test-section");
  });

  it("should handle subNavItems as strings and convert them to SectionConfig instances", () => {
    const section = new SectionConfig("Parent Section", ["Child Section"]);
    expect(section.subNavItems?.length).toBe(1);
    expect(section.subNavItems?.[0] instanceof SectionConfig).toBeTruthy();
    expect(section.subNavItems?.[0]?.title).toBe("Child Section");
  });

  it("should handle subNavItems as SectionConfig instances", () => {
    const childSection = new SectionConfig("Child Section");
    const section = new SectionConfig("Parent Section", [childSection]);
    expect(section.subNavItems?.length).toBe(1);
    expect(section.subNavItems?.[0]).toBe(childSection);
  });

  it("should match the snapshot", () => {
    const sections = [
      new SectionConfig("Section 1"),
      new SectionConfig("Section 2", ["Subsection 1"]),
    ];

    const { asFragment } = render(sideNav({ sectionConfigs: sections }));
    expect(asFragment()).toMatchSnapshot();
  });

  it("should have no accessibility violations", async () => {
    const sections = [
      new SectionConfig("Section 1"),
      new SectionConfig("Section 2", ["Subsection 1"]),
    ];

    const { container } = render(sideNav({ sectionConfigs: sections }));
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
