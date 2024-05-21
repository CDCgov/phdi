describe("Home Page", () => {
  beforeEach(() => {
    cy.visit("http://localhost:3000/");
  });

  it("Should load the home page listing all eCR IDs", () => {
    cy.get('[data-testid="table"]').should("exist");
    cy.get('[data-testid="table"]').should("have.class", "table-homepage-list");
    cy.contains("eCR ID");
    cy.contains("Stored Date");
  });

  it("When clicking on an eCR ID link, it should redirect user to the correct URL of the individual eCR", () => {
    cy.get('[data-testid="table"] tbody tr:first-child')
      .find("a")
      .invoke("text") // Get the eCR ID
      .then((text) => {
        const linkEcrId = text;
        cy.get('[data-testid="table"] tbody tr:first-child')
          .find("a")
          .click()
          // Assert correct URL after clicking on the link
          .then(() => {
            cy.url().should("include", `/view-data?id=${linkEcrId}`);
          });
      });
  });

  it("When clicking on an eCR ID link, it should load the individual eCR Viewer", () => {
    cy.get('[data-testid="table"] tbody tr:first-child').find("a").click();
    cy.contains("eCR Summary");
    cy.get("nav").should("have.class", "sticky-nav");
    cy.get("div").should("have.class", "ecr-viewer-container");
  });
});
