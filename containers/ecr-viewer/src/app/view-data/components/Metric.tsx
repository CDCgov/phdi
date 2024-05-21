"use client";
import { useEffect } from "react";
import { metrics } from "@/app/view-data/component-utils";

const basePath = process.env.NODE_ENV === "production" ? "/ecr-viewer" : "";

/**
 * Empty component used to track metrics
 * @param props - Properties for metrics
 * @param props.fhirId - FhirId of the page visited
 * @returns - An empty tag
 */
const Metric = ({ fhirId }: { fhirId: string }) => {
  useEffect(() => {
    const startTime = performance.now();
    window.addEventListener("beforeunload", async function (_e) {
      await metrics(basePath, {
        startTime: startTime,
        endTime: performance.now(),
        fhirId: `${fhirId}`,
      });
    });
  });

  return <></>;
};

export default Metric;
