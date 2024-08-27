var zipFile = output.append(input[0]);

// DIBBs orchestration service URL
var orchestrationURL = "http://localhost:8080/process-zip";
// DIBBs orchestration service configuration
var config = "sample-orchestration-s3-config.json";
// Number of times to retry in case of failure
var retries = 1;

function run() {
  var xhr = new XMLHttpRequest();
  var formData = new FormData();

  formData.append("message_type", "ecr");
  formData.append("config_file_name", config);
  formData.append("upload_file", zipFile);
  formData.append("data_type", "zip");

  xhr.open("POST", orchestrationURL, true);

  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if (xhr.status !== 200 && retries !== 0) {
        console.log("Request failed, retrying...", xhr.response);
        retries--;
        run();
      } else {
        console.log("Request failed after retrying. Status: " + xhr.status);
      }
    }
  };

  xhr.send(formData);
}

run();
