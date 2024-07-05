import React from "react";

/**
 * Header component for the ECR Viewer project.
 * This component renders the header section of the application, including the
 * navigation container, navbar, and logo. It uses USWDS (U.S. Web Design System)
 * classes for styling.
 * @returns The header section of the application.
 */
const Header: React.FC = () => (
  <header className="usa-header usa-header--basic">
    <div className="usa-nav-container padding-left-0">
      <div className="usa-navbar">
        <div className="usa-logo">
          <em className="usa-logo__text">
            <a href="/" title="<Project title>">
              eCR Viewer
            </a>
          </em>
        </div>
      </div>
    </div>
  </header>
);

export default Header;
