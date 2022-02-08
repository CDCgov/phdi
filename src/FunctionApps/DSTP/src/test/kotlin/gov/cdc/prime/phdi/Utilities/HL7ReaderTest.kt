package gov.cdc.prime.phdi.Utilities

import kotlin.test.assertSame
import org.junit.jupiter.api.Test

class HL7ReaderTest {
    @Test
    fun testReadHL7MessagesFromByteArray() {
        val multipleMessages: ByteArray = javaClass.getResource("/multipleMessages.hl7").readBytes()
        val reader = HL7Reader()
        val content = reader.readHL7MessagesFromByteArray(multipleMessages)

        // assert that the reader is able to read the bytes and return a string
        assertSame(String::class.java, content::class.java)
    }
}