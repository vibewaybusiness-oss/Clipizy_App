"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, ArrowRight, Star, Zap } from "lucide-react";
import Link from "next/link";
import { useToast } from "@/hooks/ui/use-toast";

export default function PaymentSuccessPage() {
  const [planName, setPlanName] = useState<string>('Creator Plan');
  const [customerEmail, setCustomerEmail] = useState<string>('');

  useEffect(() => {
    // Get plan from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const plan = urlParams.get('plan');
    const email = urlParams.get('email');
    
    if (plan) {
      setPlanName(plan === 'creator' ? 'Creator Plan' : 'Pro Plan');
    }
    
    if (email) {
      setCustomerEmail(email);
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-100">
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="text-center mb-12">
          <div className="mx-auto w-24 h-24 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mb-6 shadow-lg">
            <CheckCircle className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
            Payment Successful!
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Thank you for subscribing to <span className="font-semibold text-green-600">{planName}</span>. 
            Your subscription is now active and you can start creating amazing content!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-2xl">
                <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
                  <Star className="w-6 h-6 text-white" />
                </div>
                Welcome to {planName}
              </CardTitle>
              <CardDescription className="text-lg">
                Your subscription is now active and you can start using all the premium features.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-4 p-3 bg-green-50 rounded-lg">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  </div>
                  <span className="font-medium">Subscription activated successfully</span>
                </div>
                <div className="flex items-center gap-4 p-3 bg-blue-50 rounded-lg">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-blue-600" />
                  </div>
                  <span className="font-medium">Credits added to your account</span>
                </div>
                <div className="flex items-center gap-4 p-3 bg-purple-50 rounded-lg">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 text-purple-600" />
                  </div>
                  <span className="font-medium">Premium features unlocked</span>
                </div>
                {customerEmail && (
                  <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-gray-600" />
                    </div>
                    <span className="font-medium">Confirmation email sent to {customerEmail}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-2xl">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                What's Next?
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-lg text-gray-600 mb-6">
                  Now that you have an active subscription, you can:
                </p>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <ArrowRight className="w-5 h-5 text-blue-600" />
                    </div>
                    <span className="font-medium text-gray-800">Create high-quality videos with premium templates</span>
                  </div>
                  <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-100">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <ArrowRight className="w-5 h-5 text-green-600" />
                    </div>
                    <span className="font-medium text-gray-800">Access priority processing for faster generation</span>
                  </div>
                  <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-purple-50 to-violet-50 rounded-xl border border-purple-100">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <ArrowRight className="w-5 h-5 text-purple-600" />
                    </div>
                    <span className="font-medium text-gray-800">Generate videos without watermarks</span>
                  </div>
                  <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-xl border border-orange-100">
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                      <ArrowRight className="w-5 h-5 text-orange-600" />
                    </div>
                    <span className="font-medium text-gray-800">Get priority customer support</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
          <Link href="/dashboard/create">
            <Button className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-4 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200">
              <Zap className="w-5 h-5 mr-3" />
              Start Creating
            </Button>
          </Link>
          <Link href="/dashboard/settings?tab=subscription">
            <Button variant="outline" className="w-full sm:w-auto border-2 border-gray-300 hover:border-gray-400 px-8 py-4 text-lg font-semibold">
              Manage Subscription
            </Button>
          </Link>
        </div>

        <div className="text-center">
          <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-lg">
            <p className="text-lg text-gray-600 mb-4">
              If you have any questions, please contact our support team
            </p>
            <a href="mailto:support@clipizy.com" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold text-lg transition-colors">
              <span>support@clipizy.com</span>
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
