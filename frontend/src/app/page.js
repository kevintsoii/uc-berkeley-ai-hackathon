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
  const [uploading, setUploading] = useState(false);
  useTheme(); // Initialize dark mode

  const languages = [
    { code: "ar", name: "Arabic", native: "العربية" },
    { code: "bg", name: "Bulgarian", native: "Български" },
    { code: "bn", name: "Bengali", native: "বাংলা" },
    { code: "zh", name: "Chinese", native: "中文" },
    { code: "hr", name: "Croatian", native: "Hrvatski" },
    { code: "cs", name: "Czech", native: "Čeština" },
    { code: "da", name: "Danish", native: "Dansk" },
    { code: "nl", name: "Dutch", native: "Nederlands" },
    { code: "en", name: "English", native: "English" },
    { code: "et", name: "Estonian", native: "Eesti" },
    { code: "fi", name: "Finnish", native: "Suomi" },
    { code: "fr", name: "French", native: "Français" },
    { code: "de", name: "German", native: "Deutsch" },
    { code: "el", name: "Greek", native: "Ελληνικά" },
    { code: "he", name: "Hebrew", native: "עברית" },
    { code: "hi", name: "Hindi", native: "हिन्दी" },
    { code: "hu", name: "Hungarian", native: "Magyar" },
    { code: "id", name: "Indonesian", native: "Bahasa Indonesia" },
    { code: "it", name: "Italian", native: "Italiano" },
    { code: "ja", name: "Japanese", native: "日本語" },
    { code: "ko", name: "Korean", native: "한국어" },
    { code: "lv", name: "Latvian", native: "Latviešu" },
    { code: "lt", name: "Lithuanian", native: "Lietuvių" },
    { code: "ms", name: "Malay", native: "Bahasa Melayu" },
    { code: "no", name: "Norwegian", native: "Norsk" },
    { code: "pl", name: "Polish", native: "Polski" },
    { code: "pt", name: "Portuguese", native: "Português" },
    { code: "ro", name: "Romanian", native: "Română" },
    { code: "ru", name: "Russian", native: "Русский" },
    { code: "sr", name: "Serbian", native: "Српски" },
    { code: "sk", name: "Slovak", native: "Slovenčina" },
    { code: "sl", name: "Slovenian", native: "Slovenščina" },
    { code: "es", name: "Spanish", native: "Español" },
    { code: "sw", name: "Swahili", native: "Kiswahili" },
    { code: "sv", name: "Swedish", native: "Svenska" },
    { code: "th", name: "Thai", native: "ไทย" },
    { code: "tr", name: "Turkish", native: "Türkçe" },
    { code: "uk", name: "Ukrainian", native: "Українська" },
    { code: "vi", name: "Vietnamese", native: "Tiếng Việt" },
  ];

  const formCategories = [
    {
      id: 1,
      title: "Family-Based Immigrants",
      description:
        "Forms for family members of U.S. citizens and permanent residents",
      forms: [
        {
          id: 1,
          title: "Form I-130",
          description: "Petition for Alien Relative",
          difficulty: "Beginner",
          estimatedTime: "30-45 min",
          fileName: "I-130.pdf",
        },
        {
          id: 2,
          title: "Form I-485",
          description: "Application to Adjust Status to Permanent Resident",
          difficulty: "Intermediate",
          estimatedTime: "45-60 min",
          fileName: "I-485.pdf",
        },
      ],
    },
    {
      id: 2,
      title: "Employment-Based Immigrants",
      description: "Forms for employment-based immigration applications",
      forms: [
        {
          id: 3,
          title: "Form I-140",
          description: "Immigrant Petition for Alien Workers",
          difficulty: "Advanced",
          estimatedTime: "60-90 min",
          fileName: "I-140.pdf",
        },
        {
          id: 4,
          title: "PERM Labor Certification",
          description: "Application for Permanent Employment Certification",
          difficulty: "Advanced",
          estimatedTime: "90-120 min",
          fileName: "PERM.pdf",
        },
        {
          id: 5,
          title: "Form I-485",
          description: "Application to Adjust Status to Permanent Resident",
          difficulty: "Intermediate",
          estimatedTime: "45-60 min",
          fileName: "I-485.pdf",
        },
      ],
    },
    {
      id: 3,
      title: "Refugees / Asylees",
      description: "Forms for asylum seekers and refugees",
      forms: [
        {
          id: 6,
          title: "Form I-589",
          description: "Application for Asylum and for Withholding of Removal",
          difficulty: "Advanced",
          estimatedTime: "90-120 min",
          fileName: "I-589.pdf",
        },
        {
          id: 7,
          title: "Form I-485",
          description: "Application to Adjust Status to Permanent Resident",
          difficulty: "Intermediate",
          estimatedTime: "45-60 min",
          fileName: "I-485.pdf",
        },
      ],
    },
    {
      id: 4,
      title: "Students",
      description: "Forms and documents for international students",
      isSpecial: true,
      specialDescription:
        "Upload your I-20 form from your school to get started",
    },
  ];

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  const updateLanguageOnBackend = async (newLanguage) => {
    try {
      const response = await fetch(`${API_BASE_URL}/update-language`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: newLanguage,
        }),
      });

      if (response.ok) {
        console.log(`Language updated to ${newLanguage}`);
      } else {
        console.error("Failed to update language on backend");
      }
    } catch (error) {
      console.error("Error updating language:", error);
    }
  };

  const handleLanguageChange = (newLanguage) => {
    setSelectedLanguage(newLanguage);
    updateLanguageOnBackend(newLanguage);
  };

  const handleDefaultFormClick = async (form) => {
    try {
      const response = await fetch(`${API_BASE_URL}/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: selectedLanguage,
          default_form: true,
          file_name: form.fileName,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        // Navigate to fill page with session or result data
        router.push("/fill/1");
      } else {
        console.error("Failed to process default form");
      }
    } catch (error) {
      console.error("Error processing default form:", error);
    }
  };

  const handleCustomFileUpload = async (file) => {
    setUploading(true);

    try {
      // First, upload the file
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error("Upload failed");
      }

      const uploadResult = await uploadResponse.json();

      // Then process the uploaded file
      const processResponse = await fetch(`${API_BASE_URL}/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: selectedLanguage,
          default_form: false,
          file_name: uploadResult.file_name || file.name,
        }),
      });

      if (processResponse.ok) {
        const processResult = await processResponse.json();
        // Navigate to fill page with session or result data
        router.push("/fill/1");
      } else {
        throw new Error("Processing failed");
      }
    } catch (error) {
      console.error("Error uploading/processing file:", error);
      alert("Failed to upload or process file. Please try again.");
    } finally {
      setUploading(false);
    }
  };

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
      handleCustomFileUpload(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleCustomFileUpload(files[0]);
    }
    // Clear the input value to allow re-uploading the same file
    e.target.value = "";
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
              30+ Languages Supported
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
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="language-select w-full px-4 py-4 text-lg border-custom rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent border-2"
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
              className={`upload-area border-2 border-dashed border-blue-500 rounded-xl p-12 text-center transition-all duration-200   ${
                dragActive ? "bg-blue-900/20" : "hover:border-blue-400"
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
                disabled={uploading}
              />
              <label
                htmlFor="pdf-upload"
                className={uploading ? "cursor-not-allowed" : "cursor-pointer"}
              >
                <div className="mx-auto w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center mb-4">
                  {uploading ? (
                    <svg
                      className="w-8 h-8 text-blue-600 animate-spin"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                  ) : (
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
                  )}
                </div>
                <h4 className="text-xl font-semibold text-foreground-custom mb-2">
                  {uploading
                    ? "Uploading..."
                    : "Drop your PDF here or click to browse"}
                </h4>
                <p className="text-secondary-custom mb-4">
                  Supports PDF files up to 10MB
                </p>
                <div
                  className={`inline-flex items-center px-6 py-3 ${
                    uploading ? "bg-gray-600" : "bg-blue-600 hover:bg-blue-700"
                  } text-white rounded-lg transition-colors`}
                >
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
                  {uploading ? "Uploading..." : "Choose File"}
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Form Categories */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-foreground-custom mb-4 mt-40">
              Or Choose from Common Form Categories
            </h3>
            <p className="text-lg text-secondary-custom max-w-2xl mx-auto">
              Select your immigration category to find the right forms. Each
              comes with guided assistance and voice support.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
            {formCategories.map((category) => (
              <div
                key={category.id}
                className="bg-card-custom rounded-2xl shadow-lg p-6"
              >
                <div className="text-center mb-6">
                  <h4 className="text-xl font-bold text-foreground-custom mb-2">
                    {category.title}
                  </h4>
                  <p className="text-secondary-custom text-sm">
                    {category.description}
                  </p>
                </div>

                {category.isSpecial ? (
                  // Special Students section - direct to upload
                  <div className="text-center">
                    <div className="bg-blue-900/20 border-2 border-dashed border-blue-500 rounded-xl p-8 max-w-md mx-auto">
                      <div className="w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg
                          className="w-8 h-8 text-blue-400"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                          />
                        </svg>
                      </div>
                      <h5 className="text-lg font-semibold text-foreground-custom mb-2">
                        I-20 Document
                      </h5>
                      <p className="text-secondary-custom mb-4 text-sm">
                        {category.specialDescription}
                      </p>
                      <button
                        onClick={() =>
                          document.getElementById("pdf-upload").click()
                        }
                        disabled={uploading}
                        className={`inline-flex items-center px-6 py-3 ${
                          uploading
                            ? "bg-gray-600"
                            : "bg-blue-600 hover:bg-blue-700"
                        } text-white rounded-lg transition-colors font-medium`}
                      >
                        {uploading ? (
                          <svg
                            className="w-5 h-5 mr-2 animate-spin"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            ></circle>
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            ></path>
                          </svg>
                        ) : (
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
                              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                          </svg>
                        )}
                        {uploading ? "Uploading..." : "Upload I-20 Form"}
                      </button>
                    </div>
                  </div>
                ) : (
                  // Regular form categories
                  <div className="grid grid-cols-1 gap-4">
                    {category.forms.map((form) => (
                      <div
                        key={form.id}
                        onClick={() => handleDefaultFormClick(form)}
                        className="form-card rounded-xl p-6 transition-all duration-200 cursor-pointer hover:scale-105"
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h5 className="text-xl font-semibold text-foreground-custom mb-2">
                              {form.title}
                            </h5>
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
                          <span className="text-blue-400 font-medium text-sm">
                            Start Form →
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Features Section */}
        <h3 className="text-3xl font-bold text-foreground-custom mb-8 text-center mt-40">
          How Formigrant Helps You
        </h3>
        <div className="bg-card-custom rounded-2xl shadow-lg p-8 mb-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
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
              <div className="w-16 h-16 bg-green-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
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
              <div className="w-16 h-16 bg-purple-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
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
