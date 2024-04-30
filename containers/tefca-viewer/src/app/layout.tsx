import "../styles/styles.scss";
import Header from "./header"
import Footer from "./footer"
import { DataProvider } from "./utils"


export const metadata = {
  title: "TEFCA Viewer",
  description: "Try out TEFCA with queries for public health use cases.",
};

/**
 * Establishes the layout for the application.
 * @param {object} props - Props for the component.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        <div className="main-body">
         <DataProvider>
           {children}
         </DataProvider>
        </div>
        <Footer />
        </body>
    </html>
  )
}