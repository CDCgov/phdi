const {expect} = require('chai');
const axios = require('axios');
const {DockerComposeEnvironment} = require('testcontainers');

const ECR_VIEWER_URL = 'http://0.0.0.0:3000';
const ECR_VIEWER = ECR_VIEWER_URL + '/view-data';

// Define a function to set up the containers.
async function setup() {
    console.log('Setting up tests...');

    // Define the Docker Compose configuration.
    const composeFile = 'docker-compose.yml';

    // Create a Docker Compose container.
    const ecrView = await new DockerComposeEnvironment('./', composeFile)
        .up()

    console.log('eCR Viewer service ready to test!');

    // Define a function to tear down the containers.
    async function teardown() {
        console.log('\nContainer output:');
        console.log(await ecrView.logs());

        console.log('Tests finished! Tearing down.');
        await ecrView.stop();
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
        const response = await axios.get(ECR_VIEWER);
        expect(response.status).to.equal(200);
    });

    it('loads from the postgress db', async () => {
        const response = await axios.get(
          `${HTML_INSIGHTS_URL}/view-data?id=1dd10047-2207-4eac-a993-0f706c88be5d`
        );
        expect(response.status).to.equal(200)
        expect(response.data).to.include("")
    })

    // it('performs a .json post', async () => {
    //     const formData = new FormData();
    //     const jsonData = fs.createReadStream(path.resolve(__dirname, "./single_patient_bundle.json"));
    //     formData.append('file', jsonData);

    //     const response = await axios.post(HTML_INSIGHTS, formData, {
    //         headers: {
    //             ...formData.getHeaders(),
    //         },
    //     });
    //     expect(response.data.resourceType).equals("Bundle");
    //     expect(response.status).equals(200);
    // });

});
