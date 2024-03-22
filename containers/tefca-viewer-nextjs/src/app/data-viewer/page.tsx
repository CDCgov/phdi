"use client";
import {
  ProcessList,
  ProcessListItem,
  ProcessListHeading,
  Button,
  Link,
} from "@trussworks/react-uswds";
import { useRouter } from "next/navigation";

export default function UploadTutorial() {
  const router = useRouter();

  const handleClick = () => {
    router.push("/data-viewer");
  };

  return (
    <div className="display-flex flex-justify-center margin-top-5">
      <div>
        <h1 className="font-sans-2xl text-bold">Data viewer</h1>
      </div>
    </div>
  );
}
