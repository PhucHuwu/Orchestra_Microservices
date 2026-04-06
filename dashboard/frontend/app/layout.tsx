import "./globals.css";

import type { Metadata } from "next";
import { Fraunces, IBM_Plex_Sans } from "next/font/google";
import { ReactNode } from "react";

import { Providers } from "./providers";

const headingFont = Fraunces({
  subsets: ["latin"],
  variable: "--font-heading",
  weight: ["600", "700"]
});

const bodyFont = IBM_Plex_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600"]
});

export const metadata: Metadata = {
  title: "Orchestra Dashboard",
  description: "Control and monitor Orchestra Microservices"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${headingFont.variable} ${bodyFont.variable}`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
