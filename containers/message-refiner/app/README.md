# eICR Spec 1.1 Notes

For the purpose of this documentation we'll be specifically focus on the contents of the `<structuredBody>` and how the various section-level and entry-level components are composed to create the body of an eICR document.

## Section-level vs entry-level components

In vol. 2 of the eICR 1.1 spec there are tables that explain the hierarchical relationship that comprises an eICR document. There are specific blocks of elements that are named and these names have associated metadata that both signal and connect them to other nested named blocks of elements. You can think of these named blocks of elements almost like classes in object oriented programming but without inheritance in a strict sense. Rather than inheritance they signal the hierarchical relationship between the named block of elements. Each named block of elements is governed by a template that describes what metadata it must, should, or may contain as well as the order of these metadata.

Section-level templates are higher up the hierarchy while entry-level templates are children of section-level templates. Some sections are **required** in order for an eICR document to be valid based on the associated schematron. Every single template has an id that is used to test each row of the template; these rules all have unique ids that are called conf numbers (`CONF#`). When validating an eICR document against the schematron the messages coming back are based on the `CONF#` and whether or not this is a fatal error, and error, or a warning.

Additionally there are some section-level templates that have templates for both:

- Entries optional, and;
- Entries required

These signifiers do not necessarily mean that a section **must** be present in order for a message to be valid. For example, the Immunizations Section can be completely removed from an eICR document without affecting the schematron validation process whereas doing the same thing to the Encounters Section would result in an error.

This might seem confusing, but the "entries required" vs "entries optional" deal with what is required by that specific `templateId`. One template does not require an `<entry>` (optional says `<entry>` _should_ be there but required says that it _shall_ be there).

### Encounters Section (V3)

Structure:

- Encounters Section (V3) `<section>`
  - Encounter Activity (V3) `<encounter>`
    - Encounter Diagnosis (V3) `<act>`
      - Problem Observation (V3) `<observation>`
      - Initial Case Report Manual Initiation Reason Observation `<observation>`
      - Initial Case Report Trigger Code Problem Observation `<observation>`

### History of Present Illness Section

> Doesn't contain any specific entry-level templates

### Immunizations Section (V3)

Structure:

- Immunizations Section (V3) `<section>`
  - Immunization Activity (V3) `<substanceAdministration>`
    - Immunization Medication Information (V2) `<manufacturedProduct>`

### Medications Administered Section (V2)

Structure:

- Medications Administered Section (V2) `<section>`
  - Medication Activity (V2) `<substanceAdministration>`
    - Medication Information (V2) `<manufacturedProduct>`

### Plan of Treatment Section (V2)

Structure:

- Plan of Treatment Section (V2) `<section>`
  - Planned Observation (V2) `<observation>`
  - Initial Case Report Trigger Code Lab Test Order `<observation>`

### Problem Section (V3)

Structure:

- Problem Section (V3) `<section>`
  - Problem Concern Act (V3) `<act>`
    - Problem Observation (V3) `<observation>`
    - Initial Case Report Trigger Code Problem Observation `<observation>`

### Reason for Visit Section

> Doesn't contain any specific entry-level templates

### Results Section (V3)

Structure:

- Results Section (V3) `<section>`
  - Result Organizer (V3) `<organizer>`
    - Result Observation (V3) `<observation>`
    - Initial Case Report Trigger Code Result Observation `<observation>`

### Social History Section (V3)

Structure:

- Social History Section (V3) `<section>`
  - Social History Observation (V3) `<observation>`
  - Pregnanacy Observation `<observation>`
    - Estimated Date of Delivery `<observation>`

## Trigger Code Templates

### Manually triggered

#### Section-level and entry-level components

| Parent Section          | LOINC code |
| ----------------------- | ---------- |
| Encounters Section (V3) | 46240-8    |

- Encounters Section (V3) `<section>`
  - Encounter Activity (V3) `<encounter>`
    - Encounter Diagnosis (V3) `<act>`
      - Problem Observation (V3) `<observation>`
      - **Initial Case Report Manual Initiation Reason Observation `<observation>`**

Manually triggered eICRs have the following `templateId`:

- `2.16.840.1.113883.10.20.15.2.3.5`

You can see an example of this being used below in the Problem Observation (V3). The `templateId`'s `root` attribute contains the above OID as its value.

#### Example from the sample files that ship with the spec:

