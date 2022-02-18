package gov.cdc.prime.phdi

import java.util.*
import com.microsoft.azure.functions.*
import com.microsoft.azure.functions.annotation.*

import gov.cdc.prime.phdi.utilities.*

class ConvertVXUToFHIR {
    @FunctionName("convertVxuToFhir")
    fun run(
        @BlobTrigger(
            name = "file",
            dataType = "binary",
            path = "bronze/decrypted/vxu/{name}",
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
            Every time a new blob is moved to bronze/received-vxu-data, this function
            triggers, reads in the data, confirms that it's valid, converts the data
            to FHIR format, and then stores it in the bronze/valid-messages container. 
            If the data is invalid, the FHIR conversion is skipped and the data is 
            stored in bronze/invalid-messages in its original format.
        */
        val rawMessages: String = readHL7MessagesFromByteArray(content)
        val processedMessages: List<String> = convertBatchMessagesToList(rawMessages)
        val validMessages = StringBuilder()
        val invalidMessages = StringBuilder()

        processedMessages.forEach {
            if (isValidHL7Message(it)) {
                val json = convertMessageToFHIR(it, "hl7v2", "VXU_V04")
                validMessages.append("$json\n")
            } else {
                invalidMessages.append("$it\n")
            }
        }

        if (validMessages.isNotBlank()) {
            validContent.setValue(validMessages.toString().trim())
        }

        if (invalidMessages.isNotBlank()) {
            invalidContent.setValue(invalidMessages.toString().trim())
        }
    }
}
