import type { Metadata } from 'next';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Eye, Database, Lock, Users, Globe } from "lucide-react";

export const metadata: Metadata = {
  title: 'Privacy Policy - clipizy',
  description: 'Privacy Policy for clipizy AI-powered music video creation platform',
  robots: {
    index: true,
    follow: true,
  },
};

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container-custom py-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Badge className="mb-4 px-4 py-2 text-sm font-medium gradient-primary text-white">
              <Shield className="w-4 h-4 mr-2" />
              Privacy Policy
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Privacy <span className="gradient-text">Policy</span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>

          <div className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2 text-primary" />
                  1. INFORMATION WE COLLECT
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-semibold text-lg">1.1 Personal Information</h3>
                <p>We collect information you provide directly to us, including:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Account details (name, email address, password)</li>
                  <li>Profile preferences and settings</li>
                  <li>Payment and billing information</li>
                  <li>Communication preferences</li>
                  <li>Support requests and feedback</li>
                </ul>

                <h3 className="font-semibold text-lg">1.2 Content and Media</h3>
                <p>When using the Service, we process and store:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Audio files uploaded for video generation</li>
                  <li>Images, graphics, and visual assets you provide</li>
                  <li>Videos and other content generated through clipizy</li>
                  <li>Project settings and customization details</li>
                  <li>Social media content and associated metadata</li>
                </ul>

                <h3 className="font-semibold text-lg">1.3 Usage Information</h3>
                <p>We automatically collect technical and usage data, such as:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Device details (IP address, browser type, operating system)</li>
                  <li>Session activity, feature usage, and interaction logs</li>
                  <li>Performance metrics and error reports</li>
                  <li>Referral sources and marketing attribution</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Globe className="w-5 h-5 mr-2 text-primary" />
                  2. HOW WE USE YOUR INFORMATION
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-semibold text-lg">2.1 Service Provision</h3>
                <p>We use your information to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Deliver and maintain our video generation tools</li>
                  <li>Process media files and generate content</li>
                  <li>Manage subscriptions and billing</li>
                  <li>Provide customer support and resolve issues</li>
                </ul>

                <h3 className="font-semibold text-lg">2.2 Platform Improvement</h3>
                <p>We analyze aggregated and anonymized data to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Enhance our AI models and generation quality</li>
                  <li>Develop new features and services</li>
                  <li>Improve overall performance and reliability</li>
                </ul>

                <h3 className="font-semibold text-lg">2.3 Communication</h3>
                <p>We may use your information to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Send service-related updates and notifications</li>
                  <li>Provide marketing communications (only with your consent)</li>
                  <li>Respond to inquiries and support requests</li>
                  <li>Deliver important security or policy updates</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lock className="w-5 h-5 mr-2 text-primary" />
                  3. DATA SECURITY AND PROTECTION
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-semibold text-lg">3.1 Security Measures</h3>
                <p>We implement robust measures including:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>End-to-end encryption for data in transit</li>
                  <li>Secure cloud storage with role-based access controls</li>
                  <li>Regular audits and vulnerability testing</li>
                  <li>Employee training in data protection practices</li>
                  <li>Incident response and breach notification procedures</li>
                </ul>

                <h3 className="font-semibold text-lg">3.2 Data Retention</h3>
                <p>
                  We retain your personal data only as long as necessary to provide the Service and comply with legal obligations. You may request deletion of your account and associated data at any time.
                </p>

                <h3 className="font-semibold text-lg">3.3 Data Minimization</h3>
                <p>
                  We collect only the information required to operate and improve the Service. We routinely review and purge unnecessary data.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2 text-primary" />
                  4. INFORMATION SHARING AND DISCLOSURE
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p><strong>No Sale of Data:</strong> We do not sell, trade, or rent your personal information.</p>

                <p><strong>Limited Sharing:</strong> We may share information only:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>With your explicit consent</li>
                  <li>To comply with legal obligations or court orders</li>
                  <li>To protect our rights, property, or safety</li>
                  <li>With trusted service providers bound by confidentiality and security requirements</li>
                  <li>In connection with mergers, acquisitions, or business transfers</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>5. YOUR RIGHTS AND CHOICES</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>You have the right to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Access and review your personal information</li>
                  <li>Correct inaccuracies or update your data</li>
                  <li>Request deletion of your account and personal data</li>
                  <li>Export your data in a portable format</li>
                  <li>Opt out of marketing communications</li>
                  <li>Withdraw consent for processing (where applicable)</li>
                </ul>
                <p>
                  You can manage many preferences directly through your account settings. For other requests, contact us at privacy@clipizy.ai. We respond within 30 days.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>6. COOKIES AND TRACKING</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <h3 className="font-semibold text-lg">6.1 How We Use Cookies</h3>
                <p>We use cookies and similar technologies to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Maintain login sessions and user preferences</li>
                  <li>Analyze usage and improve performance</li>
                  <li>Personalize recommendations and features</li>
                </ul>

                <h3 className="font-semibold text-lg">6.2 Managing Cookies</h3>
                <p>
                  You may adjust cookie settings in your browser. Disabling cookies may limit certain features of the Service.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>7. INTERNATIONAL DATA TRANSFERS</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  Your data may be processed in countries outside your residence. Where required, we implement safeguards such as standard contractual clauses or adequacy decisions to protect your information.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>8. DISCLAIMER ON GENERATED CONTENT</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  clipizy provides automated tools for generating multimedia content. We do not monitor or review user input or AI-generated outputs before delivery. You are solely responsible for the legality, accuracy, and appropriateness of any content created, uploaded, or distributed using clipizy.
                </p>
                <p>
                  clipizy disclaims all liability arising from user-generated or AI-generated content, including but not limited to intellectual property infringement, offensive or unlawful material, and misuse of the Service.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>9. CHANGES TO THIS PRIVACY POLICY</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p>
                  We may update this Policy to reflect changes in our practices or applicable laws. We will notify users of material changes via email or in-app notifications. Continued use of the Service constitutes acceptance of the updated Policy.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>10. REGULATORY COMPLIANCE</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p><strong>GDPR (EU):</strong> We comply with the General Data Protection Regulation, including lawful basis for processing, data subject rights, and Data Protection Impact Assessments where required.</p>
                <p><strong>CCPA (California):</strong> We comply with the California Consumer Privacy Act, including rights to know, delete, and opt out of personal data sale (though we do not sell personal data).</p>
                <p><strong>Other Jurisdictions:</strong> We strive to meet applicable privacy laws in all regions where we operate.</p>
              </CardContent>
            </Card>

          </div>
        </div>
      </div>
    </div>
  );
}
