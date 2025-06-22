"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useTheme } from "@/hooks/useTheme";

export default function CompletePage() {
  const router = useRouter();
  useTheme(); // Initialize dark mode

  return (
    <div className="min-h-screen bg-gradient-custom flex flex-col">
      <Header />

      {/* Main Content */}
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-card-custom rounded-2xl shadow-lg p-8 max-w-2xl mx-auto text-center">
          {/* Success Icon */}
          <div className="mx-auto w-20 h-20 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center mb-6">
            <svg
              className="w-10 h-10 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* Success Message */}
          <h2 className="text-3xl font-bold text-foreground-custom mb-4">
            Form Completed Successfully!
          </h2>
          <p className="text-lg text-secondary-custom mb-8">
            Congratulations! You have successfully filled out all the required
            fields in your immigration form. Your information has been saved and
            is ready for review.
          </p>

          {/* Form Summary */}
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-6 mb-8 text-left">
            <h3 className="text-lg font-semibold text-foreground-custom mb-4">
              Form Summary
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-secondary-custom">Fields Completed:</span>
                <span className="text-foreground-custom font-medium">
                  3 of 3
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-custom">Completion Rate:</span>
                <span className="text-green-600 font-medium">100%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-secondary-custom">Form Type:</span>
                <span className="text-foreground-custom font-medium">
                  Sample Form
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => router.push("/")}
              className="px-6 py-3 border border-custom rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-foreground-custom"
            >
              Fill Another Form
            </button>
            <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors font-medium">
              Download Completed Form
            </button>
          </div>
        </div>

        {/* Additional Help */}
        <div className="text-center mt-8">
          <p className="text-sm text-secondary-custom">
            Need help with your completed form? Contact our support team for
            assistance.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
