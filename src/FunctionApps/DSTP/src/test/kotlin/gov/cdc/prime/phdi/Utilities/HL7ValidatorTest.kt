package gov.cdc.prime.phdi.Utilities

import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class HL7ValidatorTest {
    val validator = HL7Validator()
    val singleValidMessage = javaClass.getResource("/singleMessage.hl7").readText()
    val singleInvalidMessage = javaClass.getResource("/singleInvalidMessage.hl7").readText()
    val loremIpsum = javaClass.getResource("/loremIpsum.txt").readText()

    // need to clean the text to ensure it's working the way it would in production
    fun cleanText(content: String): String {
        var reg = "[\r\n]".toRegex()
        var cleanedMessage: String = reg.replace(content, "\r")
        reg = "[\\u000b\\u001c]".toRegex()
        cleanedMessage = reg.replace(cleanedMessage, "")
        return cleanedMessage
    }
    
    @Test
    fun testIsValidHL7Message() {
        // test that it correctly validates a single valid message
        val cleanedSingleValidMessage = cleanText(singleValidMessage)
        assertEquals(true, validator.isValidHL7Message(cleanedSingleValidMessage))

        // test that it correctly invalidates a single invalid message
        val cleanedSingleInvalidMessage = cleanText(singleInvalidMessage)
        assertEquals(false, validator.isValidHL7Message(cleanedSingleInvalidMessage))

        // test that it correctly invalidates text that is not HL7
        val cleanedLoremIpsum = cleanText(loremIpsum)
        assertEquals(false, validator.isValidHL7Message(cleanedLoremIpsum))
    }
}