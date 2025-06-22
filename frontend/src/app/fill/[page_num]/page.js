"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ValidationModal from "@/components/ValidationModal";
import { useTheme } from "@/hooks/useTheme";
import VapiAssistant from "@/components/VapiAssistant";

export default function FillPage() {
  const router = useRouter();
  const params = useParams();
  const pageNum = parseInt(params.page_num);

  const [fieldValue, setFieldValue] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isProgressing, setIsProgressing] = useState(false);
  const [showValidationModal, setShowValidationModal] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [pageInfo, setPageInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useTheme(); // Initialize dark mode

  // Language options
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

  // Default form type - in a real app, this would be determined by the uploaded PDF
  const formType = "I-130";

  // Fetch page information from backend
  useEffect(() => {
    const fetchPageInfo = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/fill/${pageNum}`);
        if (!response.ok) {
          if (response.status === 404) {
            router.push("/fill/1");
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setPageInfo(data);
      } catch (err) {
        console.error("Error fetching page info:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPageInfo();
  }, [pageNum, router]);

  // Redirect if page number is invalid - now handled by backend
  useEffect(() => {
    if (error && error.includes("404")) {
      router.push("/fill/1");
    }
  }, [error, router]);

  // Handle escape key for modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape" && showValidationModal) {
        setShowValidationModal(false);
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [showValidationModal]);

  const handleNext = () => {
    if (!fieldValue.trim() && pageInfo?.current_field?.required) {
      setShowValidationModal(true);
      return;
    }

    // Trigger progress animation
    setIsProgressing(true);

    // Save the current field value (in a real app, this would be stored in state management or API)
    console.log(`Saving ${pageInfo?.current_field?.field}: ${fieldValue}`);

    // Delay navigation to show animation
    setTimeout(() => {
      if (pageNum < pageInfo?.total_pages) {
        router.push(`/fill/${pageNum + 1}`);
      } else {
        // Redirect to completion page or summary
        router.push("/complete");
      }
    }, 300);
  };

  const handlePrevious = () => {
    if (pageNum > 1) {
      router.push(`/fill/${pageNum - 1}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-custom flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-foreground-custom">
            Loading page information...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-custom flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500">Error loading page: {error}</p>
          <button
            onClick={() => router.push("/fill/1")}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Go to First Page
          </button>
        </div>
      </div>
    );
  }

  if (!pageInfo) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-custom flex flex-col">
      <Header
        showProgress={true}
        progress={(pageNum / pageInfo.total_pages) * 100}
        currentPage={pageNum}
        totalPages={pageInfo.total_pages}
        isProgressing={isProgressing}
      />

      {/* Main Content */}
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-card-custom rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
          {/* Field Header */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-foreground-custom mb-2">
              {pageInfo.current_field.field}
              {pageInfo.current_field.required && (
                <span className="text-red-500 ml-1">*</span>
              )}
            </h2>
            <p className="text-secondary-custom">
              {pageInfo.current_field.description}
              {!pageInfo.current_field.required && (
                <span className="text-gray-400 ml-2">(Optional)</span>
              )}
            </p>
          </div>

          {/* Language Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-foreground-custom mb-2">
              Voice Assistant Language
            </label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full px-4 py-3 text-lg border-custom rounded-xl bg-card-custom text-foreground-custom focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {languages.map((language) => (
                <option key={language.code} value={language.code}>
                  {language.native} ({language.name})
                </option>
              ))}
            </select>
          </div>

          {/* Input Section */}
          <div className="space-y-6">
            <div>
              <input
                id="field-input"
                type={pageInfo.current_field.type}
                value={fieldValue}
                onChange={(e) => setFieldValue(e.target.value)}
                className="w-full px-4 py-4 text-lg border-custom rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-card-custom text-foreground-custom"
                autoFocus
              />
            </div>
          </div>
        </div>

        {/* Navigation Buttons - Outside the card */}
        <div
          className={`flex mt-8 ${
            pageNum > 1 ? "justify-between" : "justify-center"
          }`}
        >
          {/* Back Button - Only show if not on first page */}
          {pageNum > 1 && (
            <button
              onClick={handlePrevious}
              className="flex items-center space-x-3 px-6 py-3 border border-custom rounded-xl hover:bg-gray-800 transition-all duration-200 text-foreground-custom"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              <span>Previous</span>
            </button>
          )}

          {/* Next Button */}
          <button
            onClick={handleNext}
            className="flex items-center space-x-3 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 font-medium text-lg shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <span>
              {pageNum === pageInfo.total_pages
                ? "Complete Form"
                : "Next Field"}
            </span>
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>

        {/* Helper Text */}
        <div className="text-center mt-6">
          <p className="text-sm text-secondary-custom">
            Having trouble? Use the voice assistant button above for detailed
            guidance on this field.
          </p>
        </div>
      </main>

      <Footer />

      <ValidationModal
        isOpen={showValidationModal}
        onClose={() => setShowValidationModal(false)}
        fieldName={pageInfo?.current_field?.field}
      />
    </div>
  );
}
