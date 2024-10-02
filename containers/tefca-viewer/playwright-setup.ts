// async function globalSetup() {
//   const url = "http://localhost:3000/tefca-viewer";

//   const response = await fetch(url);
//   while (response.status !== 200) {
//     console.log(`Failed to connect to ${url}`);
//     const response = await fetch(url);
//   }
// }

// export default globalSetup;

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
        await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait before retrying
      }
    } catch (error) {
      console.log(
        `Fetch failed for ${url}: ${(error as Error).message}. Retrying...`,
      );
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait before retrying
    }
  }

  console.log(`Connected to ${url} successfully`);
}

export default globalSetup;
