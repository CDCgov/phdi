import Image from "next/image";

/**
 * Produces the header.
 * @returns The HeaderComponent component.
 */
export default function HeaderComponent() {
  return (
    <header className="usa-header usa-header--basic bg-primary-darker">
      <div
        className="header-footer-content usa-nav-container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center" }}>
          <Image
            src="/tefca-viewer/DIBBs_logo.png"
            alt="DIBBs Logo"
            width={168}
            height={34}
            className="usa-footer__logo-img"
          />
          <div className="usa-logo" style={{ marginLeft: "16px" }}>
            <em className="usa-logo__text text-base-lightest">
              <a
                className="text-base-lightest font-sans-lg text-bold"
                href="/tefca-viewer"
                title="TEFCA Viewer"
              >
                TEFCA Viewer
              </a>
            </em>
          </div>
        </div>
        <div
          style={{
            whiteSpace: "nowrap",
            textAlign: "right",
            marginLeft: "auto",
          }}
        >
          <p className="text-base-lightest">Data Usage Policy</p>
        </div>
      </div>
    </header>
  );
}