```xml
<entryRelationship typeCode="COMP">
    <observation classCode="OBS" moodCode="EVN">
        <!-- [C-CDA R2.1] Problem Observation (V3) -->
        <templateId root="2.16.840.1.113883.10.20.22.4.4" extension="2015-08-01" />
        <!-- [eICR R2 STU1.1] Initial Case Report Manual Initiation Reason Observation -->
        <templateId root="2.16.840.1.113883.10.20.15.2.3.5" extension="2016-12-01" />
        <id root="ab1791b0-5c71-11db-b0de-0800200c9a65" />
        <code code="75322-8" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" displayName="Complaint">
            <translation code="409586006" codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT"
                displayName="Complaint" />
        </code>
        <statusCode code="completed" />
        <effectiveTime>
            <low value="20161106000000-0500" />
        </effectiveTime>
        <value xsi:type="CD" nullFlavor="OTH">
            <originalText>Free text containing the reason for the manual eICR document</originalText>
        </value>
    </observation>
</entryRelationship>
```

#### How to return

```xml
<entry>
  <encounter>
    <entryRelationship>
      <observation>
        Data we want
      </observation>
    </entryRelationship>
  </encounter>
</entry>
```

### Lab test order

| Parent Section                 | LOINC code |
| ------------------------------ | ---------- |
| Plan of Treatment Section (V2) | 18776-5    |

- Plan of Treatment Section (V2) `<section>`
  - Planned Observation (V2) `<observation>`
  - Initial Case Report Trigger Code Lab Test Order `<observation>`

Lab test order triggered eICRs have the following `templateId`:

- `2.16.840.1.113883.10.20.15.2.3.4`

You can see an example of this being used below in the Planned Observation (V3). The `templateId`'s `root` attribute contains the above OID as its value.

#### Example from the sample files that ship with the spec:

```xml
<entry typeCode="DRIV">
  <!-- This is a request for a test to be performed (a lab test order) -->
  <observation classCode="OBS" moodCode="RQO">
    <!-- [C-CDA R1.1] Plan of Care Activity Observation -->
    <templateId root="2.16.840.1.113883.10.20.22.4.44" />
    <!-- [C-CDA R2.0] Planned Observation (V2) -->
    <templateId root="2.16.840.1.113883.10.20.22.4.44" extension="2014-06-09" />
    <!-- [eICR R2 STU1.1] Initial Case Report Trigger Code Lab Test Order -->
    <templateId root="2.16.840.1.113883.10.20.15.2.3.4" extension="2016-12-01" />
    <id root="b52bee94-c34b-4e2c-8c15-5ad9d6def205" />
    <!-- This code is from the trigger codes for laboratory test order
         value set (2.16.840.1.113762.1.4.1146.166) -->
    <code code="80825-3" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
      displayName="Zika virus envelope (E) gene [Presence] in Serum by Probe and target amplification method"
      sdtc:valueSet="2.16.840.1.114222.4.11.7508" sdtc:valueSetVersion="19/05/2016" />
    <statusCode code="active" />
    <!-- Date on which the lab test should take place -->
    <effectiveTime value="20161108" />
  </observation>
</entry>
```

#### How to return

```xml
<entry>
  <observation>
    Data we want
  </observation>
</entry>
```

### Problem observation

| Parent Section         | LOINC code |
| ---------------------- | ---------- |
| Encounter Section (V3) | 46240-8    |
| Problem Section (V3)   | 11450-4    |

- Encounters Section (V3) `<section>`
  - Encounter Activity (V3) `<encounter>`
    - Encounter Diagnosis (V3) `<act>`
      - Problem Observation (V3) `<observation>`
      - **Initial Case Report Trigger Code Problem Observation `<observation>`**

**Or:**

- Problem Section (V3) `<section>`
  - Problem Concern Act (V3) `<act>`
    - Problem Observation (V3) `<observation>`
    - Initial Case Report Trigger Code Problem Observation `<observation>`

Problem observation triggered eICRs have the following `templateId`:

- `2.16.840.1.113883.10.20.15.2.3.3`

You can see an example of this being used below in the Problem Observation (V3). The `templateId`'s `root` attribute contains the above OID as its value.

#### Example from the sample files that ship with the spec:

```xml
<entryRelationship typeCode="SUBJ">
  <observation classCode="OBS" moodCode="EVN" negationInd="false">
    <!-- [C-CDA R1.1] Problem Observation -->
    <templateId root="2.16.840.1.113883.10.20.22.4.4" />
      <!-- [C-CDA R2.1] Problem Observation (V3) -->
      <templateId root="2.16.840.1.113883.10.20.22.4.4" extension="2015-08-01" />
      <!-- [eICR R2 STU1.1] Initial Case Report Trigger Code Problem Observation -->
      <templateId root="2.16.840.1.113883.10.20.15.2.3.3" extension="2016-12-01" />
      <id root="db734647-fc99-424c-a864-7e3cda82e705" />
      <code code="29308-4" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" displayName="Diagnosis">
        <translation code="282291009" codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT"
          displayName="Diagnosis" />
      </code>
      <statusCode code="completed" />
      <effectiveTime>
        <low value="20161107" />
      </effectiveTime>
      <!-- Trigger code -->
      <value xsi:type="CD" code="27836007" codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT"
        displayName="Pertussis (disorder)" sdtc:valueSet="2.16.840.1.114222.4.11.7508"
        sdtc:valueSetVersion="19/05/2016" />
  </observation>
</entryRelationship>
```

