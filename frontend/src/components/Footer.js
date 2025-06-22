export default function Footer() {
  return (
    <footer className="bg-slate-800/50 border-t border-custom mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
         
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
              className="hover:text-blue-600 transition-colors text-white"
            >
              Privacy Policy
            </a>
            <a
              href="#terms"
              className="hover:text-blue-600 transition-colors text-white"
            >
              Terms of Service
            </a>
            <a
              href="#help"
              className="hover:text-blue-600 transition-colors text-white"
            >
              Help Center
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
