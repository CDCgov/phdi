import { Icon } from "@trussworks/react-uswds";

type BacklinkProps = {
  onClick: () => void;
  label: string;
};

/**
 *
 * @param root0
 * @param root0.onClick
 * @param root0.label
 */
const Backlink: React.FC<BacklinkProps> = ({ onClick, label }) => {
  return (
    <a href="#" onClick={onClick} className="back-link">
      <Icon.ArrowBack /> {label}
    </a>
  );
};

export default Backlink;
