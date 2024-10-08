/**
 *
 */
async function globalSetup() {
  const url = "http://localhost:3000/tefca-viewer";
  const maxRetries = 300; // Maximum number of retries
  const delay = 1000; // Delay between retries in milliseconds

  for (let attempts = 0; attempts < maxRetries; attempts++) {
    try {
      const response = await fetch(url); // Fetch the URL
      if (response.status === 200) {
        console.log(`Connected to ${url} successfully.`);
        return; // Exit the function if the webpage loads successfully
      } else {
        console.log(
          `Failed to connect to ${url}, status: ${response.status}. Retrying...`,
        );
        // Wait before the next attempt
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    } catch (error) {
      console.log(
        `Fetch failed for ${url}: ${(error as Error).message}. Retrying...`,
      );
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
    // Wait before the next attempt
    await new Promise((resolve) => setTimeout(resolve, delay));
  }

  throw new Error(`Unable to connect to ${url} after ${maxRetries} attempts.`);
}

export default globalSetup;
