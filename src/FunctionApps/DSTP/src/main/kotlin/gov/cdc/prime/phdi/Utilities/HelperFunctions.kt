package gov.cdc.prime.phdi.utilities

// Working with HL7/CCDA
import ca.uhn.hl7v2.Version
import ca.uhn.hl7v2.DefaultHapiContext
import ca.uhn.hl7v2.HL7Exception
import ca.uhn.hl7v2.HapiContext
import ca.uhn.hl7v2.model.Message
import ca.uhn.hl7v2.parser.EncodingNotSupportedException
import ca.uhn.hl7v2.parser.Parser
import ca.uhn.hl7v2.parser.XMLParser
import ca.uhn.hl7v2.parser.DefaultXMLParser
import ca.uhn.hl7v2.validation.ValidationContext
import ca.uhn.hl7v2.validation.impl.ValidationContextFactory
import ca.uhn.hl7v2.validation.builder.support.DefaultValidationBuilder

// Making API calls
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

// Working with different string representations
import org.json.JSONObject
import java.nio.charset.StandardCharsets

/* 
   ******************* 
    READING FUNCTIONS
   *******************
*/

/* 
    this method is used when you want to read in a file that is stored locally
    on your machine. As noted, it's specifically for HL7 v2 data.
*/
@Throws(NotImplementedError::class)
fun readHL7MessagesFromFile(
    filepath: String
): String {
    throw NotImplementedError("This method is not currently implemented.")
}

/* 
    this method is used when you want to directly connect to a blob storage container
    and read the data from there. As noted, it's specifically for HL7 v2 data.
*/
@Throws(NotImplementedError::class)
fun readHL7MessagesFromBlobStorage(
    client: String,
    bucketName: String,
    filepath: String 
): String {
    throw NotImplementedError("This method is not currently implemented.")
}

/*
    this method is used inside of an Azure Function (or AWS/GCP equivalent) and is
    used to read in the data based on a blob trigger.
*/
fun readHL7MessagesFromByteArray(
    content: ByteArray
): String {
    val rawMessage: String = String(content, StandardCharsets.UTF_8)
    var reg = "[\r\n]+".toRegex()
    var cleanedMessage = reg.replace(rawMessage, "\n")
    reg = "[\\u000b\\u001c]".toRegex()
    cleanedMessage = reg.replace(cleanedMessage, "")
    
    return cleanedMessage
}

/* 
   ******************* 
    PARSING FUNCTIONS
   *******************
*/
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

/* 
   ***********************
    FHIR SERVER FUNCTIONS
   ***********************
*/
// Connect to the FHIR server and get a bearer token
public fun getAccessToken(): String? {
    val tenantId: String = System.getenv("tenant_id")
    val url: String = "https://login.microsoftonline.com/${tenantId}/oauth2/token"

    val requestBody = StringBuilder("grant_type=client_credentials")
    val parameters: MutableMap<String, String> = HashMap()
    //parameters.put("grant_type", "client_credentials")
    parameters.put("client_id", System.getenv("client_id"))
    parameters.put("client_secret", System.getenv("client_secret"))
    parameters.put("resource", System.getenv("fhir_url"))
    parameters.forEach { (key, value) -> requestBody.append("&${key}=${value}") }


    val client: HttpClient = HttpClient.newHttpClient()
    val request: HttpRequest = HttpRequest.newBuilder()
        .uri(URI.create(url))
        .headers("Content-Type", "application/x-www-form-urlencoded")
        .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
        .build()

    val response: HttpResponse<String> = client.send(
        request,
        HttpResponse.BodyHandlers.ofString()
    )
    val json: JSONObject = JSONObject(response.body())
    val accessToken:String? = json.get("access_token")?.toString()
    return accessToken
}

