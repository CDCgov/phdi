import "../styles/styles.scss";
import Header from "./header"
import Footer from "./footer"
import { DataProvider } from "./utils"


export const metadata = {
  title: "TEFCA Viewer",
  description: "Try out the TEFCA Viewer.",
};

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