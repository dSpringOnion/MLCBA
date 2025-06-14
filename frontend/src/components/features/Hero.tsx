import React from 'react';
import { motion } from 'framer-motion';
import { Play, Upload, Eye, Zap, Shield, TrendingUp } from 'lucide-react';
import Button from '../ui/Button';
import Card from '../ui/Card';

interface HeroProps {
  onGetStarted: () => void;
}

const Hero: React.FC<HeroProps> = ({ onGetStarted }) => {
  const features = [
    {
      icon: <Eye className="w-6 h-6" />,
      title: "Real-time Detection",
      description: "Advanced YOLO-based vehicle tracking with behavioral analysis"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "ML Classification",
      description: "Machine learning model classifies driving behavior as safe, risky, or dangerous"
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Comprehensive Analytics",
      description: "Speed analysis, lane changes, erratic movements, and acceleration tracking"
    }
  ];

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-20 h-20 bg-primary-500 rounded-full animate-float" />
        <div className="absolute top-40 right-20 w-16 h-16 bg-purple-500 rounded-full animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-20 left-1/4 w-12 h-12 bg-blue-500 rounded-full animate-float" style={{ animationDelay: '4s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-8"
          >
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                AI-Powered
              </span>
              <br />
              Vehicle Behavior Detection
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Detect dangerous and unpredictable driving patterns in real-time using advanced 
              computer vision and machine learning. Upload your video footage and get instant 
              safety analysis.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
          >
            <Button
              size="lg"
              onClick={onGetStarted}
              className="px-8 py-4 text-lg font-semibold"
              icon={<Upload className="w-5 h-5" />}
            >
              Try Demo Now
            </Button>
            <Button
              variant="secondary"
              size="lg"
              className="px-8 py-4 text-lg font-semibold"
              icon={<Play className="w-5 h-5" />}
            >
              Watch Demo
            </Button>
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
              >
                <Card className="p-8 text-center hover" glass>
                  <div className="flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-gradient-to-r from-primary-100 to-blue-100 rounded-2xl">
                    <div className="text-primary-600">
                      {feature.icon}
                    </div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* Technical Stack */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="mt-20 pt-12 border-t border-gray-200"
          >
            <p className="text-sm text-gray-500 mb-6">Powered by</p>
            <div className="flex flex-wrap justify-center items-center gap-8 text-gray-400">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5" />
                <span className="font-medium">YOLOv8</span>
              </div>
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5" />
                <span className="font-medium">OpenCV</span>
              </div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span className="font-medium">Scikit-learn</span>
              </div>
              <div className="flex items-center space-x-2">
                <Eye className="w-5 h-5" />
                <span className="font-medium">React + TypeScript</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Hero;