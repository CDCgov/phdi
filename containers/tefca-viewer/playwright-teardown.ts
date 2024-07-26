import { exec } from "child_process";

// Function to stop Docker
/**
 *
 */
async function globalTeardown() {
  console.log("Stopping Docker...");
  await new Promise<void>((resolve, reject) => {
    exec("docker compose down", (err, stdout, stderr) => {
      if (err) {
        console.error(`Error stopping Docker: ${stderr}`);
        reject(err);
      } else {
        console.log("Docker stopped successfully");
        resolve();
      }
    });
  });
}

export default globalTeardown;
