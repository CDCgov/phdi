import { evaluate } from "@/app/view-data/utils/evaluate";
import { evaluate as fhirPathEvaluate } from "fhirpath";

jest.mock("fhirpath", () => ({
  evaluate: jest.fn(),
}));

describe("evaluate", () => {
  afterEach(() => {
    // Clear the mock implementation and calls after each test
    jest.clearAllMocks();
  });
  it("fhirpath should be called 1 time when 1 call is made ", () => {
    evaluate({ id: "1234" }, "id");

    expect(fhirPathEvaluate).toHaveBeenCalledOnce();
  });
  it("should call fhirpath.evaluate 1 time when the same call is made 2 times", () => {
    evaluate({ id: "2345" }, "id");
    evaluate({ id: "2345" }, "id");

    expect(fhirPathEvaluate).toHaveBeenCalledOnce();
  });
  it("should call fhirpath.evaluate 2 time when the context is different", () => {
    evaluate({ id: "%id" }, "id", { id: 1 });
    evaluate({ id: "%id" }, "id", { id: 2 });

    expect(fhirPathEvaluate).toHaveBeenCalledTimes(2);
  });
});
