import Script from 'next/script';

interface StructuredDataProps {
  type: 'website' | 'organization' | 'software' | 'product' | 'service';
  data: any;
}

export function StructuredData({ type, data }: StructuredDataProps) {
  const getStructuredData = () => {
    switch (type) {
      case 'website':
        return {
          "@context": "https://schema.org",
          "@type": "WebSite",
          "name": "VibeWave - AI-Powered Long-Form Media Content Creation",
          "alternateName": "VibeWave",
          "url": "https://clipizy.ai",
          "description": "Transform your audio into stunning music videos and automated social media content with advanced AI. Create professional long-form media content for social platforms in minutes.",
          "potentialAction": {
            "@type": "SearchAction",
            "target": "https://clipizy.ai/search?q={search_term_string}",
            "query-input": "required name=search_term_string"
          },
          "publisher": {
            "@type": "Organization",
            "name": "VibeWave",
            "url": "https://clipizy.ai"
          }
        };
      
      case 'organization':
        return {
          "@context": "https://schema.org",
          "@type": "Organization",
          "name": "VibeWave",
          "url": "https://clipizy.ai",
          "logo": "https://clipizy.ai/logo.png",
          "description": "Leading AI-powered platform for creating long-form media content, music videos, and automated social media posts for content creators and businesses.",
          "foundingDate": "2024",
          "sameAs": [
            "https://twitter.com/clipizy",
            "https://linkedin.com/company/clipizy",
            "https://youtube.com/@clipizy"
          ],
          "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+1-555-VIBEWAVE",
            "contactType": "customer service",
            "availableLanguage": "English"
          },
          "address": {
            "@type": "PostalAddress",
            "addressCountry": "US"
          }
        };
      
      case 'software':
        return {
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": "VibeWave AI Content Creator",
          "applicationCategory": "MultimediaApplication",
          "operatingSystem": "Web Browser",
          "description": "AI-powered platform for creating music videos, long-form media content, and automated social media posts. Transform audio into stunning visual content with advanced artificial intelligence.",
          "url": "https://clipizy.ai",
          "screenshot": "https://clipizy.ai/screenshot.jpg",
          "softwareVersion": "2.0",
          "datePublished": "2024-01-01",
          "dateModified": "2024-12-01",
          "author": {
            "@type": "Organization",
            "name": "VibeWave"
          },
          "offers": {
            "@type": "Offer",
            "price": "9.00",
            "priceCurrency": "USD",
            "priceValidUntil": "2025-12-31",
            "availability": "https://schema.org/InStock"
          },
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "ratingCount": "500",
            "bestRating": "5",
            "worstRating": "1"
          },
          "featureList": [
            "AI-powered music video generation",
            "Automated social media content creation",
            "Long-form media content production",
            "Multiple visual styles and themes",
            "4K video output quality",
            "Real-time collaboration tools",
            "Commercial usage rights",
            "API access for developers"
          ]
        };
      
      case 'product':
        return {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "VibeWave AI Content Creation Platform",
          "description": "Professional AI-powered platform for creating music videos, long-form media content, and automated social media posts. Perfect for content creators, musicians, and businesses.",
          "brand": {
            "@type": "Brand",
            "name": "VibeWave"
          },
          "category": "Software",
          "image": "https://clipizy.ai/product-image.jpg",
          "offers": [
            {
              "@type": "Offer",
              "name": "Starter Plan",
              "price": "9.00",
              "priceCurrency": "USD",
              "priceValidUntil": "2025-12-31",
              "availability": "https://schema.org/InStock",
              "description": "5 video generations per month, HD quality, basic styles"
            },
            {
              "@type": "Offer",
              "name": "Pro Plan",
              "price": "29.00",
              "priceCurrency": "USD",
              "priceValidUntil": "2025-12-31",
              "availability": "https://schema.org/InStock",
              "description": "50 video generations per month, 4K quality, all styles"
            },
            {
              "@type": "Offer",
              "name": "Team Plan",
              "price": "99.00",
              "priceCurrency": "USD",
              "priceValidUntil": "2025-12-31",
              "availability": "https://schema.org/InStock",
              "description": "200 video generations per month, team collaboration"
            }
          ],
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "ratingCount": "500",
            "bestRating": "5",
            "worstRating": "1"
          }
        };
      
      case 'service':
        return {
          "@context": "https://schema.org",
          "@type": "Service",
          "name": "AI-Powered Media Content Creation Service",
          "description": "Professional service for creating music videos, long-form media content, and automated social media posts using advanced AI technology.",
          "provider": {
            "@type": "Organization",
            "name": "VibeWave"
          },
          "areaServed": "Worldwide",
          "serviceType": "Content Creation",
          "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "VibeWave Services",
            "itemListElement": [
              {
                "@type": "Offer",
                "itemOffered": {
                  "@type": "Service",
                  "name": "Music Video Generation",
                  "description": "AI-powered creation of music videos from audio files"
                }
              },
              {
                "@type": "Offer",
                "itemOffered": {
                  "@type": "Service",
                  "name": "Social Media Automation",
                  "description": "Automated creation and scheduling of social media content"
                }
              },
              {
                "@type": "Offer",
                "itemOffered": {
                  "@type": "Service",
                  "name": "Long-Form Content Production",
                  "description": "Creation of extended video content for various platforms"
                }
              }
            ]
          }
        };
      
      default:
        return data;
    }
  };

  return (
    <Script
      id="structured-data"
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(getStructuredData(), null, 2)
      }}
    />
  );
}
