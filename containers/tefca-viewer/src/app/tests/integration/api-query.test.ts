/**
 * @jest-environment node
 */

import { GET } from "../../api/query/route";

describe("GET Health Check", () => {
  it("should return status OK", async () => {
    const response = await GET();
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.status).toBe("OK");
  });
});
