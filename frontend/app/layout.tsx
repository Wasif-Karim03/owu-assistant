import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OWU Campus Assistant",
  description:
    "Get instant answers to your Ohio Wesleyan University questions — events, offices, deadlines, resources, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
