package gov.cdc.prime.phdi;

import java.time.Duration;

import com.azure.core.util.polling.PollResponse;
import com.azure.core.util.polling.SyncPoller;
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.storage.blob.BlobClient;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.azure.storage.blob.models.BlobCopyInfo;
import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.annotation.*;

/*
Example local.settings.json (JAVA_HOME path may vary for local development):
{
  "IsEncrypted": false,
  "Values": {
    "JAVA_HOME": "/usr",
    "FUNCTIONS_WORKER_RUNTIME": "java",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "IdConn__serviceUri": "https://pidevdatasa.blob.core.windows.net",
    "AzureWebJobsStorage": "@Microsoft.KeyVault(SecretUri=https://pidev-app-kv.vault.azure.net/secrets/functionappsa)"
  }
}

Note: DefaultAzureCredential logic can be replaced with the following IF the function app 
has the Storage Blob Data Contributor role:
@BlobOutput(name = "$return", path = "silver/sink/Copy-{name}", connection = "IdConn")

Commands:
Run the following command to build:
mvn clean package -DfunctionAppName=pidev-java-functionapp -Denv=dev

Run the following command to run locally:
(May require running twice if first occurance produces errors due to updating queue)
mvn azure-functions:run -DfunctionAppName=pidev-java-functionapp -Denv=dev

Run the following command to deploy:
mvn azure-functions:deploy -DfunctionAppName=pidev-java-functionapp -Denv=dev
*/
public class BlobTriggerJava1 {

    final String endpoint = System.getenv("IdConn__serviceUri");

    // Keep source and sink on separate paths to avoid infinite loop
    @FunctionName("BlobTriggerJava1")
    public void copy(
            @BlobTrigger(name = "content", path = "silver/source/{name}", connection = "IdConn", dataType = "binary") byte[] content,
            @BindingName("name") String filename,
            @BindingName("BlobTrigger") String path,
            final ExecutionContext context) {

        String[] pathSplit = path.split("/");
        String container = pathSplit[0];
        String sourceDirectory = pathSplit[1];

        DefaultAzureCredential defaultCredential = new DefaultAzureCredentialBuilder().build();
        final BlobContainerClientBuilder clientBuilder = new BlobContainerClientBuilder()
                .endpoint(endpoint)
                .containerName(container)
                .credential(defaultCredential);

        BlobContainerClient client = clientBuilder.buildClient();
        BlobClient sourceBlobClient = client.getBlobClient(sourceDirectory + "/" + filename);
        BlobClient targetBlobClient = client.getBlobClient("sink/copy-" + filename);

        final SyncPoller<BlobCopyInfo, Void> poller = targetBlobClient.beginCopy(sourceBlobClient.getBlobUrl(),
                Duration.ofSeconds(2));
        PollResponse<BlobCopyInfo> pollResponse = poller.poll();

        System.out.printf("Copy identifier: %s%n", pollResponse.getValue().getCopyId());
    }
}
