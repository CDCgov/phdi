package gov.cdc.prime.phdi.Utilities

import ca.uhn.hl7v2.DefaultHapiContext
import ca.uhn.hl7v2.HL7Exception
import ca.uhn.hl7v2.HapiContext
import ca.uhn.hl7v2.model.Message
import ca.uhn.hl7v2.parser.EncodingNotSupportedException
import ca.uhn.hl7v2.parser.Parser
import ca.uhn.hl7v2.validation.ValidationContext;
import ca.uhn.hl7v2.validation.impl.ValidationContextFactory;

public class HL7Parser() {
    public fun parse(content: String): Map<String, MutableList<Any>> {
        val rawMessages = convertBatchMessagesToList(content)
        val processedMessages = mutableMapOf<String, MutableList<Any>>(
            "invalid_messages" to mutableListOf(),
            "valid_messages" to mutableListOf()
        )

        val context = DefaultHapiContext()
        // We will likely replace this with a more custom validation class in the future
        context.setValidationContext(ValidationContextFactory.defaultValidation() as ValidationContext);
        val parser = context.getPipeParser()

        rawMessages.forEach {
            try {
                val parsedMessage = parser.parse(it)
                processedMessages["valid_messages"]!!.add(parsedMessage)
            } catch (e: HL7Exception) {
                processedMessages["invalid_messages"]!!.add(it)
            }
        }
        return processedMessages
    }

    public fun convertBatchMessagesToList(
        content: String,
        delimiter: String = "\n"
    ): MutableList<String> {
        var reg = "[\r\n]".toRegex()
        var cleanedMessage: String = reg.replace(content, delimiter)
        reg = "[\\u000b\\u001c]".toRegex()
        cleanedMessage = reg.replace(cleanedMessage, "").trim()
        val messageLines = cleanedMessage.split(delimiter)
        val nextMessage = StringBuilder()
        val output = mutableListOf<String>()
        
        messageLines.forEach {
            if (it.startsWith("FHS"))
                return@forEach
            if (it.startsWith("BHS"))
                return@forEach
            if (it.startsWith("BTS"))
                return@forEach
            if (it.startsWith("FTS"))
                return@forEach

            if (nextMessage.isNotBlank() && it.startsWith("MSH")) {
                output.add(nextMessage.toString())
                nextMessage.clear()
            }

            if (it.isNotBlank()) {
                nextMessage.append("$it\r")
            }
        }
        // catch the last message
        if (nextMessage.isNotBlank()) {
            output.add(nextMessage.toString())
        }
        return output
    }
}
