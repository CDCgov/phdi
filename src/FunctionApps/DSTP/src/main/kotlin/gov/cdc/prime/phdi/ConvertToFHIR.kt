package gov.cdc.prime.phdi

import java.util.*
import com.microsoft.azure.functions.*
import com.microsoft.azure.functions.annotation.*

import gov.cdc.prime.phdi.utilities.*

class ConvertToFHIR {
    /* 
        Every time a new blob is moved to bronze/raw/(elr|ecr|vxu), this function
        triggers, reads in the data, confirms that it's valid, converts the data
        to FHIR format, and then stores it in the bronze/valid-messages container. 
        If the data is invalid, the FHIR conversion is skipped and the data is 
        stored in bronze/invalid-messages in its original format.
    */
    @FunctionName("convertToFhir")
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
        val rawInput: String = readHL7MessagesFromByteArray(content)
        val messageCategory: String = filename.split("/")[0].lowercase()
        val messageFormat: String? = when (messageCategory) {
            "elr" -> "hl7v2"
            "vxu" -> "hl7v2"
            "ecr" -> "ccda"
            else -> null
        }
        val messageType: String? = when (messageCategory) {
            "elr" -> "ORU_R01"
            "vxu" -> "VXU_V04"
            "ecr" -> "ccd"
            else -> null
        }

        if (messageFormat.isNullOrEmpty() || messageType.isNullOrEmpty()) {
            context.logger.warning(
                "An unknown message category was encountered and not processed."
            )
            return
        }

        val accessToken: String? = getAccessToken()
        if (accessToken.isNullOrEmpty()) {
            context.logger.warning(
                "Failed to get a valid access token."
            )
            return
        }

        /* 
            ECR data comes in in the form of XML, and as far as we know
            right now, only one message is contained in a given file.
            We'll need to adjust the code if we find out differently later.
        */
        val messages: List<String>
        val validMessages = StringBuilder()
        val invalidMessages = StringBuilder()
        if (messageType.equals("ecr")) {
            messages = listOf(rawInput)
        } else {
            messages = convertBatchMessagesToList(rawInput)
        }

        messages.forEach {
            // we currently don't have a good way of testing if ECR messages
            // are valid messages. Instead, we rely on the FHIR Converter to
            // handle it.
            if (messageCategory.equals("ecr") || isValidHL7Message(it)) {
                try {
                    val json = convertMessageToFHIR(
                        it,
                        messageFormat,
                        messageType,
                        accessToken
                    )
                    if (isValidFHIRMessage(json)) {
                        val json_single_line = json!!.replace("[\n\r]".toRegex(), "")
                        validMessages.append("$json_single_line\n")
                    } else {
                        context.logger.info(
                            "The FHIR Server failed to convert a $messageCategory message."
                        )
                        val it_single_line = it.replace("[\n\r]".toRegex(), "")
                        invalidMessages.append("$it_single_line\n")
                    }
                } catch (e: Exception) {
                    val msg: String = """
                    A server error occured during the FHIR conversion process.
                    Stack Trace:
                    ${e.stackTraceToString()}
                    """
                    context.logger.warning(msg)
                    // don't process any further
                    //TODO: implement logic to handle retries
                }
            } else {
                val it_single_line = it.replace("[\n\r]".toRegex(), "")
                invalidMessages.append("$it_single_line\n")
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