public fun convertMessageToFHIR(
    message: String,
    messageFormat: String,
    messageType: String,
    accessToken: String
): String {
    val inputDataType = when (messageFormat.lowercase()) {
        "hl7v2" -> "Hl7v2"
        "ccda" -> "Ccda"
        "json" -> "Json"
        else -> "UNKNOWN"
    }

    //TODO: Implement handling of inputDataType when it's not valid

    // valid values come from https://docs.microsoft.com/en-us/azure/healthcare-apis/fhir/convert-data
    val rootTemplate: String = when (messageType.lowercase()) {
        "adt_a01" -> "ADT_A01"
        "oml_o21" -> "OML_O21"
        "oru_r01" -> "ORU_R01"
        "vxu_v04" -> "VXU_V04"
        "ccd" -> "CCD"
        "ccda" -> "CCD"
        "consultationnote" -> "ConsultationNote"
        "dischargesummary" -> "DischargeSummary"
        "historyandphysical" -> "HistoryandPhysical"
        "operativenote" -> "OperativeNote"
        "procedurenote" -> "ProcedureNote"
        "progressnote" -> "ProgressNote"
        "referralnote" -> "ReferralNote"
        "transfersummary" -> "TransferSummary"
        "examplepatient" -> "ExamplePatient"
        "stu3chargeitem" -> "Stu3ChargeItem"
        else -> "UNKNOWN"
    }

    val templateCollection: String = when (inputDataType) {
        "Hl7v2" -> "microsofthealth/fhirconverter:default"
        "Ccda" -> "microsofthealth/ccdatemplates:default"
        "Json" -> "microsofthealth/jsontemplates:default"
        else -> "microsofthealth/hl7v2templates:default"
    }

    // connect to the FHIR #convert-data endpoint using the access token
    val fhirUrl: String = "${System.getenv("fhir_url")}/\$convert-data"
    val fhirRequestBody: JSONObject = JSONObject()
    fhirRequestBody.put("resourceType", "Parameters")
    fhirRequestBody.put("parameter", listOf(
        mapOf("name" to "inputData", "valueString" to "${message}"),
        mapOf("name" to "inputDataType", "valueString" to "${inputDataType}"),
        mapOf("name" to "templateCollectionReference", "valueString" to "${templateCollection}"),
        mapOf("name" to "rootTemplate", "valueString" to "${rootTemplate}")
    ))
    val json: String = fhirRequestBody.toString()
    
    val client: HttpClient = HttpClient.newHttpClient()
    val convertDataRequest: HttpRequest = HttpRequest.newBuilder()
        .uri(URI.create(fhirUrl))
        .headers("Content-Type", "application/json", "Authorization", "Bearer ${accessToken}")
        .POST(HttpRequest.BodyPublishers.ofString(json))
        .build()
    val rawConvertDataResponse: HttpResponse<String> = client.send(
        convertDataRequest,
        HttpResponse.BodyHandlers.ofString()
    )
    
    return rawConvertDataResponse.body()
}

/* 
   ********************** 
    VALIDATING FUNCTIONS
   **********************
*/

private fun isValidMessage(message: String, format: String): Boolean {
    val context = DefaultHapiContext()
    // We will likely replace this with a more custom validation class in the future
    context.setValidationContext(ValidationContextFactory.defaultValidation() as ValidationContext)

    val parser = if (format === "xml") context.getXMLParser() else context.getPipeParser()
    /*
        For now, we don't track or log why a message fails
        to get parsed by HL7. We simply return true if HAPI
        is able to successfully parse the message, and false
        if it can't, based on the validation context that's
        set above.
    */
    try {
        parser.parse(message)
        return true
    } catch (e: HL7Exception) {
        e.printStackTrace()
        return false
    }
}

public fun isValidHL7Message(message: String): Boolean {
    val context = DefaultHapiContext()
    // We will likely replace this with a more custom validation class in the future
    context.setValidationContext(ValidationContextFactory.defaultValidation() as ValidationContext)

    val parser = context.getPipeParser()
    try {
        parser.parse(message)
        return true
    } catch (e: HL7Exception) {
        e.printStackTrace()
        return false
    }
}

@Throws(NotImplementedError::class)
public fun isValidXMLMessage(message: String): Boolean {
    /*
        There's some work that needs to be done here because
        the methods in XMLParser are labeled as protected,
        which would be fine in Java, but in Kotlin this prevents
        access to the methods. As a result, all of the steps 
        necessary to try to parse an XML string are inaccessible.
        The solution would look something like the follow:
        val doc = xmlParser.parseStringToDocument(message)
        xmlParser.parseDocument(doc)
    */
    throw NotImplementedError("This method is not currently implemented.")
}
