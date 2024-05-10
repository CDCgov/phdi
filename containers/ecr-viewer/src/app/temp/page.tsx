/**
 * Functional component for rendering the eCR Viewer page.
 * @returns The main eCR Viewer JSX component.
 */
import { trace } from "@opentelemetry/api";

function delayedTask() {
  console.log("3 seconds have passed!");
}

/**
 * sdfsdf
 * @returns something
 */
async function fetchGithubStars() {
  return await trace
    .getTracer("ecr-viewer")
    .startActiveSpan("fetchGithubStars", async (span) => {
      try {
        return await setTimeout(delayedTask, 3000);
      } finally {
        span.end();
      }
    });
}
/**
 * dffdsfsd
 * @returns something
 */
const ECRViewerPage: React.FC = () => {
  fetchGithubStars();
  return <div>Hello</div>;
};

export default ECRViewerPage;
