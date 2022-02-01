package gov.cdc.prime.phdi

import java.util.*
import com.microsoft.azure.functions.*
import com.microsoft.azure.functions.annotation.*
import java.nio.charset.StandardCharsets

class HL7Ingest {
    @FunctionName("injesthl7")
    fun run(
            @HttpTrigger(
				name = "req",
				methods = [HttpMethod.GET, HttpMethod.POST],
				authLevel = AuthorizationLevel.FUNCTION
			) request: HttpRequestMessage<Optional<String>>,
			@BlobOutput(
				name="target",
				path="received-files/{rand-guid}",
				connection="AzureWebJobsStorage"
			) outputContent: OutputBinding<String>,
            context: ExecutionContext
	): HttpResponseMessage {

        context.logger.info("HTTP trigger processed a ${request.httpMethod.name} request.")

		val messageContents = request.body

        messageContents?.let {
			outputContent.setValue(messageContents.get())
            return request
				.createResponseBuilder(HttpStatus.OK)
				.body("File(s) successfully uploaded.")
				.build()
        }

        return request
			.createResponseBuilder(HttpStatus.BAD_REQUEST)
			.body("You must pass your data in the API request. Example: curl --data-binary @\"/path/to/your_file.hl7\"")
			.build()
    }

}
