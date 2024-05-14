/**
 * Produces the header.
 * @returns The HeaderComponent component.
 */
export default function HeaderComponent() {
  return (
    <header className="usa-header usa-header--basic bg-primary-darker">
      <div className="usa-nav-container max-w-full">
        <div className="usa-navbar w-full">
          <div className="usa-logo">
            <em className="usa-logo__text text-base-lightest">
              <a
                className="text-base-lightest"
                href="/tefca-viewer"
                title="TryTEFCA Viewer"
              >
                TryTEFCA Viewer
              </a>
            </em>
          </div>
        </div>
      </div>
    </header>
  );
}
