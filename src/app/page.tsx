"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { VideoTheater } from "@/components/common/video-theater";
import { StructuredData } from "@/components/seo/structured-data";
import { EmailSubscription } from "@/components/common/email-subscription";
import { useTheme } from "@/contexts/ThemeContext";
import {
  Sparkles,
  Zap,
  Users,
  Clock,
  Palette,
  Music,
  Video,
  Wand2,
  Check,
  Star,
  ArrowRight,
  ArrowUp,
  Play,
  Download,
  Share2,
  Heart,
  Eye,
  Maximize2,
  ExternalLink,
  FileText,
  Shield,
  Paperclip
} from "lucide-react";

const features = [
  {
    icon: Wand2,
    title: "AI-Powered Content Generation",
    description: "Advanced AI algorithms create stunning music and videos, social media content, and long-form media from your audio in minutes, not hours."
  },
  {
    icon: Palette,
    title: "Multiple Visual Styles & Themes",
    description: "Choose from various visual styles including abstract, cinematic, animated, and more. Optimized for different social media platforms and content types."
  },
  {
    icon: Music,
    title: "Smart Audio Analysis & Sync",
    description: "Intelligent audio analysis automatically syncs visuals with your music. Creates engaging content that resonates with your audience."
  },
  {
    icon: Video,
    title: "4K High Quality Output",
    description: "Export your videos in up to 4K resolution with professional-grade quality and smooth playback. Perfect for all social media platforms and professional use."
  },
  {
    icon: Clock,
    title: "Lightning Fast Processing",
    description: "Generate complete music and videos and social media content automatically with our optimized AI processing. Scale your content creation effortlessly."
  },
  {
    icon: Users,
    title: "Analytics & Insights",
    description: "Track your content performance and get insights on what's working and what's not. Centralized analytics for all your content."
  }
];

const pricingPlans = [
  {
    name: "Free Tier",
    price: "Free",
    period: "",
    description: "Perfect for trying out clipizy",
    features: [
      "60 Credits Included",
      "720p Max",
      "500 MB Cloud Storage",
      "Community Support"
    ],
    popular: false,
    cta: "Start Free"
  },
  {
    name: "Tier 1: Creator",
    price: "$25",
    period: "/month",
    description: "Perfect for content creators and influencers",
    features: [
      "1,500 Credits Included",
      "1080p Full HD (No Watermark)",
      "10 GB Cloud Storage",
      "Video Automation Access (Scheduling Only)",
      "Commercial Licensing",
      "Email Support (Standard SLA)"
    ],
    popular: true,
    cta: "Upgrade to Creator"
  },
  {
    name: "Tier 2: Pro",
    price: "$59",
    period: "/month",
    description: "For professional creators and agencies",
    features: [
      "5,000 Credits Included",
      "1080p Full HD",
      "50 GB Cloud Storage",
      "Video Automation Access (Auto-Upload Included)",
      "1 Upload/Day Automated",
      "Email Support (Standard SLA)"
    ],
    popular: false,
    cta: "Upgrade to Pro"
  },
  {
    name: "Tier 3: Business",
    price: "$119",
    period: "/month",
    description: "For large teams and organizations",
    features: [
      "12,500 Credits Included",
      "1080p Full HD",
      "150 GB Cloud Storage",
      "Premium Model LLM",
      "Video Automation Access (Advanced Queue Management)",
      "5 Uploads/Day Automated",
      "Priority Queue Access",
      "Priority Email Support"
    ],
    popular: false,
    cta: "Upgrade to Business"
  }
];

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Music Producer & Content Creator",
    content: "VibeWave has revolutionized how I create music videos and social media content. What used to take days now takes minutes! The automated posting feature saves me hours every week.",
    avatar: "SC"
  },
  {
    name: "Marcus Rodriguez",
    role: "Social Media Manager",
    content: "The AI understands my content strategy better than I do. The visual sync is absolutely perfect every time, and the social media automation has increased our engagement by 300%.",
    avatar: "MR"
  },
  {
    name: "Emily Watson",
    role: "Marketing Director",
    content: "We've cut our video production costs by 80% while improving quality and scaling our content output. VibeWave's long-form content creation is a complete game-changer for our brand.",
    avatar: "EW"
  }
];

const stats = [
  { number: "50K+", label: "Videos & Content Created" },
  { number: "2K+", label: "Active Content Creators" },
  { number: "99.9%", label: "Platform Uptime" },
  { number: "4.9/5", label: "User Satisfaction Rating" }
];

const placeholderTexts = [
  "Create a music video for my latest track",
  "Generate visuals for an electronic dance song",
  "Make a video with cinematic abstract visuals",
  "Build a music clip with vibrant colors",
  "Produce a professional music video"
];

