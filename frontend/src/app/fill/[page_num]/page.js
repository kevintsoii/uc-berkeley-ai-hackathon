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

  // Form configuration - in a real app, this would come from the uploaded PDF analysis
  const formFields = [
    {
      id: 1,
      name: "First Name",
      placeholder: "Enter your first name",
      type: "text",
    },
    {
      id: 2,
      name: "Middle Name",
      placeholder: "Enter your middle name (optional)",
      type: "text",
    },
    {
      id: 3,
      name: "Last Name",
      placeholder: "Enter your last name",
      type: "text",
    },
  ];

  const totalPages = formFields.length;
  const currentField = formFields[pageNum - 1];
  const progress = (pageNum / totalPages) * 100;

  // Default form type - in a real app, this would be determined by the uploaded PDF
  const formType = "I-130";

  // Redirect if page number is invalid
  useEffect(() => {
    if (pageNum < 1 || pageNum > totalPages) {
      router.push("/fill/1");
    }
  }, [pageNum, totalPages, router]);

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

  const handleVoiceAssistant = () => {
    setIsListening(!isListening);
    // In a real app, this would trigger voice synthesis or recognition
    if (!isListening) {
      // Simulate voice assistance
      const assistanceText = getVoiceAssistance(currentField?.name);
      if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(assistanceText);
        utterance.rate = 0.8;
        utterance.onend = () => setIsListening(false);
        speechSynthesis.speak(utterance);
      }
    } else {
      // Stop speech if currently speaking
      if ("speechSynthesis" in window) {
        speechSynthesis.cancel();
      }
    }
  };

  const getVoiceAssistance = (fieldName) => {
    const assistanceMap = {
      "First Name":
        "Please enter your first name as it appears on your official documents. This is your given name, not your family name or surname.",
      "Middle Name":
        'Enter your middle name if you have one. This field is optional. If you don\'t have a middle name, you can leave this blank or write "N/A".',
      "Last Name":
        "Please enter your last name, also known as your family name or surname. This should match exactly with your official documents.",
    };
    return (
      assistanceMap[fieldName] ||
      `Please enter your ${fieldName.toLowerCase()}.`
    );
  };

  const handleNext = () => {
    if (!fieldValue.trim() && currentField?.name !== "Middle Name") {
      setShowValidationModal(true);
      return;
    }

    // Trigger progress animation
    setIsProgressing(true);

    // Save the current field value (in a real app, this would be stored in state management or API)
    console.log(`Saving ${currentField?.name}: ${fieldValue}`);

    // Delay navigation to show animation
    setTimeout(() => {
      if (pageNum < totalPages) {
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

  if (!currentField) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-custom flex flex-col">
      <Header
        showProgress={true}
        progress={progress}
        currentPage={pageNum}
        totalPages={totalPages}
        isProgressing={isProgressing}
      />

      {/* Main Content */}
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-card-custom rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
          {/* Field Header */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-foreground-custom mb-2">
              {currentField.name}
            </h2>
            <p className="text-secondary-custom">
              Please provide your {currentField.name.toLowerCase()} as it
              appears on your official documents.
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
              <label
                htmlFor="field-input"
                className="block text-sm font-medium text-foreground-custom mb-2"
              >
                {currentField.name}{" "}
                {currentField.name !== "Middle Name" && (
                  <span className="text-red-500">*</span>
                )}
              </label>
              <input
                id="field-input"
                type={currentField.type}
                value={fieldValue}
                onChange={(e) => setFieldValue(e.target.value)}
                placeholder={currentField.placeholder}
                className="w-full px-4 py-4 text-lg border-custom rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-card-custom text-foreground-custom"
                autoFocus
              />
            </div>

            {/* Voice Assistant Button */}
            <div className="flex justify-center">
              <VapiAssistant 
                apiKey={process.env.NEXT_PUBLIC_VAPI_PUBLIC_API_KEY}
                assistantId={process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID}
                language={selectedLanguage}
                formType={formType}
                heading={currentField?.name || "General Information"}
                backendUrl="http://localhost:8000"
              />
              <button
                onClick={handleVoiceAssistant}
                className={`flex items-center space-x-3 px-6 py-3 rounded-xl transition-all duration-200 shadow-sm ${
                  isListening
                    ? "bg-red-500 hover:bg-red-600 text-white"
                    : "bg-blue-900/50 hover:bg-blue-900/70 text-blue-300 border-2 border-blue-700 hover:border-blue-600"
                }`}
              >
                <svg
                  className={`w-5 h-5 ${isListening ? "animate-pulse" : ""}`}
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
                <span className="font-medium">
                  {isListening
                    ? "Stop Voice Assistant"
                    : "Need Help? Ask Voice Assistant"}
                </span>
              </button>
            </div>

            {/* Voice Assistant Info */}
            {isListening && (
              <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <svg
                    className="w-5 h-5 text-blue-400 mt-0.5 animate-pulse"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div>
                    <h4 className="text-sm font-medium text-blue-200">
                      Voice Assistant Active
                    </h4>
                    <p className="text-sm text-blue-300 mt-1">
                      Providing guidance for: {currentField.name}
                    </p>
                  </div>
                </div>
              </div>
            )}
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
              {pageNum === totalPages ? "Complete Form" : "Next Field"}
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
        fieldName={currentField?.name}
      />
    </div>
  );
}
