function jsonToHtml(json, indent = 0) {
  if (typeof json !== "object" || json === null) {
    // Handle non-object types and null
    return `<span class="value">${JSON.stringify(json)}</span>`;
  }

  const isArray = Array.isArray(json);
  let html = isArray ? "[<br>" : "{<br>";
  const indentStr = "&nbsp;".repeat(indent * 4);
  const childIndentStr = "&nbsp;".repeat((indent + 1) * 4);

  for (const [key, value] of Object.entries(json)) {
    const formattedKey = isArray ? "" : `<span class="key">"${key}"</span>: `;
    let formattedValue;

    // Apply unique styling to the value of "resourceType" key
    if (!isArray && key === "resourceType") {
      formattedValue = `<span class="resourceType-value">"${value}"</span>`;
    } else {
      // Recursively apply formatting for nested objects/arrays
      formattedValue = jsonToHtml(value, indent + 1);
    }

    html += `${childIndentStr}${formattedKey}${formattedValue}${
      isArray ? "," : ""
    }<br>`;
  }

  html = html.replace(/,<br>$/, "<br>"); // Remove the last comma for arrays
  html += `${indentStr}${isArray ? "]" : "}"}`;
  return html;
}

document
  .getElementById("dataForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    // Hide the API response and show the loader
    document.getElementById("loader").style.display = "block";
    document.getElementById("apiResponse").style.display = "none";

    var useCase = document.getElementById("useCase").value;
    var fhirServer = document.getElementById("fhirServer").value;
    var firstName = document.getElementById("first_name").value;
    var lastName = document.getElementById("last_name").value;
    var dob = document.getElementById("dob").value;

    var data = {
      fhir_server: fhirServer,
      first_name: firstName,
      last_name: lastName,
      dob: dob,
      use_case: useCase,
    };

    fetch("use-case-query/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide loader and show API response
        console.log("Hide loader");
        document.getElementById("loader").style.display = "none";
        document.getElementById("apiResponse").innerHTML =
          "<pre>" + jsonToHtml(data) + "</pre>";
        document.getElementById("apiResponse").style.display = "block";
      })
      .catch((error) => {
        // Hide loader and show error
        document.getElementById("loader").style.display = "none";
        document.getElementById("apiResponse").innerHTML = "Error: " + error;
        document.getElementById("apiResponse").style.display = "block";
      });
  });
