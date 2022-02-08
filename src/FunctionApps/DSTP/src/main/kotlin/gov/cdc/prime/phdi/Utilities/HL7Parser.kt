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
    data class ProcessedMessages(
        val valid_messages: List<Message>,
        val invalid_messages: List<String>
    )

    public fun parse(content: String): ProcessedMessages {
        val rawMessages = convertBatchMessagesToList(content)
        val valid_messages = mutableListOf<Message>()
        val invalid_messages = mutableListOf<String>()

        val context = DefaultHapiContext()
        // We will likely replace this with a more custom validation class in the future
        context.setValidationContext(ValidationContextFactory.defaultValidation() as ValidationContext);
        val parser = context.getPipeParser()

        rawMessages.forEach {
            try {
                val parsedMessage = parser.parse(it)
                valid_messages.add(parsedMessage)
            } catch (e: HL7Exception) {
                invalid_messages.add(it)
            }
        }
        return ProcessedMessages(valid_messages, invalid_messages)
    }

    /* This method was adopted from PRIME ReportStream, which can be found here: 
       https://github.com/CDCgov/prime-reportstream/blob/194396582be02fcc51295089f20b0c2b90e7c830/prime-router/src/main/kotlin/serializers/Hl7Serializer.kt#L121
    */
    public fun convertBatchMessagesToList(
        content: String,
        delimiter: String = "\n"
    ): MutableList<String> {
        var reg = "[\r\n]".toRegex()
        var cleanedMessage: String = reg.replace(content, delimiter)
        /* 
           These are unicode for vertical tab and file separator, respectively
           \u000b appears before every MSH segment, and \u001c appears at the
           end of the message in some of the data we've been receiving, so 
           we're explicitly removing them here.
        */
        reg = "[\\u000b\\u001c]".toRegex()
        cleanedMessage = reg.replace(cleanedMessage, "").trim()
        val messageLines = cleanedMessage.split(delimiter)
        val nextMessage = StringBuilder()
        val output = mutableListOf<String>()
        
        /* 
        FHS is a "File Header Segment", which is used to head a file (group of batches)
        FTS is a "File Trailer Segment", which defines the end of a file
        BHS is "Batch Header Segment", which defines the start of a batch
        BTS is "Batch Trailer Segment", which defines the end of a batch
        
        The structure of an HL7 Batch looks like this:
        [FHS] (file header segment) { [BHS] (batch header segment)
        { [MSH (zero or more HL7 messages)
        ....
        ....
        ....
        ] }
        [BTS] (batch trailer segment)
        }
        [FTS] (file trailer segment)

        We ignore lines that start with these since we don't want to include them in a message
        */
        messageLines.forEach {
            if (it.startsWith("FHS"))
                return@forEach
            if (it.startsWith("BHS"))
                return@forEach
            if (it.startsWith("BTS"))
                return@forEach
            if (it.startsWith("FTS"))
                return@forEach

            /*
                If we reach a line that starts with MSH and we have
                content in nextMessage, then by definition we have 
                a full message in nextMessage and need to append it
                to output. This will not trigger the first time we
                see a line with MSH since nextMessage will be empty
                at that time.
            */
            if (nextMessage.isNotBlank() && it.startsWith("MSH")) {
                output.add(nextMessage.toString())
                nextMessage.clear()
            }

            // Otherwise, continue to add the line of text to nextMessage
            if (it.isNotBlank()) {
                nextMessage.append("$it\r")
            }
        }
        /*
            Since our loop only adds messages to output when it finds
            a line that starts with MSH, the last message would never
            be added. So we explicitly add it here.
        */
        if (nextMessage.isNotBlank()) {
            output.add(nextMessage.toString())
        }
        return output
    }
}
