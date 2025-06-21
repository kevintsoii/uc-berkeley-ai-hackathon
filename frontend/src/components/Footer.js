export default function Footer() {
  return (
    <footer className="bg-slate-800/50 border-t border-custom mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-6 h-6 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg
                className="w-4 h-4 text-white"
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
            <h3 className="text-lg font-bold text-foreground-custom">
              FormBridge
            </h3>
          </div>
          <p className="text-secondary-custom mb-4 text-sm">
            Making immigration forms accessible to everyone, regardless of
            language barriers.
          </p>
          <div className="flex justify-center space-x-6 text-xs text-secondary-custom">
            <a
              href="#privacy"
              className="hover:text-blue-600 transition-colors"
            >
              Privacy Policy
            </a>
            <a href="#terms" className="hover:text-blue-600 transition-colors">
              Terms of Service
            </a>
            <a href="#help" className="hover:text-blue-600 transition-colors">
              Help Center
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
