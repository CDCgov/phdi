describe("Happy Path", () => {
  it("Should load the eCR Viewer for a known ID", () => {
    // Visit a valid URL
    const basePath = Cypress.env("BASE_PATH") || "";
    cy.visit(
      `${basePath}/view-data?id=1.2.840.114350.1.13.478.3.7.8.688883.230886`,
    );

    // Gets the expected content
    cy.get("#patient-summary").contains("Patient Summary");
    cy.contains("APPLE ZTEST");
  });
});

describe("Failing Path", () => {
  it("Should return an error when given an invalid ID", () => {
    // Visit an invalid URL
    const basePath = Cypress.env("BASE_PATH") || "";
    cy.visit(`${basePath}/view-data?id=123`);

    cy.contains("Sorry, we couldn't find this eCR ID.");
  });
});
