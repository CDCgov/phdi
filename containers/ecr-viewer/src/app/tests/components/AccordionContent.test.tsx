import React from "react";
import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { Bundle } from "fhir/r4";
import { loadYamlConfig } from "@/app/api/utils";
import AccordionContent from "@/app/view-data/components/AccordionContent";

const mappings = loadYamlConfig();

describe("Snapshot test for Accordion Content", () => {
  it("Given no data, info message for empty sections should appear", async () => {
    const bundleEmpty: Bundle = {
      resourceType: "Bundle",
      type: "batch",
      entry: [],
    };

    let { container } = render(
      <AccordionContent fhirBundle={bundleEmpty} fhirPathMappings={mappings} />,
    );

    expect(await axe(container)).toHaveNoViolations();
    container.querySelectorAll("[id], [aria-describedby]").forEach((el) => {
      el.removeAttribute("id");
      el.removeAttribute("aria-describedby");
    });
    expect(container).toMatchSnapshot();

    expect(
      screen.getByText("No patient information was found in this eCR."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No encounter information was found in this eCR."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No clinical information was found in this eCR."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No lab information was found in this eCR."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No eCR metadata was found in this eCR."),
    ).toBeInTheDocument();
  });
});
