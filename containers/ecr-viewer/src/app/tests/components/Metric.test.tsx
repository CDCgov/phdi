import React from "react";
import { render } from "@testing-library/react";

jest.mock("../../view-data/component-utils", () => ({
  metrics: jest.fn(),
}));

import { metrics } from "../../view-data/component-utils";
import Metric from "@/app/view-data/components/Metric";

describe("ECRViewerPage", () => {
  it("calls metrics on beforeunload", () => {
    const metricsMock = metrics as jest.Mock;

    const { unmount } = render(<Metric fhirId={""} />);

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
