import "../styles/styles.scss";
export const metadata = {
  title: "DIBBs eCR Viewer",
  description: "View your eCR data in an easy-to-understand format.",
};

/**
 * `RootLayout` serves as the top-level layout component for a React application.
 * @param props - The properties passed to the component.
 * @param props.children - The child components or elements to be rendered within
 *   the `<body>`f tag of the HTML document.
 * @returns A React element representing the top-level HTML structure, with the
 *   `children` rendered inside the `<body>` tag.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
