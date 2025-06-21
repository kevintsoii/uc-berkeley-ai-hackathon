"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { useTheme } from "@/hooks/useTheme";

export default function Home() {
  const router = useRouter();
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [dragActive, setDragActive] = useState(false);
  useTheme(); // Initialize dark mode

  const languages = [
    { code: "en", name: "English", native: "English" },
    { code: "es", name: "Spanish", native: "Español" },
    { code: "zh", name: "Chinese", native: "中文" },
    { code: "hi", name: "Hindi", native: "हिन्दी" },
    { code: "ar", name: "Arabic", native: "العربية" },
    { code: "pt", name: "Portuguese", native: "Português" },
    { code: "ru", name: "Russian", native: "Русский" },
    { code: "fr", name: "French", native: "Français" },
    { code: "de", name: "German", native: "Deutsch" },
    { code: "ja", name: "Japanese", native: "日本語" },
  ];

  const sampleForms = [
    {
      id: 1,
      title: "Form I-485",
      description: "Application to Register Permanent Residence",
      difficulty: "Advanced",
      estimatedTime: "45-60 min",
    },
    {
      id: 2,
      title: "Form N-400",
      description: "Application for Naturalization",
      difficulty: "Intermediate",
      estimatedTime: "30-45 min",
    },
    {
      id: 3,
      title: "Form I-130",
      description: "Petition for Alien Relative",
      difficulty: "Beginner",
      estimatedTime: "20-30 min",
    },
    {
      id: 4,
      title: "Form I-765",
      description: "Application for Employment Authorization",
      difficulty: "Intermediate",
      estimatedTime: "25-35 min",
    },
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      // Handle file upload here
      console.log("File uploaded:", files[0]);
      // Navigate to first fill page
      router.push("/fill/1");
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      // Handle file upload here
      console.log("File uploaded:", files[0]);
      // Navigate to first fill page
      router.push("/fill/1");
    }
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      Beginner: "bg-green-900/50 text-green-300",
      Intermediate: "bg-yellow-900/50 text-yellow-300",
      Advanced: "bg-red-900/50 text-red-300",
    };
    return colors[difficulty] || "bg-gray-900/50 text-gray-300";
  };

  return (
    <div className="min-h-screen bg-gradient-custom">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-6xl font-bold text-foreground-custom mb-6 leading-tight">
            Fill Immigration Forms
            <span className="text-blue-600"> with Confidence</span>
          </h2>
          <p className="text-xl md:text-2xl text-secondary-custom mb-8 max-w-4xl mx-auto leading-relaxed">
            Get AI-powered assistance to complete your immigration forms
            step-by-step. Upload your PDF, choose your language, and let our
            voice assistant guide you through every question.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm text-secondary-custom">
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              10+ Languages Supported
            </div>
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Voice Assistance
            </div>
            <div className="flex items-center">
              <svg
                className="w-5 h-5 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Secure & Private
            </div>
          </div>
        </div>

        {/* Language Selection */}
        <div className="mb-12">
          <div className="bg-card-custom rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-semibold text-foreground-custom mb-6 text-center">
              Choose Your Language
            </h3>
            <div className="relative">
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="language-select w-full px-4 py-4 text-lg border-custom rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.native} ({lang.name})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* PDF Upload Section */}
        <div className="mb-16">
          <div className="bg-card-custom rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-semibold text-foreground-custom mb-6 text-center">
              Upload Your Form
            </h3>

            <div
              className={`upload-area border-2 border-dashed rounded-xl p-12 text-center transition-all duration-200 ${
                dragActive
                  ? "border-blue-500 bg-blue-900/20"
                  : "hover:border-blue-400"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileInput}
                className="hidden"
                id="pdf-upload"
              />
              <label htmlFor="pdf-upload" className="cursor-pointer">
                <div className="mx-auto w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center mb-4">
                  <svg
                    className="w-8 h-8 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </div>
                <h4 className="text-xl font-semibold text-foreground-custom mb-2">
                  Drop your PDF here or click to browse
                </h4>
                <p className="text-secondary-custom mb-4">
                  Supports PDF files up to 10MB
                </p>
                <div className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                  Choose File
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Sample Forms */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-foreground-custom mb-4">
              Or Choose from Common Forms
            </h3>
            <p className="text-lg text-secondary-custom max-w-2xl mx-auto">
              Start with one of these popular immigration forms. Each comes with
              guided assistance and voice support.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {sampleForms.map((form) => (
              <div
                key={form.id}
                className="form-card rounded-xl p-6 transition-all duration-200 cursor-pointer"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h4 className="text-xl font-semibold text-foreground-custom mb-2">
                      {form.title}
                    </h4>
                    <p className="text-secondary-custom text-sm leading-relaxed">
                      {form.description}
                    </p>
                  </div>
                  <div className="flex flex-col items-end space-y-2">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(
                        form.difficulty
                      )}`}
                    >
                      {form.difficulty}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-4 border-t border-custom">
                  <div className="flex items-center text-sm text-secondary-custom">
                    <svg
                      className="w-4 h-4 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {form.estimatedTime}
                  </div>
                  <button
                    onClick={() => router.push("/fill/1")}
                    className="text-blue-600 hover:text-blue-700 font-medium text-sm transition-colors"
                  >
                    Start Form →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features Section */}
        <div className="bg-card-custom rounded-2xl shadow-lg p-8 mb-16">
          <h3 className="text-2xl font-bold text-foreground-custom mb-8 text-center">
            How FormBridge Helps You
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-foreground-custom mb-2">
                Voice Assistance
              </h4>
              <p className="text-secondary-custom">
                Get audio explanations for complex questions in your preferred
                language
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-green-600"
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
              <h4 className="text-lg font-semibold text-foreground-custom mb-2">
                Step-by-Step Guidance
              </h4>
              <p className="text-secondary-custom">
                Complete forms one section at a time with clear instructions
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                  />
                </svg>
              </div>
              <h4 className="text-lg font-semibold text-foreground-custom mb-2">
                Multilingual Support
              </h4>
              <p className="text-secondary-custom">
                Available in 10+ languages with native speaker support
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
