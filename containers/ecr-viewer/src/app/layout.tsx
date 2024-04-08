import "../styles/styles.scss";
export const metadata = {
  title: "DIBBs eCR Viewer",
  description: "View your eCR data in an easy-to-understand format.",
};

/**
 *
 * @param root0
 * @param root0.children
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
