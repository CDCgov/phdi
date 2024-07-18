import Image from "next/image";

/**
 * Produces the footer.
 * @returns The footer component.
 */
export default function FooterComponent() {
  return (
    <footer className="usa-footer">
      <div className="usa-footer__secondary-section max-w-full bg-primary-darker">
        <div className="header-footer-content grid-container usa-nav-container">
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
                  alt="CDC logo"
                  width={62}
                  height={36}
                  className="usa-footer__logo-img"
                />
              </div>
              <div className="mobile-lg:grid-col-auto">
                <p className="text-base-lightest">
                  Centers for Disease Control and Prevention
                </p>
              </div>
            </div>
            <div
              className="
                usa-footer__logo
                grid-row
                mobile-lg:grid-col-2 mobile-lg:grid-gap-1
              "
              style={{
                width: "20%",
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "center",
              }}
            >
              <div style={{ whiteSpace: "nowrap", textAlign: "right" }}>
                <p className="text-base-lightest">
                  For more information about this solution, send us an email at{" "}
                  <a
                    href="mailto:dibbs@cdc.gov"
                    style={{
                      color: "inherit",
                      fontWeight: "bold",
                      textDecoration: "underline",
                    }}
                  >
                    dibbs@cdc.gov
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
