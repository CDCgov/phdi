import asyncio
import os
import pathlib

import aiohttp
from lxml import etree as ET


async def call_openai_gpt_async(
    session, messages, model="gpt-3.5-turbo", max_tokens=400
):
    """
    Makes an asynchronous API call to OpenAI's GPT model using aiohttp.

    :param session: The aiohttp session object to use for requests.
    :param prompt: The input prompt to generate text from.
    :param model: The model to use. Default is 'gpt-3.5-turbo	'.
    :param max_tokens: The maximum number of tokens to generate. Default is 100.
    :return: The generated text response.
    """
    api_key = os.environ["OPENAI_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    async with session.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    ) as response:
        if response.status == 200:
            return await response.json()
        else:
            return f"Error: {response.status}, {await response.text()}"


async def main():
    """
    Converts XML CDA Observations to FHIR Observation resources using aio.
    """
    patient_id = "76d0716f-6af0-49e6-b99e-73ccd831c8d8"

    phdc_path = pathlib.Path(__file__).parent / "HEPA_GDIT_Example.xml"
    phdc = ET.parse(phdc_path)
    observations = phdc.findall(".//{urn:hl7-org:v3}observation")[0:10]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for observation in observations[0:100]:
            initial_message = {
                "role": "system",
                "content": f"""
                    You are helping transform healthcare data between
                    different formats. Convert the following XML CDA Observation
                    element to a FHIR Observation resource. Do not change any of
                    the values for code system or code system name from how you
                    find them in the XML. For any date or date time include just
                    the date in YYYY-MM-DD format. If the value has xsi:type="TS"
                    include the data in Observation.valueDateTime not
                    Observation.effectiveDateTime. Include category.coding.code.
                    The subject should reference Patient/{patient_id}. Your response
                    should be a JSON formatted Observation resource.
                    """,
            }
            observation_message = {
                "role": "user",
                "content": ET.tostring(observation).decode(),
            }
            tasks.append(
                call_openai_gpt_async(session, [initial_message, observation_message])
            )

        responses = await asyncio.gather(*tasks)
        for response in responses:
            print(response["choices"][0]["message"]["content"])


# Run the main function in the asyncio event loop
asyncio.run(main())
