import type {Metadata} from 'next';
import './globals.css';
import { Toaster } from "@/components/ui/toaster"
import { ConditionalLayout } from "@/components/layout/conditional-layout"
import { AuthProvider } from "@/contexts/auth-context"
import { PricingProvider } from "@/contexts/pricing-context"
import { ThemeProvider } from "@/contexts/ThemeContext"

export const metadata: Metadata = {
  title: 'VibeWave - AI-Powered Long-Form Media Content Creation Platform',
  description: 'Transform your audio into stunning music videos and automated social media content with advanced AI. Create professional long-form media content for social platforms in minutes. Perfect for content creators, musicians, and businesses.',
  keywords: 'AI music video generator, automated social media content, long-form media creation, AI video generation, social media automation, content creation platform, music video maker, AI content creator, video automation, social media posts generator, TikTok video creator, Instagram content automation, YouTube video maker, AI video editor, automated content creation, social media management, content marketing automation, video production AI, music video AI, social media AI tools',
  authors: [{ name: 'VibeWave Team' }],
  creator: 'VibeWave',
  publisher: 'VibeWave',
  applicationName: 'VibeWave',
  generator: 'Next.js',
  referrer: 'origin-when-cross-origin',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://clipizy.ai'),
  alternates: {
    canonical: 'https://clipizy.ai',
  },
  openGraph: {
    title: 'VibeWave - AI-Powered Long-Form Media Content Creation Platform',
    description: 'Transform your audio into stunning music videos and automated social media content with advanced AI. Create professional long-form media content for social platforms in minutes.',
    url: 'https://clipizy.ai',
    siteName: 'VibeWave',
    images: [
      {
        url: 'https://clipizy.ai/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'VibeWave - AI-Powered Long-Form Media Content Creation',
        type: 'image/jpeg',
      },
      {
        url: 'https://clipizy.ai/og-image-square.jpg',
        width: 1200,
        height: 1200,
        alt: 'VibeWave - AI Content Creation Platform',
        type: 'image/jpeg',
      },
    ],
    locale: 'en_US',
    type: 'website',
    countryName: 'United States',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VibeWave - AI-Powered Long-Form Media Content Creation',
    description: 'Transform your audio into stunning music videos and automated social media content with advanced AI. Create professional content in minutes.',
    images: ['https://clipizy.ai/og-image.jpg'],
    creator: '@clipizy',
    site: '@clipizy',
  },
  robots: {
    index: true,
    follow: true,
    nocache: false,
    googleBot: {
      index: true,
      follow: true,
      noimageindex: false,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
    yandex: 'your-yandex-verification-code',
    yahoo: 'your-yahoo-verification-code',
  },
  category: 'Technology',
  classification: 'AI Content Creation Platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#6366f1" />
        <meta name="msapplication-TileColor" content="#6366f1" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="VibeWave" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="format-detection" content="address=no" />
        <meta name="format-detection" content="email=no" />
      </head>
      <body className="font-sans antialiased">
        <ThemeProvider>
          <AuthProvider>
            <PricingProvider>
              <ConditionalLayout>
                {children}
              </ConditionalLayout>
            </PricingProvider>
          </AuthProvider>
        </ThemeProvider>
        <Toaster />
      </body>
    </html>
  );
}
