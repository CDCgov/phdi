import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import SocialHistory from "../../view-data/components/SocialHistory";

describe("SocialHistory", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const socialAvailableData = [
      {
        title: "Occupation",
        value: "Nursing, psychiatric, and home health aides",
      },
      {
        title: "Tobacco Use",
        value: "Tobacco smoking consumption unknown",
      },
      {
        title: "Homeless Status",
        value: "unsatisfactory living conditions (finding)",
      },
      {
        title: "Occupation",
        value: "Nursing, psychiatric, and home health aides",
      },
      {
        title: "Sexual Orientation",
        value: "Do not know",
      },
    ];
    container = render(
      <SocialHistory socialData={socialAvailableData} />,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
