import { metrics } from "@/app/view-data/component-utils";
import fetchMock from "jest-fetch-mock";

fetchMock.enableMocks();

describe("Metrics", () => {
  beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    fetchMock.resetMocks();
  });

  it("calls fetch with the correct arguments", async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ ok: true }));

    const basePath = "https://example.com";
    const metricOptions = { key: "value" };

    await metrics(basePath, metricOptions);

    expect(fetch).toHaveBeenCalledWith(`${basePath}/api/metrics`, {
      body: JSON.stringify(metricOptions),
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
  });

  it("throws an error if the response is not ok", async () => {
    fetchMock.mockResponseOnce("", { status: 404 });

    const basePath = "https://example.com";
    const metricOptions = { key: "value" };

    await expect(metrics(basePath, metricOptions)).rejects.toThrow(
      "Sorry, we couldn't find this endpoint.",
    );
  });

  it("handles internal server error", async () => {
    fetchMock.mockResponseOnce("", {
      status: 500,
      statusText: "Internal Server Error",
    });

    const basePath = "https://example.com";
    const metricOptions = { key: "value" };

    await expect(metrics(basePath, metricOptions)).rejects.toThrow(
      "Internal Server Error",
    );
  });
});
