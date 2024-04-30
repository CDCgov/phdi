import { processSnomedCode } from "../view-data/service";

describe("view-data service", () => {
  //PLACEHOLDER TEST REPLACE ME WITH SOMETHING REAL
  it("processSnomedCode returns the snomed code it is given", () => {
    const testSnomedCode = "Lola the stinky dog";

    const result = processSnomedCode(testSnomedCode);

    expect(result).toEqual(testSnomedCode);
  });
  //PLACEHOLDER TEST REPLACE ME WITH SOMETHING REAL
});
