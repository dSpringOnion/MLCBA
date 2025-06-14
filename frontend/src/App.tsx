import React, { useState, useRef } from 'react';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/layout/Header';
import Hero from './components/features/Hero';
import FileUpload from './components/features/FileUpload';
import ResultsDisplay from './components/features/ResultsDisplay';
import { VideoAnalysisResult } from './types';

function App() {
  const [showDemo, setShowDemo] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<VideoAnalysisResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const demoRef = useRef<HTMLDivElement>(null);

  const handleGetStarted = () => {
    setShowDemo(true);
    setTimeout(() => {
      demoRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleUploadComplete = (result: VideoAnalysisResult) => {
    setAnalysisResult(result);
    setIsProcessing(false);
  };

  const handleUploadStart = () => {
    setIsProcessing(true);
    setAnalysisResult(null);
  };

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />
      
      <main className="relative">
        {/* Hero Section */}
        <Hero onGetStarted={handleGetStarted} />

        {/* Demo Section */}
        <AnimatePresence>
          {showDemo && (
            <motion.section
              ref={demoRef}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="py-20 px-4 sm:px-6 lg:px-8"
            >
              <div className="max-w-6xl mx-auto">
                <div className="text-center mb-12">
                  <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-4xl font-bold text-gray-900 mb-4"
                  >
                    Upload & Analyze Traffic Video
                  </motion.h2>
                  <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    className="text-xl text-gray-600 max-w-3xl mx-auto"
                  >
                    Upload your video footage to detect dangerous driving behaviors, 
                    analyze traffic patterns, and get comprehensive safety insights.
                  </motion.p>
                </div>

                {/* Upload and Results Container */}
                <div className="space-y-8">
                  {!analysisResult && !isProcessing && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.4, delay: 0.6 }}
                    >
                      <FileUpload
                        onUploadComplete={handleUploadComplete}
                        onUploadStart={handleUploadStart}
                      />
                    </motion.div>
                  )}

                  {isProcessing && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4 }}
                      className="text-center py-20"
                    >
                      <div className="inline-flex items-center space-x-4 px-8 py-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg">
                        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">Processing Video</h3>
                          <p className="text-gray-600">Analyzing vehicle behavior patterns...</p>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {analysisResult && (
                    <motion.div
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6 }}
                      className="space-y-6"
                    >
                      <div className="text-center">
                        <button
                          onClick={handleNewAnalysis}
                          className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200 font-medium"
                        >
                          Analyze Another Video
                        </button>
                      </div>
                      
                      <ResultsDisplay results={analysisResult} />
                    </motion.div>
                  )}
                </div>

                {/* Sample Videos Section */}
                {!isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.8 }}
                    className="mt-20 pt-12 border-t border-gray-200"
                  >
                    <div className="text-center mb-8">
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">
                        Don't have a video? Try our samples
                      </h3>
                      <p className="text-gray-600">
                        Test the system with pre-loaded traffic footage demonstrating different risk scenarios
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {[
                        { name: 'Highway Traffic', risk: 'Low Risk', desc: 'Normal highway driving patterns' },
                        { name: 'City Intersection', risk: 'Medium Risk', desc: 'Urban traffic with lane changes' },
                        { name: 'Aggressive Driving', risk: 'High Risk', desc: 'Dangerous driving behaviors' }
                      ].map((sample, index) => (
                        <motion.div
                          key={sample.name}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.4, delay: 1 + index * 0.1 }}
                          className="bg-white/70 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:shadow-lg transition-all duration-300 cursor-pointer"
                        >
                          <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg mb-4 flex items-center justify-center">
                            <div className="text-4xl">🚗</div>
                          </div>
                          <h4 className="font-semibold text-gray-900 mb-2">{sample.name}</h4>
                          <p className="text-sm text-gray-600 mb-3">{sample.desc}</p>
                          <div className={`
                            inline-block px-3 py-1 rounded-full text-xs font-medium
                            ${sample.risk === 'Low Risk' ? 'bg-success-100 text-success-800' :
                              sample.risk === 'Medium Risk' ? 'bg-warning-100 text-warning-800' :
                              'bg-danger-100 text-danger-800'}
                          `}>
                            {sample.risk}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.section>
          )}
        </AnimatePresence>
      </main>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#333',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            borderRadius: '12px',
            border: '1px solid rgba(0, 0, 0, 0.1)',
          },
        }}
      />
    </div>
  );
}

export default App;