export default function Home() {
  const { theme, resolvedTheme } = useTheme();
  const router = useRouter();
  const [theaterVideo, setTheaterVideo] = useState<{
    src: string;
    title: string;
    description: string;
  } | null>(null);
  const [prompt, setPrompt] = useState("");
  const [animatedPlaceholder, setAnimatedPlaceholder] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const [currentPlaceholderIndex, setCurrentPlaceholderIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!isTyping) return;

    const currentText = placeholderTexts[currentPlaceholderIndex];
    
    if (!isDeleting && animatedPlaceholder.length < currentText.length) {
      const timeout = setTimeout(() => {
        setAnimatedPlaceholder(currentText.slice(0, animatedPlaceholder.length + 1));
      }, 50);
      return () => clearTimeout(timeout);
    } else if (!isDeleting && animatedPlaceholder.length === currentText.length) {
      const timeout = setTimeout(() => {
        setIsDeleting(true);
      }, 2000);
      return () => clearTimeout(timeout);
    } else if (isDeleting && animatedPlaceholder.length > 0) {
      const timeout = setTimeout(() => {
        setAnimatedPlaceholder(currentText.slice(0, animatedPlaceholder.length - 1));
      }, 30);
      return () => clearTimeout(timeout);
    } else if (isDeleting && animatedPlaceholder.length === 0) {
      setIsDeleting(false);
      setCurrentPlaceholderIndex((prev) => (prev + 1) % placeholderTexts.length);
    }
  }, [animatedPlaceholder, isDeleting, currentPlaceholderIndex, isTyping]);

  const handleInputFocus = () => {
    setIsTyping(false);
    setAnimatedPlaceholder("");
  };

  const handleInputBlur = () => {
    if (!prompt) {
      setIsTyping(true);
      setAnimatedPlaceholder("");
      setIsDeleting(false);
    }
  };

  const handleGenerate = () => {
    router.push("/dashboard/create");
  };

  const handleUploadTrack = () => {
    router.push("/dashboard/create");
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleGenerate();
    }
  };

  const openTheater = (src: string, title: string, description: string) => {
    setTheaterVideo({ src, title, description });
  };

  const closeTheater = () => {
    setTheaterVideo(null);
  };

  return (
    <div className="min-h-screen">
      {/* STRUCTURED DATA */}
      <StructuredData type="website" data={{}} />
      <StructuredData type="organization" data={{}} />
      <StructuredData type="software" data={{}} />
      <StructuredData type="product" data={{}} />
      <StructuredData type="service" data={{}} />
      
      {/* HERO BANNER SECTION */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 animated-bg"></div>
        <div className="absolute inset-0 hero-gradient"></div>
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10"></div>
        <video
          className="absolute inset-0 w-full h-full object-cover opacity-15"
          autoPlay
          loop
          muted
          onLoadedMetadata={(e) => {
            e.currentTarget.currentTime = 9;
          }}
          onError={(e) => {
            e.currentTarget.style.display = 'none';
          }}
        >
          <source src="/media/hero_section.mp4" type="video/mp4" />
        </video>

        <div className="relative container-custom">
          <div className="text-center max-w-5xl mx-auto">
            {/* MAIN HEADLINE */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 fade-in-up" style={{ lineHeight: '1.2' }}>
              Turn Your Music Into
              <span className="gradient-text-ai block pb-4">Stunning Videos</span>
            </h1>

            {/* PROMPT INPUT SECTION */}
            <div className="max-w-4xl mx-auto mb-12 fade-in-up">
              <div className="relative">
                <div className="relative">
                  <Input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onFocus={handleInputFocus}
                    onBlur={handleInputBlur}
                    onKeyDown={handleKeyPress}
                    placeholder=""
                    className="w-full h-16 md:h-20 text-lg md:text-xl px-6 md:px-8 py-6 rounded-2xl bg-white/95 dark:bg-gray-900/95 border-2 border-primary/20 focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all duration-300 shadow-lg pr-32"
                  />
                  {!prompt && isTyping && (
                    <div className="absolute left-6 md:left-8 top-1/2 -translate-y-1/2 text-lg md:text-xl text-muted-foreground/60 pointer-events-none flex items-center">
                      <span>{animatedPlaceholder}</span>
                      <span className="inline-block w-0.5 h-5 md:h-6 ml-1 bg-primary" style={{ animation: 'blink 1s infinite' }}>|</span>
                    </div>
                  )}
                </div>
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  <Button
                    onClick={handleUploadTrack}
                    size="lg"
                    variant="ghost"
                    className="h-12 md:h-14 w-12 md:w-14 rounded-full hover:bg-primary/10 transition-all duration-300 flex items-center justify-center p-0 border border-border/50 hover:border-primary/50"
                    aria-label="Upload track"
                  >
                    <Paperclip className="w-5 h-5 md:w-6 md:h-6 text-muted-foreground hover:text-primary transition-colors" />
                  </Button>
                  <Button
                    onClick={handleGenerate}
                    size="lg"
                    className="h-12 md:h-14 w-12 md:w-14 rounded-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center p-0"
                    aria-label="Generate"
                  >
                    <ArrowUp className="w-5 h-5 md:w-6 md:h-6" />
                  </Button>
                </div>
              </div>
            </div>

            {/* PRIMARY CTA */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8 fade-in-up">
              <Button size="lg" className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white text-base px-10 py-3 h-auto rounded-full font-semibold shadow-lg hover:shadow-xl transition-all duration-300" asChild>
                <Link href="/dashboard/create">
                  <Play className="w-4 h-4 mr-2" />
                  Start Creating Free
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-base px-10 py-3 h-auto border-2 border-primary/30 hover:border-primary/50 hover:bg-primary/5 rounded-full font-semibold transition-all duration-300" asChild>
                <Link href="/#features">
                  <Eye className="w-4 h-4 mr-2" />
                  See Examples
                </Link>
              </Button>
            </div>

            {/* TRUST INDICATORS */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto fade-in-up">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">{stat.number}</div>
                  <div className="text-sm text-muted-foreground font-medium">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>


      {/* MEDIA SHOWCASE SECTION */}
      <section className="py-20 section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <Badge className="mb-6 px-4 py-2 text-sm font-medium gradient-primary text-white">
              <Video className="w-4 h-4 mr-2" />
              AI Showcase
            </Badge>
            <h2 className="heading-responsive font-bold mb-6">
              See What Our AI Can <span className="gradient-text-ai">Create</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
              Real music videos and social media content generated by our AI from user audio files. 
              Perfect for TikTok, Instagram, YouTube, and all major platforms.
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center">
                <Check className="w-4 h-4 text-primary mr-2" />
                <span>4K Quality Output</span>
              </div>
              <div className="flex items-center">
                <Check className="w-4 h-4 text-primary mr-2" />
                <span>Auto-Sync to Music</span>
              </div>
              <div className="flex items-center">
                <Check className="w-4 h-4 text-primary mr-2" />
                <span>Multiple Visual Styles</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            <Card className="group relative overflow-hidden bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-xl hover:scale-105">
              <div className="aspect-video bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center relative">
                <video
                  className="w-full h-full object-cover"
                  poster="/api/placeholder/800/450"
                  controls
                  preload="metadata"
                  muted
                  onLoadedMetadata={(e) => {
                    e.currentTarget.currentTime = 5;
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.play();
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.pause();
                    e.currentTarget.currentTime = 5;
                  }}
                  onVolumeChange={(e) => {
                    if (e.currentTarget.volume > 0) {
                      e.currentTarget.muted = false;
                    }
                  }}
                  onError={(e) => {
                    console.error('Video load error:', e);
                    const video = e.target as HTMLVideoElement;
                    video.style.display = 'none';
                    const placeholder = video.nextElementSibling as HTMLElement;
                    if (placeholder) placeholder.style.display = 'flex';
                  }}
                >
                  <source src="/media/thumbnail_1.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                <div className="w-full h-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-2xl font-bold" style={{display: 'none'}}>
                  <div className="text-center">
                    <Play className="w-12 h-12 mx-auto mb-2" />
                    Electronic Dance
                  </div>
                </div>
                
                {/* Overlay Controls */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center">
                  <Button
                    size="lg"
                    variant="secondary"
                    onClick={() => openTheater("/media/thumbnail_1.mp4", "Electronic Dance Track", "AI-generated visuals synced to electronic music")}
                    className="opacity-0 group-hover:opacity-100 transition-all duration-300 bg-white/90 hover:bg-white text-black border-0 shadow-lg"
                  >
                    <Maximize2 className="w-5 h-5 mr-2" />
                    Full Screen
                  </Button>
                </div>

                {/* Genre Badge */}
                <div className="absolute top-3 left-3">
                  <Badge className="bg-purple-500/90 text-white border-0">
                    Electronic
                  </Badge>
                </div>
              </div>
              
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold">Electronic Dance Track</h3>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="w-4 h-4 mr-1" />
                    3:24
                  </div>
                </div>
                <p className="text-muted-foreground mb-4">
                  AI-generated visuals synced to electronic music with dynamic particle effects and color transitions
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Eye className="w-4 h-4 mr-1" />
                      1.2K views
                    </div>
                    <div className="flex items-center">
                      <Heart className="w-4 h-4 mr-1" />
                      89 likes
                    </div>
                  </div>
                  <Button size="sm" variant="outline" asChild>
                    <Link href="/dashboard/create">
                      <Play className="w-4 h-4 mr-1" />
                      Create Similar
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="group relative overflow-hidden bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-xl hover:scale-105">
              <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center relative">
                <video
                  className="w-full h-full object-cover"
                  poster="/api/placeholder/800/450"
                  controls
                  preload="metadata"
                  muted
                  onLoadedMetadata={(e) => {
                    e.currentTarget.currentTime = 5;
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.play();
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.pause();
                    e.currentTarget.currentTime = 5;
                  }}
                  onVolumeChange={(e) => {
                    if (e.currentTarget.volume > 0) {
                      e.currentTarget.muted = false;
                    }
                  }}
                  onError={(e) => {
                    console.error('Video load error:', e);
                    const video = e.target as HTMLVideoElement;
                    video.style.display = 'none';
                    const placeholder = video.nextElementSibling as HTMLElement;
                    if (placeholder) placeholder.style.display = 'flex';
                  }}
                >
                  <source src="/media/thumbnail_2.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                <div className="w-full h-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white text-2xl font-bold" style={{display: 'none'}}>
                  <div className="text-center">
                    <Play className="w-12 h-12 mx-auto mb-2" />
                    Ambient Soundscape
                  </div>
                </div>
                
                {/* Overlay Controls */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center">
                  <Button
                    size="lg"
                    variant="secondary"
                    onClick={() => openTheater("/media/thumbnail_2.mp4", "Ambient Soundscape", "Abstract visuals matching ambient audio")}
                    className="opacity-0 group-hover:opacity-100 transition-all duration-300 bg-white/90 hover:bg-white text-black border-0 shadow-lg"
                  >
                    <Maximize2 className="w-5 h-5 mr-2" />
                    Full Screen
                  </Button>
                </div>

                {/* Genre Badge */}
                <div className="absolute top-3 left-3">
                  <Badge className="bg-blue-500/90 text-white border-0">
                    Ambient
                  </Badge>
                </div>
              </div>
              
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold">Ambient Soundscape</h3>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="w-4 h-4 mr-1" />
                    4:12
                  </div>
                </div>
                <p className="text-muted-foreground mb-4">
                  Abstract visuals matching ambient audio with flowing organic shapes and calming color palettes
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Eye className="w-4 h-4 mr-1" />
                      856 views
                    </div>
                    <div className="flex items-center">
                      <Heart className="w-4 h-4 mr-1" />
                      67 likes
                    </div>
                  </div>
                  <Button size="sm" variant="outline" asChild>
                    <Link href="/dashboard/create">
                      <Play className="w-4 h-4 mr-1" />
                      Create Similar
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="group relative overflow-hidden bg-card border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-xl hover:scale-105">
              <div className="aspect-video bg-gradient-to-br from-green-500/20 to-teal-500/20 flex items-center justify-center relative">
                <video
                  className="w-full h-full object-cover"
                  poster="/api/placeholder/800/450"
                  controls
                  preload="metadata"
                  muted
                  onLoadedMetadata={(e) => {
                    e.currentTarget.currentTime = 5;
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.play();
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.pause();
                    e.currentTarget.currentTime = 5;
                  }}
                  onVolumeChange={(e) => {
                    if (e.currentTarget.volume > 0) {
                      e.currentTarget.muted = false;
                    }
                  }}
                  onError={(e) => {
                    console.error('Video load error:', e);
                    const video = e.target as HTMLVideoElement;
                    video.style.display = 'none';
                    const placeholder = video.nextElementSibling as HTMLElement;
                    if (placeholder) placeholder.style.display = 'flex';
                  }}
                >
                  <source src="/media/thumbnail_3.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                <div className="w-full h-full bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center text-white text-2xl font-bold" style={{display: 'none'}}>
                  <div className="text-center">
                    <Play className="w-12 h-12 mx-auto mb-2" />
                    Rock Anthem
                  </div>
                </div>
                
                {/* Overlay Controls */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center">
                  <Button
                    size="lg"
                    variant="secondary"
                    onClick={() => openTheater("/media/thumbnail_3.mp4", "Rock Anthem", "High-energy visuals for rock music")}
                    className="opacity-0 group-hover:opacity-100 transition-all duration-300 bg-white/90 hover:bg-white text-black border-0 shadow-lg"
                  >
                    <Maximize2 className="w-5 h-5 mr-2" />
                    Full Screen
                  </Button>
                </div>

                {/* Genre Badge */}
                <div className="absolute top-3 left-3">
                  <Badge className="bg-green-500/90 text-white border-0">
                    Rock
                  </Badge>
                </div>
              </div>
              
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold">Rock Anthem</h3>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="w-4 h-4 mr-1" />
                    3:45
                  </div>
                </div>
                <p className="text-muted-foreground mb-4">
                  High-energy visuals for rock music with dynamic lighting effects and powerful visual transitions
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <Eye className="w-4 h-4 mr-1" />
                      2.1K views
                    </div>
                    <div className="flex items-center">
                      <Heart className="w-4 h-4 mr-1" />
                      156 likes
                    </div>
                  </div>
                  <Button size="sm" variant="outline" asChild>
                    <Link href="/dashboard/create">
                      <Play className="w-4 h-4 mr-1" />
                      Create Similar
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Call to Action */}
          <div className="text-center mt-8">
            <div className="max-w-2xl mx-auto">
              <h3 className="text-xl font-bold mb-3">
                Ready to Create Your Own <span className="gradient-text">AI Music Video?</span>
              </h3>
              <p className="text-muted-foreground mb-6">
                Join thousands of creators who are already using VibeWave to generate professional music videos in minutes
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button size="lg" className="btn-gradient text-base px-6 py-3" asChild>
                  <Link href="/dashboard/create">
                    <Play className="w-4 h-4 mr-2" />
                    Start Creating Now
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" className="text-base px-6 py-3" asChild>
                  <Link href="/#features">
                    <Eye className="w-4 h-4 mr-2" />
                    Learn More
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="section-padding  bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10 dark:from-primary/20 dark:via-accent/10 dark:to-primary/20">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-responsive font-bold mb-4">
              Powerful Features for
              <span className="gradient-text"> Content Creators & Social Media Professionals</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to create professional music videos, long-form content, and automated social media posts with AI
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="feature-card group fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
                  <CardHeader>
                    <div className="feature-icon">
                      <Icon className="w-6 h-6" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS SECTION */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-responsive font-bold mb-4">
              How It <span className="gradient-text">Works</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Create professional music videos, social media content, and automated posts in four simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
            {/* Step 1 */}
            <Card className="group relative overflow-hidden bg-card/50 backdrop-blur-sm border border-primary/20 hover:border-primary/40 transition-all duration-500 hover:shadow-xl hover:scale-105 fade-in-up">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardContent className="relative p-8 text-center">
                <div className="relative mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary/20 to-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Music className="w-10 h-10 text-primary" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-primary to-accent rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">1</span>
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-3 text-foreground">Upload Audio or Generate</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Upload your own audio, or generate audio that matches your vision using top-tier AI
                </p>
                <div className="mt-4 flex justify-center">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                </div>
              </CardContent>
            </Card>

            {/* Step 2 */}
            <Card className="group relative overflow-hidden bg-card/50 backdrop-blur-sm border border-accent/20 hover:border-accent/40 transition-all duration-500 hover:shadow-xl hover:scale-105 fade-in-up" style={{ animationDelay: "0.2s" }}>
              <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-primary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardContent className="relative p-8 text-center">
                <div className="relative mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-accent/20 to-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Wand2 className="w-10 h-10 text-accent" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-accent to-primary rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">2</span>
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-3 text-foreground">Customize Style & Settings</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Choose your visual style, mood, settings, or let AI generate a description for you
                </p>
                <div className="mt-4 flex justify-center">
                  <div className="w-2 h-2 bg-accent rounded-full animate-pulse delay-300"></div>
                </div>
              </CardContent>
            </Card>

            {/* Step 3 */}
            <Card className="group relative overflow-hidden bg-card/50 backdrop-blur-sm border border-purple-500/20 hover:border-purple-500/40 transition-all duration-500 hover:shadow-xl hover:scale-105 fade-in-up" style={{ animationDelay: "0.4s" }}>
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardContent className="relative p-8 text-center">
                <div className="relative mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-purple-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Video className="w-10 h-10 text-purple-600" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">3</span>
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-3 text-foreground">Generate Content</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Rest while our AI creates your professional music videos and social media content
                </p>
                <div className="mt-4 flex justify-center">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-500"></div>
                </div>
              </CardContent>
            </Card>

            {/* Step 4 */}
            <Card className="group relative overflow-hidden bg-card/50 backdrop-blur-sm border border-green-500/20 hover:border-green-500/40 transition-all duration-500 hover:shadow-xl hover:scale-105 fade-in-up" style={{ animationDelay: "0.6s" }}>
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 via-transparent to-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <CardContent className="relative p-8 text-center">
                <div className="relative mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-green-500/20 to-green-500/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Share2 className="w-10 h-10 text-green-600" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-green-500 to-teal-500 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">4</span>
                  </div>
                </div>
                <h3 className="text-xl font-bold mb-3 text-foreground">Upload to Social Media</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Effortlessly upload your content to TikTok, Instagram, YouTube, and other platforms
                </p>
                <div className="mt-4 flex justify-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse delay-700"></div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Connection Lines */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 transform -translate-y-1/2 pointer-events-none">
            <div className="max-w-7xl mx-auto px-8">
              <div className="flex justify-between">
                <div className="w-1/4 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
                <div className="w-1/4 h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent"></div>
                <div className="w-1/4 h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
              </div>
            </div>
          </div>

          {/* AUTOMATION HIGHLIGHT SECTION */}
          <div className="mt-20">
            <div className="relative">
              {/* Background Elements */}
              <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-accent/5 to-primary/5 rounded-3xl"></div>
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className="w-32 h-32 bg-gradient-to-r from-primary/20 to-accent/20 rounded-full blur-3xl"></div>
              </div>
              
              <div className="relative bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10 border border-primary/20 rounded-3xl p-8 md:p-12">
                {/* OR Divider */}
                <div className="flex items-center justify-center mb-8">
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
                  <div className="mx-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-primary to-accent rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-lg">OR</span>
                    </div>
                  </div>
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
                </div>

                {/* Automation Content */}
                <div className="text-center max-w-4xl mx-auto">
                  <div className="flex items-center justify-center mb-6">
                    <div className="w-20 h-20 bg-gradient-to-r from-primary to-accent rounded-full flex items-center justify-center mr-4 shadow-lg">
                      <Zap className="w-10 h-10 text-white" />
                    </div>
                    <div className="text-left">
                      <h3 className="text-3xl md:text-4xl font-bold gradient-text mb-2">
                        Automate as a 1-Step Process
                      </h3>
                      <div className="flex items-center">
                        <Badge className="bg-gradient-to-r from-primary to-accent text-white border-0 px-3 py-1">
                          <Sparkles className="w-4 h-4 mr-1" />
                          Set & Forget
                        </Badge>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
                    Set up once and let our AI automatically create and post content to your social media platforms based on your preferences and schedule
                  </p>

                  {/* Automation Features */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                      <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Clock className="w-6 h-6 text-primary" />
                      </div>
                      <h4 className="font-semibold mb-2">Smart Scheduling</h4>
                      <p className="text-sm text-muted-foreground">AI determines optimal posting times for maximum engagement</p>
                    </div>
                    
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                      <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Wand2 className="w-6 h-6 text-accent" />
                      </div>
                      <h4 className="font-semibold mb-2">Auto-Generation</h4>
                      <p className="text-sm text-muted-foreground">Creates fresh content automatically based on your style preferences</p>
                    </div>
                    
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                      <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Share2 className="w-6 h-6 text-green-500" />
                      </div>
                      <h4 className="font-semibold mb-2">Multi-Platform</h4>
                      <p className="text-sm text-muted-foreground">Posts to TikTok, Instagram, YouTube, and more simultaneously</p>
                    </div>
                  </div>

                  {/* CTA Button */}
                  <Button 
                    size="lg" 
                    className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white text-lg px-8 py-4 h-auto rounded-full font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105" 
                    asChild
                  >
                    <Link href="/dashboard/create">
                      <Zap className="w-5 h-5 mr-2" />
                      Start Automation Setup
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TESTIMONIALS SECTION */}
      <section className="section-padding  bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10 dark:from-primary/20 dark:via-accent/10 dark:to-primary/20">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-responsive font-bold mb-4">
              Loved by <span className="gradient-text">Content Creators & Social Media Professionals Worldwide</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              See what our users are saying about VibeWave's AI-powered content creation platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="p-6 fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
                <CardContent className="p-0">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mr-4">
                      <span className="text-primary font-semibold">{testimonial.avatar}</span>
                    </div>
                    <div>
                      <div className="font-semibold">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                    </div>
                  </div>
                  <p className="text-muted-foreground italic">"{testimonial.content}"</p>
                  <div className="flex mt-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING SECTION */}
      <section id="pricing" className="section-padding py-20">
        <div className="container-custom">
          <div className="text-center mb-20">
            <Badge className="mb-6 px-4 py-2 text-sm font-medium gradient-primary text-white">
              <Sparkles className="w-4 h-4 mr-2" />
              Pricing Plans
            </Badge>
            <h2 className="heading-responsive font-bold mb-6">
              Simple, Transparent <span className="gradient-text">Pricing</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
              Choose the plan that fits your creative needs. All plans include our core AI video generation features.
            </p>
            <div className="flex items-center justify-center space-x-8 text-sm text-muted-foreground">
              <div className="flex items-center">
                <Check className="w-4 h-4 text-primary mr-2" />
                <span>No setup fees</span>
              </div>
              <div className="flex items-center">
                <Check className="w-4 h-4 text-primary mr-2" />
                <span>Cancel anytime</span>
              </div>
              <div className="flex items-center">
                <Check className="w-4 h-4 text-primary mr-2" />
                <span>14-day free trial</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {pricingPlans.map((plan, index) => (
              <Card key={index} className={`relative ${plan.popular ? "ring-2 ring-primary scale-105" : ""} transition-all duration-200 hover:shadow-lg`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}
                <CardHeader className="text-center pb-4">
                  <CardTitle className="text-2xl font-bold mb-2">{plan.name}</CardTitle>
                  <div className="mb-4">
                    <span className="text-4xl font-bold gradient-text">{plan.price}</span>
                    <span className="text-muted-foreground text-lg ml-1">{plan.period}</span>
                  </div>
                  <CardDescription className="text-base text-muted-foreground">{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start">
                        <Check className="w-5 h-5 text-primary mr-3 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-muted-foreground leading-relaxed">{feature}</span>
                      </li>
                    ))}
                    {plan.name === "Free Tier" && (
                      <li className="flex items-start">
                        <span className="w-5 h-5 text-red-500 mr-3 flex-shrink-0 mt-0.5 flex items-center justify-center">✕</span>
                        <span className="text-sm text-muted-foreground leading-relaxed">Watermark on exports</span>
                      </li>
                    )}
                  </ul>
                  <Button
                    className={`w-full ${plan.popular ? "btn-gradient" : "hover:bg-primary hover:text-primary-foreground"} transition-all duration-200`}
                    variant={plan.popular ? "default" : "outline"}
                    size="lg"
                    asChild
                  >
                    <Link href="/dashboard/create">
                      {plan.cta}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>


      {/* CTA SECTION */}
      <section className="relative overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10 dark:from-primary/20 dark:via-accent/10 dark:to-primary/20"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background"></div>
        
        {/* Animated Background Elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-primary/10 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-accent/10 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-purple-500/10 rounded-full blur-lg animate-pulse delay-500"></div>
        
        <div className="relative container-custom py-20">
          <div className="text-center max-w-4xl mx-auto">
            {/* Main Heading */}
            <div className="mb-8">
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                Ready to Create Your First
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent block sm:inline">
                  {" "}AI-Powered Content?
                </span>
              </h2>
            </div>
            
            {/* Description */}
            <p className="text-lg sm:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
              Join thousands of content creators and social media professionals who are already using clipizy to
              <span className="text-foreground font-semibold"> scale their content production</span> and
              <span className="text-foreground font-semibold"> automate their social media presence</span>.
            </p>
            
            {/* Stats or Social Proof */}
            <div className="flex flex-wrap justify-center items-center gap-8 mb-12 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>10,000+ Active Creators</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-300"></div>
                <span>1M+ Videos Generated</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-700"></div>
                <span>4.9/5 Rating</span>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button 
                size="lg" 
                className="h-14 px-8 text-lg font-semibold bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105" 
                asChild
              >
                <Link href="/dashboard/create">
                  <Play className="w-6 h-6 mr-3" />
                  Start Creating Now
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="h-14 px-8 text-lg font-semibold border-2 border-primary/20 hover:border-primary/40 hover:bg-primary/5 transition-all duration-300 transform hover:scale-105" 
                asChild
              >
                <Link href="/pricing">
                  <Sparkles className="w-6 h-6 mr-3" />
                  View Pricing
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
            </div>
            
            {/* Trust Indicators */}
            <div className="pt-8 border-t border-border/20">
              <p className="text-sm text-muted-foreground mb-4">Trusted by creators worldwide</p>
              <div className="flex flex-wrap justify-center items-center gap-6 opacity-60">
                <div className="flex items-center gap-2 text-xs">
                  <Shield className="w-4 h-4" />
                  <span>SSL Secured</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <Check className="w-4 h-4" />
                  <span>No Setup Required</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <Clock className="w-4 h-4" />
                  <span>Instant Results</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* COMPREHENSIVE FAQ SECTION */}
      <section className="section-padding py-20">
        <div className="container-custom">
          <div className="text-center mb-10">
            <Badge className="mb-6 px-4 py-2 text-sm font-medium gradient-primary text-white">
              <FileText className="w-4 h-4 mr-2" />
              FAQ
            </Badge>
            <h2 className="heading-responsive font-bold mb-6">
              Frequently Asked <span className="gradient-text">Questions</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Everything you need to know about VibeWave's AI-powered music video and distribution platform
            </p>
          </div>

          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* LEFT COLUMN */}
              <div className="space-y-6">
                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-primary/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Video className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">What exactly can VibeWave create?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        VibeWave generates full-length music videos directly from prompts. You can choose between simple static visuals, looped animations, or full scene-based videos with transitions and intros/outros. Each video is automatically synced to your music.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-accent/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Zap className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">How does the automation pipeline work?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Once you've set up your preferences (music prompts, visual styles, transitions), you can save them as templates. The automation pipeline lets you generate and schedule multiple videos in advance, so new content can be published automatically to YouTube or prepared for distribution services.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-green-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-green-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Check className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">Can I use the generated videos and music commercially?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Yes. All generated content comes with commercial usage rights, meaning you can monetize your music videos on YouTube, distribute audio through services like Spotify, and use the visuals for promotional campaigns.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-blue-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-blue-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <FileText className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">What file formats are supported?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        For music, we support MP3, WAV, and FLAC uploads. Exported videos are delivered in MP4 format, optimized for YouTube and other major platforms.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-purple-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-purple-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Star className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">Is there a free plan?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Yes. New users can generate one static video for free to test the platform. Paid tiers unlock animated and scene-based videos, longer durations, and automation features.
                      </p>
                    </div>
                  </div>
                </Card>
              </div>

              {/* RIGHT COLUMN */}
              <div className="space-y-6">
                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-orange-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-orange-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Clock className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">How long does it take to create a music video?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Simple static or looped videos usually generate in under 5 minutes. Scene-based, long-form videos may take 10–20 minutes depending on complexity. You'll be notified when your video is ready.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-cyan-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-cyan-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Share2 className="w-5 h-5 text-cyan-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">Which platforms can I publish to?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Our first focus is YouTube for long-form music videos. We're also building integrations with music distribution partners so you can send your audio tracks directly to Spotify, Apple Music, and more. Social clips (TikTok, Instagram Reels) will be supported in upcoming updates.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-pink-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-pink-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Wand2 className="w-5 h-5 text-pink-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">Can I save and reuse my settings?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Absolutely. You can save your prompts, styles, and transitions as presets. This lets you quickly create consistent videos for albums, EPs, or recurring content without redoing your setup every time.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-indigo-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-indigo-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Users className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">Do I keep the rights to my music?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        Yes. You always retain full rights to your uploaded music. Any AI-generated visual content is royalty-free and fully yours to use commercially.
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="p-6 hover:shadow-lg transition-all duration-300 border-l-4 border-l-teal-500/50">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-teal-500/10 rounded-full flex items-center justify-center flex-shrink-0">
                      <Download className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-foreground">What payment methods do you support?</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        We accept all major credit cards and PayPal. Payments are processed securely through Stripe. Enterprise plans with invoicing are available on request.
                      </p>
                    </div>
                  </div>
                </Card>
              </div>
            </div>

            {/* CONTACT CTA */}
            <div className="mt-16 text-center">
              <Card className="p-8 bg-gradient-to-r from-primary/5 to-accent/5 border-primary/20">
                <div className="max-w-2xl mx-auto">
                  <h3 className="text-2xl font-bold mb-4">
                    Still have questions?
                  </h3>
                  <p className="text-muted-foreground mb-6">
                    Our support team is here to help you get the most out of VibeWave. Get in touch and we'll respond within 24 hours.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Button variant="outline" asChild>
                      <Link href="/contact">
                        <FileText className="w-4 h-4 mr-2" />
                        Contact Support
                      </Link>
                    </Button>
                    <Button asChild>
                      <Link href="/dashboard/create">
                        <Play className="w-4 h-4 mr-2" />
                        Start Creating
                      </Link>
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* EMAIL SUBSCRIPTION SECTION */}
      <section className="section-padding  bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10 dark:from-primary/20 dark:via-accent/10 dark:to-primary/20">
        <div className="container-custom">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="heading-responsive font-bold mb-4">
              Stay Updated with <span className="gradient-text">Latest Features</span>
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Get notified about new AI features, workflow improvements, and exclusive content creation tips.
            </p>
            <EmailSubscription
              placeholder="Enter your email address"
              buttonText="Subscribe to Updates"
              source="homepage"
              variant="default"
              size="lg"
              className="max-w-md mx-auto"
            />
          </div>
        </div>
      </section>

      {/* VIDEO THEATER MODAL */}
      {theaterVideo && (
        <VideoTheater
          isOpen={!!theaterVideo}
          onClose={closeTheater}
          videoSrc={theaterVideo.src}
          title={theaterVideo.title}
          description={theaterVideo.description}
        />
      )}
    </div>
  );
}
