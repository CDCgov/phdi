import { NextRequest, NextResponse } from "next/server";
import fs from "fs"
import { searchObject } from "./utils";
import pgPromise from "pg-promise";

export async function GET() {
  const db = require('pg-promise')();
  console.log("DATABASE_URL: ", process.env.DATABASE_URL)
  const database = db(process.env.DATABASE_URL);

  try {
    const data = await database.one('SELECT * FROM fhir LIMIT 1');
    console.log("data parse success!")
    console.log(data)
    // res.status(200).json(data);
  } catch (error) {
    console.error('Error fetching data:', error);
    // res.status(500).json({ error: 'Internal Server Error' });
  }

  return NextResponse.json({ data: data, resourceType: "Bundle" }, { status: 200 });

  // const data = await request.formData()
  // const file: File | null = data.get('file') as unknown as File;
  // if(!file){
  //   return NextResponse.json({error: "File is null"}, {status: 500})
  // }
  // const templatePath = './views/index.mustache';
  // const templateString = fs.readFileSync(templatePath, 'utf8');
  //
  // const bytes = await file.arrayBuffer();
  // const buffer = await Buffer.from(bytes);
  // const dataJSON = JSON.parse(buffer.toString('utf8'));
  // const parsed = templateString.replace(/{{(.*?)}}/g, (_, key) => {
  //   return JSON.stringify(searchObject(dataJSON, key))
  // });
  //
  // return NextResponse.json({ data: parsed, resourceType: "Bundle" }, { status: 200 });
  
}

export const getStaticProps = async () => {
  // Fetch data during build time
  const db = require('pg-promise')();
  const database = db(process.env.DATABASE_URL);
  const data = await database.one('SELECT * FROM your_table LIMIT 1');

  return {
    props: { data },
  };
};