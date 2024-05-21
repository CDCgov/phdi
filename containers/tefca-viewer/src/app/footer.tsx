//import Image from 'next/image'

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
            >
              <div className="mobile-lg:grid-col-auto">
                {/* <Image
                  src="/CDC_logo.png"
                  className="usa-footer__logo-img"
                  alt="CDC logo"
                  width={62}
                  height={36}
                /> */}
              </div>
              <div className="mobile-lg:grid-col-auto">
                <p className=" text-base-lightest usa-footer__logo-heading">
                  Centers for Disease Control and Prevention
                </p>
                <p className="text-base-lightest">
                  For more information send us an email at dibbs@cdc.gov or
                  visit{"  "}
                  <a
                    href="https://cdcgov.github.io/dibbs-site/"
                    className="text-base-lightest"
                  >
                    our website
                  </a>
                  .
                </p>
              </div>
            </div>
            <div
              className="
                usa-footer__logo
                grid-row
                mobile-lg:grid-col-2 mobile-lg:grid-gap-1
                right-justified-text
              "
            >
              <div className="mobile-lg:grid-col-auto right-justified-text">
                <p className="text-base-lightest usa_footer-trademark right-justified-text">
                  © 2024 CDC. All rights reserved.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
