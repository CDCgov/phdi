import AccordionContainer from "../AccordionContainer";
import { screen, render } from "@testing-library/react";

describe("AccordionContainer", () => {
  it("should display all items", () => {
    render(
      <AccordionContainer
        accordionItems={[
          {
            title: "my heading",
            content: "my content",
            expanded: false,
            id: "123",
            headingLevel: "h3",
          },
        ]}
      />,
    );
    expect(screen.getByText("my content").id).toEqual("my-heading_1");
  });
});
