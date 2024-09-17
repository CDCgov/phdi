import { exec } from "child_process";

/**
 *
 */
async function jestTeardown() {
  console.log("Stopping Docker DB...");
  await new Promise<void>((resolve, reject) => {
    exec("docker compose down", (err, stdout, stderr) => {
      if (err) {
        console.error(`Error starting Docker DB: ${stderr}`);
        reject(err);
      } else {
        console.log("Docker DB started successfully");
        resolve();
      }
    });
  });
}

export default jestTeardown;
