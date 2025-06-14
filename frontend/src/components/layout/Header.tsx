import React from 'react';
import { motion } from 'framer-motion';
import { Car, Brain, Shield, Github } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <motion.header 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="relative bg-white/80 backdrop-blur-md border-b border-gray-200/50 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center space-x-4">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
              className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-primary-600 to-blue-600 rounded-xl"
            >
              <Car className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                Vehicle Behavior Detector
              </h1>
              <p className="text-sm text-gray-600">AI-Powered Traffic Safety Analysis</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <div className="hidden md:flex items-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-primary-600" />
                <span>YOLO Detection</span>
              </div>
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4 text-success-600" />
                <span>ML Classification</span>
              </div>
            </div>
            
            <motion.a
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              href="https://github.com/danielpark"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">View Code</span>
            </motion.a>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;