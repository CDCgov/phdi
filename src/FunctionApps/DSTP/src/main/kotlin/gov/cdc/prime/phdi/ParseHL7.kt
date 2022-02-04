package gov.cdc.prime.phdi

import java.util.*
import com.microsoft.azure.functions.*
import com.microsoft.azure.functions.annotation.*

import gov.cdc.prime.phdi.Utilities.HL7Reader
import gov.cdc.prime.phdi.Utilities.HL7Parser
import gov.cdc.prime.phdi.Utilities.HL7Validator

class ParseHL7 {
    @FunctionName("parsehl7")
    fun run(
        @BlobTrigger(
            name = "file",
            dataType = "binary",
            path = "bronze/decrypted/{name}",
            connection="AzureWebJobsStorage"
        ) content: ByteArray,
        @BindingName("name") filename: String,
        @BlobOutput(
            name="validTarget",
            dataType = "string",
            path="bronze/validation/{name}.valid",
            connection="AzureWebJobsStorage"
        ) validContent: OutputBinding<String>,
        @BlobOutput(
            name="invalidTarget",
            dataType = "string",
            path="bronze/validation/{name}.invalid",
            connection="AzureWebJobsStorage"
        ) invalidContent: OutputBinding<String>,
        context: ExecutionContext
	) {
        context.logger.info("Name: ${filename} Size: ${content.size} bytes.")

        // we don't actually do any processing of the HL7 messages here
        // We read in files from blob storage, extract individual messages from that
        // file, and then check that each message is valid. If it is, it goes to one
        // bucket, and if it's not it goes to another.

        val reader = HL7Reader()
        val parser = HL7Parser()
        val validator = HL7Validator()
        val cleanedMessages: String = reader.readHL7MessagesFromByteArray(content)
        val processedMessages: List<String> =  parser.convertBatchMessagesToList(cleanedMessages)
        val validMessages = StringBuilder()
        val invalidMessages = StringBuilder()

        processedMessages.forEach {
            if (validator.isValidHL7Message(it)) {
                validMessages.append("$it\r")
            } else {
                invalidMessages.append("$it\r")
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
