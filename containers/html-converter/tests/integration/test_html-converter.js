const { expect } = require('chai');
const axios = require('axios');
const FormData = require('form-data');
const path = require("path");
const fs = require('fs');
const { DockerComposeEnvironment } = require('testcontainers');

const HTML_INSIGHTS_URL = 'http://0.0.0.0:8080';
const HTML_INSIGHTS = HTML_INSIGHTS_URL + '/generate-html';

// Define a function to set up the containers.
async function setup() {
    console.log('Setting up tests...');
  
    // Define the Docker Compose configuration.
    const composeFile = 'docker-compose.yaml';
  
    // Create a Docker Compose container.
    const htmlInsights = await new DockerComposeEnvironment('./tests/integration',composeFile)
      .up()
  
    console.log('HTML Insights service ready to test!');
  
    // Define a function to tear down the containers.
    async function teardown() {
        console.log('\nContainer output:');
        console.log(await htmlInsights.logs());
    
        console.log('Tests finished! Tearing down.');
        await htmlInsights.stop();
        }
    
        // Add the teardown function as a finalizer.
        process.on('exit', async () => {
        await teardown();
    });
  }

module.exports = setup;

describe('Integration tests', () => {
  before(async () => {
    await setup();
  });

  it('should perform a health check', async () => {
    const response = await axios.get(HTML_INSIGHTS_URL);
    expect(response.status).to.equal(200);
  });

  it('performs a .csv post', async () => {
    const formData = new FormData();
    const csvData = fs.createReadStream(path.resolve(__dirname, "./test.csv"));
    formData.append('file', csvData);
    
    // Perform a POST request with the CSV data
    const response = await axios.post(HTML_INSIGHTS, formData, {
      headers: {
        ...formData.getHeaders(),
      },
    });
    expect(response.data).includes("<td>HUNSINGER</td>");
    // Assuming the server responds with a 200 status code for a successful POST
    expect(response.status).to.equal(200);
  });

});
