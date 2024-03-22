import "../styles/styles.scss";
export const metadata = {
  title: "TEFCA Viewer",
  description: "Try out the TEFCA Viewer.",
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
