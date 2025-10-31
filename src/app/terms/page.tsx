import type { Metadata } from 'next';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, FileText, Users, AlertTriangle } from "lucide-react";

export const metadata: Metadata = {
  title: 'Terms of Service - clipizy',
  description: 'Terms of Service for clipizy AI-powered music video creation platform',
  robots: {
    index: true,
    follow: true,
  },
};

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container-custom py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="mb-4 px-4 py-2 text-sm font-medium gradient-primary text-white">
              <FileText className="w-4 h-4 mr-2" />
              Legal Document
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              clipizy Terms of <span className="gradient-text">Service</span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Effective Date: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          <div className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-primary" />
                  INTRODUCTION
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  These Terms of Service ("Terms") govern your access to and use of clipizy ("the Service"), an AI-powered multimedia creation platform. By using the Service, you agree to these Terms. If you do not agree, you must discontinue use immediately.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-primary" />
                  1. ACCEPTANCE OF TERMS
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  By accessing or using clipizy, you acknowledge that you have read, understood, and agree to be bound by these Terms and our Privacy Policy (incorporated herein by reference). If you are using the Service on behalf of an organization, you represent that you have the authority to bind that organization to these Terms.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2 text-primary" />
                  2. DESCRIPTION OF SERVICE
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  clipizy provides AI-powered tools that allow users to generate, edit, and distribute multimedia content. Core features include:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>AI-generated music videos from audio files</li>
                  <li>Social media content creation and optimization</li>
                  <li>Media asset library and management tools</li>
                  <li>Collaborative editing and sharing functionality</li>
                  <li>Export and distribution features</li>
                  <li>API access for third-party integrations</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-primary" />
                  3. USER RESPONSIBILITIES
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-semibold text-lg">3.1 Content Guidelines</h3>
                <p>You agree not to use the Service to create, upload, or distribute content that:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Violates any applicable law or regulation</li>
                  <li>Infringes intellectual property or proprietary rights</li>
                  <li>Contains harmful, abusive, or unlawful material</li>
                  <li>Promotes violence, discrimination, or illegal activities</li>
                  <li>Contains malware, viruses, or malicious code</li>
                  <li>Violates privacy rights or distributes personal data without consent</li>
                </ul>

                <h3 className="font-semibold text-lg">3.2 Account Security</h3>
                <p>You are solely responsible for:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Maintaining the confidentiality of your account credentials</li>
                  <li>All activity conducted under your account</li>
                  <li>Immediately notifying clipizy of any unauthorized access</li>
                  <li>Ensuring your content complies with these Terms</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>4. INTELLECTUAL PROPERTY RIGHTS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-semibold text-lg">4.1 User Content</h3>
                <p>
                  You retain full ownership of all content you upload to clipizy, including audio, video, images, and other media. By submitting content, you grant clipizy a limited, non-exclusive license to store, process, and use such content solely for the purpose of operating and improving the Service.
                </p>

                <h3 className="font-semibold text-lg">4.2 AI-Generated Content</h3>
                <p>
                  Content generated by clipizy's AI tools using your input materials belongs to you. You may use such generated content for commercial or non-commercial purposes in accordance with your subscription plan. clipizy does not claim copyright ownership of user-generated outputs.
                </p>
                <p>
                  By using the Service, you grant clipizy a limited license to store and process generated content for service delivery, and (with your consent) to showcase examples for marketing or research purposes.
                </p>

                <h3 className="font-semibold text-lg">4.3 clipizy Platform</h3>
                <p>
                  All rights, title, and interest in and to clipizy's software, algorithms, models, media libraries, templates, trademarks, and related technology remain the exclusive property of clipizy. Your use of the Service does not transfer any ownership rights.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>5. PRIVACY AND DATA PROTECTION</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  Your privacy is important to us. Our practices for collecting, using, and protecting your personal data are outlined in our Privacy Policy. While clipizy uses industry-standard security practices, you acknowledge that no system is completely secure and use the Service at your own risk.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>6. SUBSCRIPTION AND PAYMENT TERMS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p><strong>Billing:</strong> Subscription fees are billed in advance on a monthly or annual basis. All payments are non-refundable except as required by law or expressly provided in our refund policy.</p>
                <p><strong>Usage Limits:</strong> Each plan includes specific limits (e.g., number of video generations per month). Exceeding these limits may result in additional charges or service restrictions.</p>
                <p><strong>Cancellation:</strong> You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>7. DISCLAIMERS AND LIMITATIONS OF LIABILITY</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p><strong>Service Availability:</strong> clipizy strives for high availability but provides the Service on an "as is" and "as available" basis, without warranties of any kind.</p>
                <p><strong>AI-Generated Content:</strong> clipizy does not guarantee the accuracy, appropriateness, or commercial suitability of AI-generated content. You are solely responsible for reviewing and approving content before use.</p>

                <h3 className="font-semibold text-lg">Disclaimer on Generated Content</h3>
                <p>
                  clipizy provides automated tools for generating multimedia content. We do not monitor, edit, or review user input or AI-generated outputs before delivery. You are solely responsible for the legality, accuracy, and appropriateness of any content created, uploaded, or distributed using the Service.
                </p>
                <p>
                  clipizy disclaims all liability for user-generated or AI-generated content, including but not limited to intellectual property infringement, offensive or unlawful material, and any misuse of the Service.
                </p>

                <p><strong>Limitation of Liability:</strong> To the fullest extent permitted by law, clipizy shall not be liable for any indirect, incidental, or consequential damages arising from use of the Service.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>8. TERMINATION</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  clipizy may suspend or terminate your account immediately if you violate these Terms or engage in harmful conduct. Upon termination, your right to use the Service ends immediately, and clipizy may delete your data. Where feasible, we will provide reasonable notice.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>9. GOVERNING LAW AND DISPUTE RESOLUTION</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  These Terms are governed by the laws of [Insert Jurisdiction]. Any dispute shall be resolved through binding arbitration, except either party may seek injunctive relief in court for urgent matters.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>10. CHANGES TO TERMS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  clipizy reserves the right to update or modify these Terms at any time. Material changes will be communicated via email or within the Service. Continued use of clipizy after changes constitutes acceptance.
                </p>
              </CardContent>
            </Card>

          </div>
        </div>
      </div>
    </div>
  );
}
