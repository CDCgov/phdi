import React from "react";
import { render, screen } from "@testing-library/react";
import { DataDisplay, DataDisplayInfo } from "../../utils";

describe("DataDisplay Component", () => {
  it("should render the title and value", () => {
    const item: DataDisplayInfo = {
      title: "Test Title",
      value: "Test Value",
    };

    render(<DataDisplay item={item} />);

    // Check if title is rendered
    expect(screen.getByText("Test Title")).toBeInTheDocument();

    // Check if value is rendered
    expect(screen.getByText("Test Value")).toBeInTheDocument();
  });

  it("should apply the provided className", () => {
    const item: DataDisplayInfo = {
      title: "Test Title",
      value: "Test Value",
    };
    const className = "custom-class";

    render(<DataDisplay item={item} className={className} />);

    // Check if the className is applied to the inner container
    expect(screen.getByText("Test Value")).toHaveClass("custom-class");
    expect(screen.getByText("Test Value").parentElement).toHaveClass(
      "grid-row",
    );
  });

  it("should render React elements as value", () => {
    const item: DataDisplayInfo = {
      title: "Test Title",
      value: <span data-testid="custom-element">Custom Element</span>,
    };

    render(<DataDisplay item={item} />);

    // Check if the custom React element is rendered
    expect(screen.getByTestId("custom-element")).toBeInTheDocument();
  });

  it("should render an array of React elements as value", () => {
    const item: DataDisplayInfo = {
      title: "Test Title",
      value: [
        <span key="1" data-testid="element-1">
          Element 1
        </span>,
        <span key="2" data-testid="element-2">
          Element 2
        </span>,
      ],
    };

    render(<DataDisplay item={item} />);

    // Check if the array of React elements is rendered
    expect(screen.getByTestId("element-1")).toBeInTheDocument();
    expect(screen.getByTestId("element-2")).toBeInTheDocument();
  });
});
