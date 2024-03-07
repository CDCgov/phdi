const testBody = {
  fhirBundle: {
    resourceType: "Bundle",
    type: "batch",
    entry: [
      {
        fullUrl: "urn:uuid:12345",
        resource: {
          resourceType: "Composition",
          id: "12345",
        },
      },
    ],
  },
};

describe("POST /api/save-fhir-data", () => {
  it("should successfully save FHIR Bundle to the database", () => {
    cy.request({
      method: "POST",
      url: "http://localhost:3000/api/save-fhir-data",
      body: testBody,
      headers: {
        "Content-Type": "application/json",
      },
    });

    cy.intercept("postgres://postgres:pw@db:5432/ecr_viewer_db", (req) => {
      console.log("REQUEST: ", req);
      expect(req).toEqual("haha");
    }).as("intercept");
  });
});

// describe("POST /api/save-fhir-data", () => {
//   it("should successfully save FHIR Bundle to the database", () => {
//     cy.intercept("POST", "/api/save-fhir-data", (req) => {
//       // Mock response
//       req.reply({
//         statusCode: 200,
//         body: {
//           message: "Success. Saved FHIR Bundle to database: test_reply",
//         },
//         headers: {
//           "content-type": "text/html",
//         },
//       });
//     }).as("successPostRequest");

//     cy.visit({
//       method: "POST",
//       url: "http://localhost:3000/api/save-fhir-data",
//       body: testBody,
//       headers: {
//         "Content-Type": "application/json",
//       },
//     });

//     cy.wait("@successPostRequest").then((interception) => {
//       expect(interception.response.statusCode).to.eq(200);
//       cy.contains("Success. Saved FHIR Bundle to database: test_reply").should(
//         "exist",
//       );
//     });
//   });

//   it("should fail to save FHIR Bundle to the database", () => {
//     cy.intercept("POST", "/api/save-fhir-data", (req) => {
//       // Mock response
//       req.reply({
//         statusCode: 400,
//         body: {
//           message: "Failed to insert data to database. test_reply",
//         },
//         headers: {
//           "content-type": "text/html",
//         },
//       });
//     }).as("failPostRequest");

//     cy.visit({
//       method: "POST",
//       url: "http://localhost:3000/api/save-fhir-data",
//       body: testBody,
//       headers: {
//         "Content-Type": "application/json",
//       },
//       failOnStatusCode: false,
//     });

//     cy.wait("@failPostRequest").then((interception) => {
//       expect(interception.response.statusCode).to.eq(400);
//       cy.contains("Failed to insert data to database. test_reply").should(
//         "exist",
//       );
//     });
//   });
// });
