describe("Happy Path", () => {
  it("Should load the eCR Viewer for a known ID", () => {
    // Visit a valid URL
    cy.visit(
      "http://localhost:3000/view-data?id=6100896d-b520-497c-b2fe-1c111c679274",
    );

    // Gets the expected content
    cy.get("#patient-summary").contains("Patient Summary");
    cy.contains("VICTORIA HUNTER");
  });
});

describe("Failing Path", () => {
  it("Should return an error when given an invalid ID", () => {
    //Visit an invalid URL
    cy.visit("http://localhost:3000/view-data?id=123");

    cy.contains("Sorry, we couldn't find this eCR ID.");
  });
});
