package gov.cdc.prime.phdi

import java.util.*
import com.microsoft.azure.functions.*
import com.microsoft.azure.functions.annotation.*

import gov.cdc.prime.phdi.utilities.*

class ConvertECRToFHIR {
    @FunctionName("convertEcrToFhir")
    fun run(
        @BlobTrigger(
            name = "file",
            dataType = "binary",
            path = "bronze/decrypted/ecr/{name}",
            connection="AzureWebJobsStorage"
        ) content: ByteArray,
        // @BindingName("name") filename: String,
        @BlobOutput(
            name="validTarget",
            dataType = "string",
            path="bronze/valid-messages/{name}.fhir",
            connection="AzureWebJobsStorage"
        ) validContent: OutputBinding<String>,
        @BlobOutput(
            name="invalidTarget",
            dataType = "string",
            path="bronze/invalid-messages/{name}.txt",
            connection="AzureWebJobsStorage"
        ) invalidContent: OutputBinding<String>,
        context: ExecutionContext
	) {
        // no logging until we can confirm that filename is never sensitive
        //context.logger.info("Name: ${filename} Size: ${content.size} bytes.")

        /* 
            Every time a new blob is moved to bronze/received-ecr-data, this function
            triggers, reads in the data, confirms that it's valid, converts the data
            to FHIR format, and then stores it in the bronze/valid-messages container. 
            If the data is invalid, the FHIR conversion is skipped and the data is 
            stored in bronze/invalid-messages in its original format.
        */

        val rawMessage: String = readHL7MessagesFromByteArray(content)
        /* TODO: 
            Figure out if an access token is even necessary. If it is
            then figure out a way to get the expiration time from the
            environment variables and only grab a new token if necessary.
        */    
        val accessToken: String? = getAccessToken()
        // Because of the issues enumerated in HelperFunctions.kt, we don't currently
        // check if it's a valid CCDA message. Instead we try to convert it, and if it
        // fails we send it to invalid.
        if (!accessToken.isNullOrEmpty()) {
            try {
                val json = convertMessageToFHIR(rawMessage, "ccda", "ccd", accessToken)
                validContent.setValue(json)
            } catch(e: Exception) {
                invalidContent.setValue(rawMessage)
            }
        }
        
    }
}
