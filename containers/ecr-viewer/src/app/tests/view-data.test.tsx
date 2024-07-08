import React from "react";
import { render } from "@testing-library/react";
import ECRViewerPage from "../view-data/page";

jest.mock("../view-data/component-utils", () => ({
  metrics: jest.fn(),
}));

jest.mock("../view-data/components/LoadingComponent", () => ({
  EcrLoadingSkeleton: () => <div>Loading...</div>,
}));

import { metrics } from "../view-data/component-utils";

describe("ECRViewerPage", () => {
  it("calls metrics on beforeunload", () => {
    const metricsMock = metrics as jest.Mock;

    const { unmount } = render(<ECRViewerPage />);

    // Create a fake event
    const event = new Event("beforeunload");
    // Trigger the beforeunload event
    window.dispatchEvent(event);

    // Verify that the metrics function was called

    expect(metricsMock).toHaveBeenCalledWith("", {
      fhirId: "",
      startTime: expect.any(Number),
      endTime: expect.any(Number),
    });

    unmount(); // Clean up
  });
});
