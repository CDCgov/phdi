import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import ListECRViewer from "@/app/components/ListEcrViewer";
import userEvent, { UserEvent } from "@testing-library/user-event";

const mockPush = jest.fn();
const mockSearchParams = new URLSearchParams();
jest.mock("next/navigation", () => {
  return {
    useRouter: () => ({
      push: mockPush,
    }),
    useSearchParams: () => mockSearchParams,
    usePathname: () => "",
  };
});

describe("Home Page, ListECRViewer", () => {
  let container: HTMLElement;
  beforeAll(() => {
    container = render(
      <ListECRViewer totalCount={100}>
        <br />
      </ListECRViewer>,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});

describe("Pagination for home page", () => {
  let user: UserEvent;

  beforeEach(() => {
    user = userEvent.setup();
    jest.resetAllMocks();
  });

  it("should have 4 pages when there are 100 and default page length is used", async () => {
    render(
      <ListECRViewer totalCount={100}>
        <br />
      </ListECRViewer>,
    );

    expect(screen.getByText("1"));
    expect(screen.getByText("2"));
    expect(screen.getByText("3"));
    expect(screen.getByText("4"));
    expect(screen.queryByText("5")).not.toBeInTheDocument();
    expect(screen.getByText("Showing 1-25 of 100 eCRs"));
  });

  it("should only update the route once on load", () => {
    render(
      <ListECRViewer totalCount={100}>
        <br />
      </ListECRViewer>,
    );
    expect(mockPush).toHaveBeenCalledExactlyOnceWith("?itemsPerPage=25");
  });

  it("should display 50 per page when items per page is set to 50", async () => {
    jest.spyOn(Storage.prototype, "setItem");

    render(
      <ListECRViewer totalCount={100}>
        <br />
      </ListECRViewer>,
    );
    await user.selectOptions(screen.getByTestId("Select"), ["50"]);

    expect(screen.getByText("1"));
    expect(screen.getByText("2"));
    expect(screen.getByText("Showing 1-50 of 100 eCRs"));
    expect(mockPush).toHaveBeenLastCalledWith("?itemsPerPage=50");
  });

  it("should update local storage when items per page is set to 50", async () => {
    jest.spyOn(Storage.prototype, "setItem");
    render(
      <ListECRViewer totalCount={100}>
        <br />
      </ListECRViewer>,
    );

    await user.selectOptions(screen.getByTestId("Select"), ["50"]);

    expect(localStorage.setItem).toHaveBeenCalledWith(
      "userPreferences",
      JSON.stringify({ itemsPerPage: 50 }),
    );
  });

  it("should load 50 items per page if 50 was previously set", () => {
    const spyLocalStorage = jest.spyOn(Storage.prototype, "getItem");
    spyLocalStorage.mockImplementationOnce(() =>
      JSON.stringify({ itemsPerPage: 50 }),
    );
    render(
      <ListECRViewer totalCount={100}>
        <br />
      </ListECRViewer>,
    );

    expect(screen.getByText("Showing 1-50 of 100 eCRs")).toBeInTheDocument();
    expect(mockPush).toHaveBeenLastCalledWith("?itemsPerPage=50");
  });

  it("should display 51-51 on third page", async () => {
    mockSearchParams.set("page", "3");
    render(
      <ListECRViewer totalCount={51}>
        <br />
      </ListECRViewer>,
    );

    expect(screen.getByText("Showing 51-51 of 51 eCRs")).toBeInTheDocument();
  });
});
