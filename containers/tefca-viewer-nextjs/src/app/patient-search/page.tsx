// "use client";

// import { useFormState, useFormStatus } from "react-dom";
// import { createTodo } from "@/app/utils.tsx";

// const initialState = {
//     message: "",
// };

// function SubmitButton() {
//     const { pending } = useFormStatus();

//     return (
//         <button type="submit" aria-disabled={pending}>
//             Add
//         </button>
//     );
// }

// export function AddForm() {
//     const [state, formAction] = useFormState(createTodo, initialState);

//     return (
//         <form action={formAction}>
//             <label htmlFor="todo">Enter Task</label>
//             <input type="text" id="todo" name="todo" required />
//             <SubmitButton />
//             <p aria-live="polite" className="sr-only" role="status">
//                 {state?.message}
//             </p>
//         </form>
//     );
// }

"use client";
import React, { useState } from "react";

const PatientSearch: React.FC = () => {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<string>("");

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log("First Name:", firstName);
    console.log("Last Name:", lastName);
    console.log("FHIR Server:", fhirServer);
  };

  return (
    <div>
      <h1>Patient Search</h1>
      <link
        rel="stylesheet"
        type="text/css"
        href="patient-search/style.css"
      ></link>

      <div>
        <label htmlFor="fhirServer">FHIR Server:</label>
        <select
          id="fhirServer"
          value={fhirServer}
          onChange={(event) => {
            setFhirServer(event.target.value);
          }}
          required
        >
          <option value="">Select FHIR Server</option>
          <option value="meld">Meld</option>
          <option value="ehealth-exchange">eHealth Exchange</option>
        </select>
      </div>
      <div>
        <label htmlFor="firstName">First Name:</label>
        <input
          type="text"
          id="firstName"
          value={firstName}
          onChange={(event) => {
            setFirstName(event.target.value);
          }}
        />
      </div>
      <div>
        <label htmlFor="lastName">Last Name:</label>
        <input
          type="text"
          id="lastName"
          value={lastName}
          onChange={(event) => {
            setLastName(event.target.value);
          }}
        />
      </div>
      <button type="button" onClick={handleSubmit}>
        Submit
      </button>
    </div>
  );
};

export default PatientSearch;
