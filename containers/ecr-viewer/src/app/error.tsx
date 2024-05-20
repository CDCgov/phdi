"use client"; // Error components must be Client Components

import { useEffect } from "react";

/**
 * Renders an Error component to display when an error occurs.
 * @param props - The props object.
 * @param props.error - The error object, possibly with a digest.
 * @returns - Returns the JSX element for the Error component.
 */
export default function Error({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div>
      <h2>Something went wrong!</h2>
    </div>
  );
}
