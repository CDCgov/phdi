import { exec } from "child_process";

/**
 *
 */
async function jestSetup() {
  console.log("Starting the Docker DB...");
  await new Promise<void>((resolve, reject) => {
    exec(
      "docker compose -f docker-compose-dev.yaml up",
      (err, stdout, stderr) => {
        if (err) {
          console.error(`Error starting Docker DB: ${stderr}`);
          reject(err);
        } else {
          console.log("Docker DB started successfully");
          resolve();
        }
      },
    );
  });
  // exec("docker compose -f docker-compose-dev.yaml up", (err, stdout, stderr) => {
  //     if (err) {
  //         console.error(`Error starting Docker DB: ${stderr}`);
  //     } else {
  //         console.log("Docker DB started successfully");
  //     }
  // });
}

export default jestSetup;
