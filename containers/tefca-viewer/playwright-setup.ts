/**
 *
 */
async function globalSetup() {
  const url = "http://localhost:3000/tefca-viewer";

  const response = await fetch(url);
  while (response.status !== 200) {
    console.log(`Failed to connect to ${url}`);
    const response = await fetch(url);
  }
}

export default globalSetup;