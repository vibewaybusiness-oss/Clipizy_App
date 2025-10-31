"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Brain,
  Target,
  Users,
  Zap,
  Lightbulb,
  Heart,
  ArrowRight,
  CheckCircle,
  Play,
  Award,
  Globe,
  Shield,
  Sparkles,
  Music
} from "lucide-react";

const values = [
  {
    icon: Brain,
    title: "AI-First Innovation",
    description: "We believe in pushing the boundaries of what's possible with artificial intelligence to democratize creative content creation."
  },
  {
    icon: Heart,
    title: "Creator-Centric",
    description: "Every feature we build is designed with creators in mind, making professional-quality content accessible to everyone."
  },
  {
    icon: Zap,
    title: "Speed & Efficiency",
    description: "We understand that time is precious for creators, so we've optimized our platform for maximum speed and efficiency."
  },
  {
    icon: Globe,
    title: "Global Community",
    description: "We're building a worldwide community of creators who inspire and support each other in their creative journeys."
  }
];


const milestones = [
  {
    year: "2024 Q4",
    title: "Platform Launch",
    description: "Launched VibeWave with advanced AI music analysis and automated content generation workflows"
  },
  {
    year: "2025 Q1",
    title: "Smart Audio Processing",
    description: "Introduced intelligent audio analysis that automatically syncs visuals with music beats and mood"
  },
  {
    year: "2025 Q2",
    title: "Workflow Automation",
    description: "Built comprehensive automation pipelines for social media content creation and distribution"
  },
  {
    year: "2025 Q3",
    title: "Advanced Generation",
    description: "Enhanced AI workflows for long-form content creation with seamless transitions and scene management"
  },
  {
    year: "2025 Q4",
    title: "Enterprise Solutions",
    description: "Launched enterprise-grade workflows for agencies and large content teams with custom automation"
  }
];

const stats = [
  { number: "50K+", label: "Videos Generated" },
  { number: "2K+", label: "Active Creators" },
  { number: "15+", label: "Countries" },
  { number: "99.9%", label: "Uptime" }
];

export default function About() {
  return (
    <div className="min-h-screen">
      {/* HERO SECTION */}
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
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="heading-responsive font-bold mb-8 fade-in-up">
              <span className="gradient-text-ai block">Democratizing Creative Content Creation</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              We empower artists with professional-quality music video creation.
              Bring your musical visions to life without the traditional barriers of time, cost, or technical expertise.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button size="lg" className="btn-gradient text-lg px-8 py-4" asChild>
                <Link href="/dashboard/create">
                  <Play className="w-5 h-5 mr-2" />
                  Try clipizy
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-4" asChild>
                <Link href="/contact">
                  <Heart className="w-5 h-5 mr-2" />
                  Join Our Community
                </Link>
              </Button>
            </div>

            {/* STATS */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-2xl mx-auto">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold gradient-text mb-2">{stat.number}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* MISSION SECTION */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="fade-in-up">
              <h2 className="heading-responsive font-bold mb-6">
                Our <span className="gradient-text">Mission</span>
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                We believe that creativity shouldn't be limited by technical barriers or budget constraints.
                Our mission is to democratize content creation by making professional-quality music video
                production accessible to creators of all levels.
              </p>
              <p className="text-lg text-muted-foreground mb-8">
                Through advanced AI technology, we're breaking down the traditional barriers that have
                prevented many talented creators from bringing their musical visions to life. Whether
                you're an independent artist, content creator, or marketing professional, clipizy
                empowers you to create stunning visuals that match your audio perfectly.
              </p>
              <div className="flex items-center space-x-4">
                <Button className="btn-gradient" asChild>
                  <Link href="/dashboard/create">
                    Start Creating
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/#features">Learn More</Link>
                </Button>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* VALUES SECTION */}
      <section className="section-padding  bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10 dark:from-primary/20 dark:via-accent/10 dark:to-primary/20">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-responsive font-bold mb-4">
              Our <span className="gradient-text">Values</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              The principles that guide everything we do
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => {
              const Icon = value.icon;
              return (
                <Card key={index} className="feature-card fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
                  <CardHeader>
                    <div className="feature-icon">
                      <Icon className="w-6 h-6" />
                    </div>
                    <CardTitle className="text-xl">{value.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {value.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>


      {/* TIMELINE SECTION */}
      <section className="section-padding">
        <div className="container-custom">
          <div className="text-center mb-16">
            <h2 className="heading-responsive font-bold mb-4">
              Our <span className="gradient-text">Journey</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Key milestones in our mission to democratize content creation
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              {milestones.map((milestone, index) => (
                <div key={index} className="flex items-start space-x-6 fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <Badge variant="outline" className="text-primary border-primary">
                        {milestone.year}
                      </Badge>
                      <h3 className="text-xl font-semibold">{milestone.title}</h3>
                    </div>
                    <p className="text-muted-foreground">{milestone.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* TECHNOLOGY SECTION */}
      <section className="section-padding  bg-gradient-to-br from-primary/10 via-accent/5 to-primary/10 dark:from-primary/20 dark:via-accent/10 dark:to-primary/20">
        <div className="container-custom">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="fade-in-up">
              <h2 className="heading-responsive font-bold mb-6">
                Advanced <span className="gradient-text-ai">Music Analysis & Workflows</span>
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Our platform uses sophisticated audio analysis to understand rhythm, mood, and energy patterns,
                then automatically generates perfectly synced visual content through intelligent workflow automation.
              </p>
              <div className="space-y-4 mb-8">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-primary" />
                  <span className="text-muted-foreground">Intelligent audio pattern recognition</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Zap className="w-5 h-5 text-primary" />
                  <span className="text-muted-foreground">Automated content generation workflows</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Award className="w-5 h-5 text-primary" />
                  <span className="text-muted-foreground">Smart social media distribution</span>
                </div>
              </div>
              <Button className="btn-gradient" asChild>
                <Link href="/dashboard/create">
                  Experience the Technology
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
            </div>

            <div className="fade-in-up" style={{ animationDelay: "0.2s" }}>
              <div className="relative">
                <div className="aspect-square bg-gradient-to-br from-primary/10 to-accent/10 rounded-2xl flex items-center justify-center">
                  <div className="text-center">
                    <Music className="w-24 h-24 text-primary mx-auto mb-4" />
                    <p className="text-lg font-medium">Smart Analysis</p>
                    <p className="text-sm text-muted-foreground">Audio Workflows</p>
                  </div>
                </div>
                <div className="absolute -bottom-4 -left-4 w-16 h-16 bg-accent/20 rounded-full flex items-center justify-center">
                  <Zap className="w-8 h-8 text-accent" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="section-padding">
        <div className="container-custom text-center">
          <h2 className="heading-responsive font-bold mb-4 text-gray-900 dark:text-white">
            Ready to Join Our
            <span className="block gradient-text">Creative Revolution?</span>
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto text-gray-600 dark:text-gray-300">
            Be part of the future of content creation. Start creating amazing music videos today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="btn-gradient text-lg px-8 py-4" asChild>
              <Link href="/dashboard/create">
                <Play className="w-5 h-5 mr-2" />
                Start Creating
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-4" asChild>
              <Link href="/contact">
                <Heart className="w-5 h-5 mr-2" />
                Get in Touch
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
