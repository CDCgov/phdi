import { NextRequest, NextResponse } from "next/server";
import fs from "fs"
import { searchObject } from "./utils";



export async function POST(request: NextRequest) {
  const data = await request.formData()
  const file: File | null = data.get('file') as unknown as File;
  if(!file){
    return NextResponse.json({error: "File is null"}, {status: 500})
  }
  const templatePath = './views/index.mustache';
  const templateString = fs.readFileSync(templatePath, 'utf8');

  const bytes = await file.arrayBuffer();
  const buffer = await Buffer.from(bytes);
  const dataJSON = JSON.parse(buffer.toString('utf8'));
  const parsed = templateString.replace(/{{(.*?)}}/g, (_, key) => {
    return JSON.stringify(searchObject(dataJSON, key))
  });
  
  return NextResponse.json({ data: parsed, resourceType: "Bundle" }, { status: 200 });
  
}