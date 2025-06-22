"use client";

export default function Header({
  showProgress = false,
  progress = 0,
  currentPage = 1,
  totalPages = 1,
  isProgressing = false,
}) {
  return (
    <header className="bg-header-custom sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div
          className={`flex items-center justify-between ${
            showProgress ? "mb-4" : ""
          }`}
        >
          <a
            href="/"
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
          >
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-foreground-custom">
              Formigrant
            </h1>
          </a>

          <div className="flex items-center space-x-6">
            {/* Navigation - only show when no progress bar */}
            {!showProgress && (
              <nav className="hidden md:flex items-center space-x-6">
                <a
                  href="#how-it-works"
                  className="text-secondary-custom hover:text-blue-600 transition-colors"
                >
                  How it Works
                </a>
                <a
                  href="#support"
                  className="text-secondary-custom hover:text-blue-600 transition-colors"
                >
                  Support
                </a>
                <a
                  href="#contact"
                  className="text-secondary-custom hover:text-blue-600 transition-colors"
                >
                  Contact
                </a>
              </nav>
            )}

            {/* Page indicator for fill pages */}
            {showProgress && (
              <div className="text-sm text-secondary-custom">
                Page {currentPage} of {totalPages}
              </div>
            )}
          </div>
        </div>

        {/* Progress Bar - only show on fill pages */}
        {showProgress && (
          <>
            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className={`progress-gradient h-3 rounded-full transition-all duration-500 ease-out ${
                  isProgressing ? "animate-pulse" : ""
                }`}
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-secondary-custom mt-2">
              <span>Started</span>
              <span>{Math.round(progress)}% Complete</span>
              <span>Finished</span>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
