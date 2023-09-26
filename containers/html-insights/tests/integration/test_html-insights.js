const { expect } = require('chai');
const axios = require('axios');
const { DockerComposeEnvironment, Wait } = require('testcontainers');

const HTML_INSIGHTS_URL = 'http://0.0.0.0:8080';
const HTML_INSIGHTS = HTML_INSIGHTS_URL + '/html-insights';

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

describe('Integration Tests', () => {
  before(async () => {
    await setup();
  });

  it('should perform a health check', async () => {
    const response = await axios.get(HTML_INSIGHTS_URL);
    expect(response.status).to.equal(200);
  });

});
