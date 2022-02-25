package gov.cdc.prime.phdi

import java.util.*
import com.microsoft.azure.functions.*
import com.microsoft.azure.functions.annotation.*

import gov.cdc.prime.phdi.utilities.*

class ConvertELRToFHIR {
    @FunctionName("convertElrToFhir")
    fun run(
        @BlobTrigger(
            name = "file",
            dataType = "binary",
            path = "bronze/decrypted/elr/{name}",
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
            Every time a new blob is moved to bronze/decrypted/elr, this function
            triggers, reads in the data, confirms that it's valid, converts the data
            to FHIR format, and then stores it in the bronze/valid-messages container. 
            If the data is invalid, the FHIR conversion is skipped and the data is 
            stored in bronze/invalid-messages in its original format.
        */
        val rawMessages: String = readHL7MessagesFromByteArray(content)
        val processedMessages: List<String> =  convertBatchMessagesToList(rawMessages)
        val validMessages = StringBuilder()
        val invalidMessages = StringBuilder()
        /* TODO: 
            Figure out if an access token is even necessary. If it is
            then figure out a way to get the expiration time from the
            environment variables and only grab a new token if necessary.
        */    
        val accessToken: String? = getAccessToken()

        if (!accessToken.isNullOrEmpty()) {
            processedMessages.forEach {
                if (isValidHL7Message(it)) {
                    try{
                        val json = convertMessageToFHIR(it, "hl7v2", "ORU_R01", accessToken)
                        if (isValidFHIRMessage(json)) {
                            validMessages.append("$json\n")
                        } else {
                            context.logger.info("An invalid FHIR message was returned during the conversion process.")
                            invalidMessages.append("$it\n")
                        }
                    } catch (e: Exception) {
                        context.logger.info("Failed to convert a message to FHIR. Error: ${e.stackTraceToString()}")
                        invalidMessages.append("$it\n")
                    }
                } else {
                    invalidMessages.append("$it\n")
                }
            }
        } else {
            context.logger.info("Failed to retrieve a valid access token.")
        }
        

        if (validMessages.isNotBlank()) {
            validContent.setValue(validMessages.toString().trim())
        }

        if (invalidMessages.isNotBlank()) {
            invalidContent.setValue(invalidMessages.toString().trim())
        }
    }
}
