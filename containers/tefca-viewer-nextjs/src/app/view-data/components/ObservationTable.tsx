import React from 'react';
import { Table } from '@trussworks/react-uswds';

interface Observation {
    id: string;
    typeDisplay: string;
    typeCode: string;
    typeSystem: string;
    valueString: string;
    valueQuantity: string;
    valueUnit: string;
    valueDisplay: string;
    valueCode: string;
    valueSystem: string;
    interpDisplay: string;
    interpCode: string;
    interpSystem: string;
    effectiveDateTime: string;
    referenceRangeHigh: string;
    referenceRangeLow: string;
    referenceRangeHighUnit: string;
    referenceRangeLowUnit: string;
}

interface ObservationTableProps {
    observation: Observation[];
}

export default function ObservationTable(props: ObservationTableProps) {
    return (
        <Table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Interpretation</th>
                    <th>Value</th>
                    <th>Reference Range</th>
                </tr>
            </thead>
            <tbody>
                {props.observation.map((obs) => (
                    <tr key={obs.id}>
                        <td>{obs.effectiveDateTime}</td>
                        <td>{[obs.typeDisplay, obs.typeCode, obs.typeSystem].join("\n")}</td>
                        <td>{[obs.interpDisplay, obs.interpCode, obs.interpSystem].join("\n")}</td>
                        <td>{obs.valueString || [obs.valueQuantity, obs.valueUnit].join(" ") || [obs.valueDisplay, obs.valueCode, obs.valueSystem].join("\n")}</td>
                        <td>{["HIGH:", obs.referenceRangeHigh, obs.referenceRangeHighUnit].join(" ") + "\n" + ["LOW:", obs.referenceRangeLow, obs.referenceRangeLowUnit].join(" ")}</td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
}
