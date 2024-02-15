import SideNav, {
  SectionConfig,
  sortHeadings,
} from "@/app/view-data/components/SideNav";
import { render } from "@testing-library/react";
import { axe } from "jest-axe";

describe("SectionConfig", () => {
  beforeEach(() => {
    // IntersectionObserver isn't available in test environment
    const mockIntersectionObserver = jest.fn();
    mockIntersectionObserver.mockReturnValue({
      observe: () => null,
      unobserve: () => null,
      disconnect: () => null,
    });
    window.IntersectionObserver = mockIntersectionObserver;
  });

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
    const { asFragment } = render(
      <>
        <SideNav />
        <h2 id="section-1">Section 1</h2>
        <h2 id="section-2">Section 2</h2>
        <h3 id="section-3">Section 3</h3>
        <h4 id="section-4">Section 4</h4>
        <h2 id="section-2-2">Section 2 - 2</h2>
      </>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should have no accessibility violations", async () => {
    const { container } = render(<SideNav />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("should sort section headings", async () => {
    const headings = [
      {
        text: "foo",
        level: "h1",
        priority: 1,
      },
      {
        text: "bar",
        level: "h2",
        priority: 2,
      },
      {
        text: "biz",
        level: "h1",
        priority: 1,
      },
    ];
    const foo = new SectionConfig("foo", ["bar"]);
    const bar = new SectionConfig("biz");

    const result: SectionConfig[] = [foo, bar];
    const resultSub = result[0]?.subNavItems;
    const sortedResults = sortHeadings(headings);
    const sortedResultsSub = sortedResults[0]?.subNavItems;
    expect(sortedResults[0].id).toBe(result[0].id);
    expect(sortedResults[1].id).toBe(result[1].id);
    expect(sortedResultsSub ? sortedResultsSub[0].id : null).toBe(
      resultSub ? resultSub[0].id : undefined,
    );
  });

  it("should only render side nav items on page", async () => {
    const { container } = render(
      <>
        <SideNav />
        <h2 id="section-1">Section 1</h2>
        <h2 id="section-2">Section 2</h2>
        <h3 id="section-3">Section 3</h3>
        <h4 id="section-4">Section 4</h4>
        <h2 id="section-2-2">Section 2 - 2</h2>
      </>,
    );
    expect(container.innerHTML).toContain('<a href="#section-1" class="">');
  });
});
