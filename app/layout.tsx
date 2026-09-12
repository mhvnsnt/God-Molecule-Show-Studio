import type { Metadata } from 'next';
import Script from 'next/script';
import './globals.css';

export const metadata: Metadata = {
  title: 'God Molecule Studio',
  description:
    'The show-specific creative cockpit and production environment for God Molecule.',
  openGraph: {
    title: 'God Molecule Studio',
    description:
      'The show-specific creative cockpit and production environment for God Molecule.',
    type: 'website',
  },
  twitter: { card: 'summary_large_image' },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
        {/* Google Identity Services. afterInteractive, not beforeInteractive:
            the Character view checks for window.google inside an effect and
            polls until it lands, so blocking first paint on it buys nothing. */}
        <Script
          src="https://accounts.google.com/gsi/client"
          strategy="afterInteractive"
        />
      </body>
    </html>
  );
}
