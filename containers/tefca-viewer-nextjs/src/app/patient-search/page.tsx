"use client";
import React, { useState } from "react";

const Page: React.FC = () => {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<string>("");

  const handleFirstNameChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    setFirstName(event.target.value);
  };

  const handleLastNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLastName(event.target.value);
  };

  const handleFhirServerChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ) => {
    setFhirServer(event.target.value);
  };

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
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fhirServer">FHIR Server:</label>
          <select
            id="fhirServer"
            value={fhirServer}
            onChange={handleFhirServerChange}
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
            onChange={handleFirstNameChange}
            required
          />
        </div>
        <div>
          <label htmlFor="lastName">Last Name:</label>
          <input
            type="text"
            id="lastName"
            value={lastName}
            onChange={handleLastNameChange}
            required
          />
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default Page;

// 'use client'
// import { ProcessList, ProcessListItem, ProcessListHeading, Button, Link, Form } from '@trussworks/react-uswds'
// import { useRouter } from 'next/navigation';
// import { useState } from 'react';

// const router = useRouter();

// const MyForm = () => {
//     const handleClick = () => {
//         router.push('/data-viewer')
//     }
//     const [formData, setFormData] = useState({
//         name: '',
//         email: '',
//         message: '',
//     });

//     const handleChange = (e) => {
//         setFormData({ ...formData, [e.target.name]: e.target.value });
//     };

//     return (
//         <form onSubmit={handleClick}>
//             <input
//                 type="text"
//                 name="name"
//                 value={formData.name}
//                 onChange={handleChange}
//                 placeholder="Your Name"
//             />
//             <input
//                 type="email"
//                 name="email"
//                 value={formData.email}
//                 onChange={handleChange}
//                 placeholder="Your Email"
//             />
//             <textarea
//                 name="message"
//                 value={formData.message}
//                 onChange={handleChange}
//                 placeholder="Your Message"
//             ></textarea>
//             <Button type="button" onClick={handleClick}>Submit</Button>
//         </form>
//     );
// };

// export default MyForm;
