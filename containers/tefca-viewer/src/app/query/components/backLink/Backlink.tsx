import { Icon } from "@trussworks/react-uswds";

type BacklinkProps = {
  onClick: () => void;
  label: string;
};

const Backlink: React.FC<BacklinkProps> = ({ onClick, label }) => {
  return (
    <a href="#" onClick={onClick} className="back-link">
      <Icon.ArrowBack /> {label}
    </a>
  );
};

export default Backlink;