#### How to return

This will depend on the `typeCode` of the `<entryRelationship>` element. In the example above we have nested `<entryRelationship>` tags with a `typeCode="SUBJ"`, which means that as you continue to navigate towards the last child `<entryRelationship>` tag you end up with the subject (`SUBJ`) of the `<entry>`. This means that there may need to be either some cleaning out of additional `<entryRelationship>` blocks that are merely referenced (`REFE`) or a part of/component of (`COMP`) and `<entry>` rather than the main reason for the data.

```xml
<entry>
  <encounter>
    <entryRelationship>
      <act>
        <entryRelationship>
          <observation>
            <entryRelationship>
              Data we want
            </entryRelationship>
          </observation>
        </entryRelationship>
      </act>
    </entryRelationship>
  </encounter>
</entry>
```

### Result observation

| Parent Section       | LOINC code |
| -------------------- | ---------- |
| Results Section (V3) | 30954-2    |

- Results Section (V3) `<section>`
  - Result Organizer (V3) `<organizer>`
    - Result Observation (V3) `<observation>`
    - **Initial Case Report Trigger Code Result Observation `<observation>`**

Result observation triggered eICRs have the following `templateId`:

- `2.16.840.1.113883.10.20.15.2.3.2`

You can see an example of this being used below in the Result Observation (V3). The `templateId`'s `root` attribute contains the above OID as its value.

#### Example from the sample files that ship with the spec:

```xml
<component>
  <!-- This observation is a trigger code preliminary result observation -
        both the code and value are trigger codes and thus
        both the code and the value must contain @sdtc:valueSet and @sdtc:valueSetVersion.
        Preliminary result is indicated by statusCode="active" -->
  <observation classCode="OBS" moodCode="EVN">
    <!-- [C-CDA R1.1] Result Observation -->
    <templateId root="2.16.840.1.113883.10.20.22.4.2" />
    <!-- [C-CDA R2.1] Result Observation (V3) -->
    <templateId root="2.16.840.1.113883.10.20.22.4.2" extension="2015-08-01" />
    <!-- [eICR R2 STU1.1] Initial Case Report Trigger Code Result Observation -->
    <templateId root="2.16.840.1.113883.10.20.15.2.3.2" extension="2016-12-01" />
    <id root="bf9c0a26-4524-4395-b3ce-100450b9c9ac" />
    <!-- This code is a trigger code from RCTC subset: "Trigger code for laboratory test names"
          @sdtc:valueSet and @sdtc:valueSetVersion shall be present -->
    <code code="548-8" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC"
      displayName="Bordetella pertussis [Presence] in Throat by Organism specific culture"
      sdtc:valueSet="2.16.840.1.114222.4.11.7508" sdtc:valueSetVersion="19/05/2016" />
    <!-- statusCode is set to active indicating that this is a preliminary result -->
    <statusCode code="active" />
    <effectiveTime value="20161107" />
    <!-- This value is a trigger code from RCTC subset: "Trigger code for organism or substance"
          @sdtc:valueSet and @sdtc:valueSetVersion shall be present -->
    <value xsi:type="CD" code="5247005" displayName="Bordetella pertussis (organism)"
      codeSystem="2.16.840.1.113883.6.96" codeSystemName="SNOMED CT" sdtc:valueSet="2.16.840.1.114222.4.11.7508"
      sdtc:valueSetVersion="19/05/2016" />
    <!-- This interpretation code denotes that this patient value is abnormal
         (bordetella pertussis (organism) was present in the culture) -->
    <interpretationCode code="A" displayName="Abnormal" codeSystem="2.16.840.1.113883.5.83"
      codeSystemName="ObservationInterpretation" />
  </observation>
</component>
```

#### How to return

This `<entry>` **must** contain what is called a "results organizer", which is the `<organizer>` child immediately after the `<entry>`. The trigger code `<observation>` is then wrapped in a `<component>` as a child of `<organizer>`.

```xml
<entry>
  <organizer>
    <component>
      <observation>
        Data we want
      </observation>
    </component>
  </organizer>
</entry>
```
