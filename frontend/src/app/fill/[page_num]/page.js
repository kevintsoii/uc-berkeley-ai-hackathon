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
  const [pageNum, setPageNum] = useState(parseInt(params.page_num));
  const [firstLoad, setFirstLoad] = useState(true);

  const [fieldValue, setFieldValue] = useState("");
  const [originalValue, setOriginalValue] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isProgressing, setIsProgressing] = useState(false);
  const [showValidationModal, setShowValidationModal] = useState(false);
  const [pageInfo, setPageInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [isFinishing, setIsFinishing] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [isProcessingPdf, setIsProcessingPdf] = useState(true);
  const [reviewData, setReviewData] = useState(null);
  useTheme(); // Initialize dark mode

  // Default form type - in a real app, this would be determined by the uploaded PDF
  const formType = "I-130";

  // Fetch page information from backend
  useEffect(() => {
    const fetchPageInfo = async (retryCount = 0) => {
      try {
        setLoading(true);
        setError(null); // Clear previous errors
        const response = await fetch(`http://localhost:8000/fill/${pageNum}`);
        if (!response.ok) {
          if (response.status === 404) {
            router.push("/fill/1");
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data);

        // Check if form is still being processed
        if (firstLoad && data.message === "Form is being processed") {
          if (retryCount < 10) {
            // Limit retries to prevent infinite loop
            console.log(
              `Form is being processed, retrying in 2 seconds... (attempt ${
                retryCount + 1
              }/10)`
            );
            setTimeout(() => {
              fetchPageInfo(retryCount + 1);
            }, 3000); // Wait 2 seconds before retry
            return;
          } else {
            throw new Error(
              "Form processing is taking too long. Please try again later."
            );
          }
        }

        setPageInfo(data);
        // Populate field value if it exists and is not empty, otherwise clear it
        const fieldVal =
          data.current_field.value && data.current_field.value !== ""
            ? data.current_field.value
            : "";
        setFieldValue(fieldVal);
        setOriginalValue(fieldVal);
        setLoading(false);
        setFirstLoad(false);
      } catch (err) {
        console.error("Error fetching page info:", err);
        setError(err.message);
      } finally {
        setIsProgressing(false); // Reset progress state
      }
    };

    fetchPageInfo();
  }, [pageNum]);

  // Fetch language from backend
  useEffect(() => {
    const fetchLanguage = async () => {
      try {
        const response = await fetch("http://localhost:8000/language");
        if (response.ok) {
          const data = await response.json();
          setSelectedLanguage(data.language);
        }
      } catch (err) {
        console.error("Error fetching language:", err);
        // Keep default "en" if fetch fails
      }
    };

    fetchLanguage();
  }, []);

  // Save field value to backend if changed
  const saveFieldValue = async (value) => {
    try {
      const response = await fetch(`http://localhost:8000/fill/${pageNum}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ value }),
      });

      if (!response.ok) {
        console.error("Failed to save field value");
      } else {
        console.log(`Saved field value: ${value}`);
      }
    } catch (error) {
      console.error("Error saving field value:", error);
    }
  };

  // Fetch form review from Gemini
  const fetchFormReview = async () => {
    try {
      const response = await fetch("http://localhost:8000/review");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log("Form review received:", data);
      setReviewData(data);
      setIsProcessingPdf(false);
    } catch (error) {
      console.error("Error fetching form review:", error);
      setIsProcessingPdf(false);
    }
  };

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

  const handleNext = async () => {
    if (
      pageInfo?.current_field?.required &&
      (!fieldValue || !fieldValue.trim())
    ) {
      setShowValidationModal(true);
      return;
    }

    // Save field value if it changed
    if (fieldValue !== originalValue) {
      await saveFieldValue(fieldValue);
    }

    // Check if this is the last page (Complete button)
    if (pageNum === pageInfo?.total_pages) {
      setIsFinishing(true);
      try {
        const response = await fetch("http://localhost:8000/finish", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Form finished successfully:", data);

        // Set finished state to show completion screen
        setIsFinished(true);

        // Start the review process
        fetchFormReview();
      } catch (error) {
        console.error("Error finishing form:", error);
        setError("Failed to complete form. Please try again.");
      } finally {
        setIsFinishing(false);
      }
      return;
    }

    // Trigger progress animation for regular navigation
    setIsProgressing(true);

    // Delay navigation to show animation
    setTimeout(() => {
      const nextPage = pageNum + 1;
      setPageNum(nextPage);
      // Update URL without triggering navigation
      window.history.replaceState(null, "", `/fill/${nextPage}`);
    }, 300);
  };

  const handlePrevious = async () => {
    if (pageNum > 1) {
      // Save field value if it changed
      if (fieldValue !== originalValue) {
        await saveFieldValue(fieldValue);
      }

      const prevPage = pageNum - 1;
      setPageNum(prevPage);
      // Update URL without triggering navigation
      window.history.replaceState(null, "", `/fill/${prevPage}`);
    }
  };

  console.log(loading);
  console.log(firstLoad);

  if (loading && firstLoad) {
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

  if (isFinishing) {
    return (
      <div className="min-h-screen bg-gradient-custom flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (isFinished) {
    return (
      <div className="min-h-screen bg-gradient-custom">
        <div className="flex h-screen">
          {/* Left side - PDF Embed */}
          <div className="w-1/2 p-4">
            <div className="h-full bg-white rounded-lg shadow-lg">
              <iframe
                src="http://localhost:8000/finished.pdf"
                className="w-full h-full rounded-lg"
                title="Finished Form PDF"
              />
            </div>
          </div>

          {/* Right side - Success message and loading */}
          <div className="w-1/2 flex flex-col items-center justify-center p-8">
            <div className="text-center">
              <div className="flex items-center justify-center mb-8">
                <div className="w-8 h-8 mr-3 bg-green-500 rounded-full flex items-center justify-center">
                  <svg
                    className="w-5 h-5 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-foreground-custom">
                  Form Completed Successfully!
                </h1>
              </div>

              {/* Loading spinner or review results */}
              {isProcessingPdf && (
                <div className="mb-8 flex flex-col items-center justify-center">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto"></div>
                  <p className="mt-4 text-secondary-custom">
                    Reviewing your finished form...
                  </p>
                </div>
              )}

              {!isProcessingPdf && reviewData && (
                <div className="mb-8 p-6 bg-card-custom rounded-xl border border-custom">
                  <div className="text-center mb-4">
                    <div className="text-3xl font-bold text-foreground-custom">
                      {reviewData.score}/100 {' '}
                      {reviewData.score >= 90 ? '🌟' : 
                       reviewData.score >= 80 ? '✨' :
                       reviewData.score >= 70 ? '👍' :
                       reviewData.score >= 60 ? '😐' :
                       '⚠️'}
                    </div>
                  </div>

                  <div className="text-center mb-4">
                    <p className="text-foreground-custom">
                      {reviewData.review}
                    </p>
                  </div>

                  {reviewData.improvements &&
                    reviewData.improvements.length > 0 && (
                      <div className="mt-4">
                        <ul className="text-sm text-secondary-custom space-y-1">
                          {reviewData.improvements.map((improvement, index) => (
                            <li key={index} className="flex items-start">
                              <span className="mr-2">•</span>
                              <span>{improvement}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                </div>
              )}

              <button
                onClick={() => router.push("/")}
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 font-medium text-lg shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Return to Home
              </button>
            </div>
          </div>
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
      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 mt-6">
        <div className="bg-card-custom rounded-2xl shadow-lg p-8 w-2xl max-w-2xl mx-auto">
          {/* Field Header */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-foreground-custom mb-2">
              {pageInfo.current_field.field}
              {pageInfo.current_field.required && (
                <span className="text-red-500 ml-1">*</span>
              )}
            </h2>
            <p className="text-secondary-custom text-md">
              {pageInfo.current_field.description}
            </p>
          </div>

          {/* Input Section */}
          <div className="space-y-6">
            <div>
              <input
                id="field-input"
                type={pageInfo.current_field.type}
                value={fieldValue}
                onChange={(e) => setFieldValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleNext();
                  }
                }}
                placeholder={`Enter text...`}
                className="w-full px-4 py-4 text-lg border-custom rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-card-custom text-foreground-custom"
                autoFocus
              />
            </div>
          </div>
        </div>
        {/* Voice Assistant Button */}
        <div className="flex justify-center">
          <VapiAssistant
            apiKey={process.env.NEXT_PUBLIC_VAPI_PUBLIC_API_KEY}
            assistantId={process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID}
            language={selectedLanguage}
            formType={formType}
            heading={pageInfo.current_field?.field || "General Information"}
            backendUrl="http://localhost:8000"
          />
        </div>
        {/* Navigation Buttons - Outside the card */}
        <div
          className={`flex mt-12 ${
            pageNum > 1 ? "justify-between" : "justify-center"
          }`}
        >
          {/* Back Button - Only show if not on first page */}
          {pageNum > 1 && (
            <button
              onClick={handlePrevious}
              className="flex items-center justify-center w-52 space-x-3 px-6 py-3 border border-custom rounded-xl hover:bg-gray-800 transition-all duration-200 text-foreground-custom"
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
            className="flex items-center justify-center space-x-3 text-center w-52 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 font-medium text-lg shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <span>
              {pageNum === pageInfo.total_pages ? "Complete" : "Next Field"}
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
        <div className="text-center mt-12">
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
