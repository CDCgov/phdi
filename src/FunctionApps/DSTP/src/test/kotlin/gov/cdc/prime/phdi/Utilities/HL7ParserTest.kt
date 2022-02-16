package gov.cdc.prime.phdi.Utilities

import kotlin.test.assertEquals
import kotlin.test.assertSame
import org.junit.jupiter.api.Test
import gov.cdc.prime.phdi.Utilities.HL7Parser

class HL7ParserTest {
    val singleMessage: String = javaClass.getResource("/singleMessage.hl7").readText()
    val multipleMessages: String = javaClass.getResource("/multipleMessages.hl7").readText()
    val mixedMessages: String = javaClass.getResource("/mixedMessages.hl7").readText()
    val batchFileSingleMessage: String = javaClass.getResource("/batchFileSingleMessage.hl7").readText()
    val batchFileMultipleMessages: String = javaClass.getResource("/batchFileMultipleMessages.hl7").readText()
    val batchFileNoMessage: String = javaClass.getResource("/batchFileNoMessage.hl7").readText()
    val loremIpsum: String = javaClass.getResource("/loremIpsum.txt").readText()
    val parser = HL7Parser()

    @Test
    fun testConvertBatchMessagesToList() {
        // test a single message
        val single = parser.convertBatchMessagesToList(singleMessage)
        assertEquals(1, single.size)

        // test multiple messages
        val multiple = parser.convertBatchMessagesToList(multipleMessages)
        assertEquals(10, multiple.size)

        // test invalid messages
        // convertBatchMessagesToList makes no effort to determine if 
        // the data it receives is valid HL7, so it will still chunk
        // messages even if one or more of the messages are invalid
        val invalid = parser.convertBatchMessagesToList(mixedMessages)
        assertEquals(3, invalid.size)

        // test batch file with a single message
        val batch_single = parser.convertBatchMessagesToList(batchFileSingleMessage)
        assertEquals(1, batch_single.size)

        // test batch file with multiple messages
        val batch_multiple = parser.convertBatchMessagesToList(batchFileMultipleMessages)
        assertEquals(5, batch_multiple.size)

        //test batch file with no messages
        val batch_empty = parser.convertBatchMessagesToList(batchFileNoMessage)
        assertEquals(0, batch_empty.size)

        // test pure text file
        // convertBatchMessagesToList makes no effort to determine if 
        // the data it receives is valid HL7, so it will still chunk
        // messages even if the text itself is not HL7. This should result
        // in a single element being returned, regardless of how large
        // the text is.
        val text = parser.convertBatchMessagesToList(loremIpsum)
        assertEquals(1, text.size)
    }

    @Test
    fun testParse() {
        val processedMessages = parser.parse(mixedMessages)
        val processedText = parser.parse(loremIpsum)

        // test that the method is returning the type we expect
        assertSame(HL7Parser.ProcessedMessages::class.java, processedMessages::class.java)
        assertSame(HL7Parser.ProcessedMessages::class.java, processedText::class.java)

        // test that it returns the correct number of valid messages
        assertEquals(2, processedMessages.valid_messages.size)
        assertEquals(0, processedText.valid_messages.size)

        // test that it returns the correct number of invalid messages
        assertEquals(1, processedMessages.invalid_messages.size)
        assertEquals(1, processedText.invalid_messages.size)
    }
}