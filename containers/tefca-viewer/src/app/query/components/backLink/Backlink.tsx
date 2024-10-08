import { Icon } from "@trussworks/react-uswds";

type BacklinkProps = {
  onClick: () => void;
  label: string;
};

/**
 *
 * @param root0 - params
 * @param root0.onClick - function to handle a click (likely a goBack function)
 * @param root0.label - Link label to display
 * @returns A backlink component styled according to Figma
 */
const Backlink: React.FC<BacklinkProps> = ({ onClick, label }) => {
  return (
    <a
      href="#"
      onClick={onClick}
      className="back-link unchanged-color-on-visit"
      aria-label="Back arrow indicating ability to navigate back a page if clicked"
    >
      <Icon.ArrowBack /> {label}
    </a>
  );
};

export default Backlink;
