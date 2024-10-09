import fetch, { RequestInit, HeaderInit, Response } from "node-fetch";
import { v4 as uuidv4 } from "uuid";
import { FHIR_SERVERS } from "./constants";
/**
 * Defines the model for a FHIR server configuration
 */
type FHIR_SERVER_CONFIG = {
  hostname: string;
  init: RequestInit;
};

/**
 * The configurations for the FHIR servers currently supported.
 */
export const fhirServers: Record<FHIR_SERVERS, FHIR_SERVER_CONFIG> = {
  "HELIOS Meld: Direct": {
    hostname: "https://gw.interop.community/HeliosConnectathonSa/open",
    init: {} as RequestInit,
  },
  "HELIOS Meld: eHealthExchange": configureEHX("MeldOpen"),
  "JMC Meld: Direct": {
    hostname: "https://gw.interop.community/JMCHeliosSTISandbox/open",
    init: {} as RequestInit,
  },
  "JMC Meld: eHealthExchange": configureEHX("JMCHelios"),
  "Public HAPI: Direct": {
    hostname: "https://hapi.fhir.org/baseR4",
    init: {} as RequestInit,
  },
  "OpenEpic: eHealthExchange": configureEHX("OpenEpic"),
  "CernerHelios: eHealthExchange": configureEHX("CernerHelios"),
  "OPHDST Meld: Direct": {
    hostname: "https://gw.interop.community/CDCSepHL7Connectatho/open",
    init: {} as RequestInit,
  },
};

/**
 * Configure eHealthExchange for a specific destination.
 * @param xdestination The x-destination header value
 * @returns The configuration for the server
 */
function configureEHX(xdestination: string): FHIR_SERVER_CONFIG {
  let init: RequestInit = {
    method: "GET",
    headers: {
      Accept: "application/json, application/*+json, */*",
      "Accept-Encoding": "gzip, deflate, br",
      "Content-Type": "application/fhir+json; charset=UTF-8",
      "X-DESTINATION": xdestination,
      "X-POU": "PUBHLTH",
      "X-Request-Id": uuidv4(),
      prefer: "return=representation",
      "Cache-Control": "no-cache",
    } as HeaderInit,
  };
  if (xdestination === "CernerHelios" && init.headers) {
    (init.headers as Record<string, string>)["OAUTHSCOPES"] =
      "system/Condition.read system/Encounter.read system/Immunization.read system/MedicationRequest.read system/Observation.read system/Patient.read system/Procedure.read system/MedicationAdministration.read system/DiagnosticReport.read system/RelatedPerson.read";
  }
  return {
    hostname: "https://concept01.ehealthexchange.org:52780/fhirproxy/r4/",
    init: init,
  };
}

/**
 * A client for querying a FHIR server
 * @param server The FHIR server to query
 * @returns The client
 */
class FHIRClient {
  private hostname: string;
  private init;

  constructor(server: FHIR_SERVERS) {
    const config = fhirServers[server];
    this.hostname = config.hostname;
    this.init = config.init;
  }

  async get(path: string): Promise<Response> {
    return fetch(this.hostname + path, this.init);
  }

  async getBatch(paths: Array<string>): Promise<Array<Response>> {
    const fetchPromises = paths.map((path) =>
      fetch(this.hostname + path, this.init).then((response) => {
        return response;
      }),
    );

    return await Promise.all(fetchPromises);
  }
}

export default FHIRClient;
