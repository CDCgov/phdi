package gov.cdc.prime.phdi.Utilities

import org.apache.logging.log4j.kotlin.Logging
import java.time.format.DateTimeFormatter
import java.io.InputStream
import java.io.OutputStream
import java.nio.charset.StandardCharsets

public class HL7Reader() {
    fun readHL7MessagesFromFile(
        filepath: String
    ): String {
        // reads in a file of one or more HL7 messages and returns the content as a string
        return "This method is not currently implemented."
    }

    fun readHL7MessagesFromBlobStorage(
        client: String,
        bucketName: String,
        filepath: String 
    ): String {
        // given a cloud client, bucket name, and file path, read the content and return it as a string
        return "This method is not currently implemented."
    }

    fun readHL7MessagesFromByteArray(
        content: ByteArray
    ): String {
        val rawMessage: String = String(content, StandardCharsets.UTF_8)
        var reg = "[\r\n]".toRegex()
        var cleanedMessage: String = reg.replace(rawMessage, "\r")
        reg = "[\\u000b\\u001c]".toRegex()
        cleanedMessage = reg.replace(cleanedMessage, "")
        return cleanedMessage
    }
}
