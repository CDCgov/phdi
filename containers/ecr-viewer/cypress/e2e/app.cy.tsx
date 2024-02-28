describe("Navigation", () => {
  it("should redirect when url contains /ecr-viewer", () => {
    // Visit bad url
    cy.visit("http://localhost:3000/ecr-viewer/view-data");

    // The new url should NOT include "/ecr-viewer"
    cy.url().should("not.include", "/ecr-viewer");
  });
});
