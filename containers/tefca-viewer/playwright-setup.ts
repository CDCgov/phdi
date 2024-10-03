/**
 *
 */
async function globalSetup() {
  const url = "http://localhost:3000/tefca-viewer";
  let response;

  while (!response || response.status !== 200) {
    try {
      response = await fetch(url);
      if (response.status !== 200) {
        console.log(
          `Failed to connect to ${url}, status: ${response.status}. Retrying...`,
        );
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
    } catch (error) {
      console.log(
        `Fetch failed for ${url}: ${(error as Error).message}. Retrying...`,
      );
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  console.log(`Connected to ${url} successfully`);
  await new Promise((resolve) => setTimeout(resolve, 2000));
}

export default globalSetup;
