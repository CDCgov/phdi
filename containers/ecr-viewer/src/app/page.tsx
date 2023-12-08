// pages/index.js

"use client"

import { useEffect, useState } from 'react';


const HomePage = ({ data }) => {
  const [firstRow, setFirstRow] = useState(data);

  useEffect(() => {
    // Fetch the first row from the PostgreSQL database
    const fetchData = async () => {
      try {
        const response = await fetch('/api/data?id=345');
        const newData = await response.json();
        setFirstRow(newData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1>Hello, Next.js!</h1>
      <p>First Row from PostgreSQL Database:</p>
      <pre>{JSON.stringify(firstRow, null, 2)}</pre>
    </div>
  );
};

// export const getStaticProps = async () => {
//   // Fetch data during build time
//   const db = require('pg-promise')();
//   const database = db(process.env.DATABASE_URL);
//   const data = await database.one('SELECT * FROM your_table LIMIT 1');
//
//   return {
//     props: { data },
//   };
// };

export default HomePage;