import "../styles/styles.scss";
export const metadata = {
  title: "DIBBs eCR Viewer",
  description: "View an eCR the easy way",
};

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
