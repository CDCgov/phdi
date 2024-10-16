describe("Happy Path", () => {
  it("Should load the eCR Viewer for a known ID", () => {
    // Visit a valid URL
    const basePath = Cypress.env("BASE_PATH") || "";
    cy.visit(`${basePath}/view-data?id=6100896d-b520-497c-b2fe-1c111c679274`);

    // Gets the expected content
    cy.get("#patient-summary").contains("Patient Summary");
    cy.contains("VICTORIA HUNTER");
    cy.contains(basePath);
  });
});

describe("Failing Path", () => {
  it("Should return an error when given an invalid ID", () => {
    // Visit an invalid URL
    const basePath = Cypress.env("BASE_PATH") || "";
    cy.visit(`${basePath}/view-data?id=123`);

    cy.contains("Sorry, we couldn't find this eCR ID.");
    cy.contains(basePath);
  });
});
