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
        style={{ display: "flex", alignItems: "center" }}
      >
        <div className="grid-row grid-gap">
          <div
            className="
                usa-footer__logo
                grid-row
                mobile-lg:grid-col-10 mobile-lg:grid-gap-1
              "
            style={{ width: "80%" }}
          >
            <div className="mobile-lg:grid-col-auto">
              <Image
                src="/tefca-viewer/CDC_logo.png"
                alt="DIBBs Logo"
                width={62}
                height={36}
                className="usa-footer__logo-img"
              />
            </div>
            <div className="mobile-lg:grid-col-auto">
              <em className="usa-logo__text text-base-lightest">
                <a
                  className="text-base-lightest font-sans-2xl text-bold"
                  href="/tefca-viewer"
                  title="Pipeline Demo Site"
                >
                  Pipeline Demo Site
                </a>
              </em>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
