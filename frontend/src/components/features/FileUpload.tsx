import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, CheckCircle } from 'lucide-react';
import Button from '../ui/Button';
import ProgressBar from '../ui/ProgressBar';
import { uploadVideo } from '../../utils/api';
import { VideoAnalysisResult, UploadProgress } from '../../types';
import toast from 'react-hot-toast';

interface FileUploadProps {
  onUploadComplete: (result: VideoAnalysisResult) => void;
  onUploadStart?: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete, onUploadStart }) => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('video/')) {
      toast.error('Please upload a video file');
      return;
    }

    // Validate file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
      toast.error('File size must be less than 100MB');
      return;
    }

    setUploadedFile(file);
    setIsUploading(true);
    onUploadStart?.();

    try {
      const result = await uploadVideo(file, (progress) => {
        setUploadProgress(progress);
      });

      console.log('Upload result:', result);
      console.log('Result type:', typeof result);
      console.log('Result keys:', result ? Object.keys(result) : 'null/undefined');
      console.log('Full result object:', JSON.stringify(result, null, 2));
      
      // Check if result has the expected structure
      if (!result) {
        console.error('Null/undefined result from server');
        toast.error('No response from server. Please check your connection.');
        return;
      }
      
      // Check if models are still loading (various response formats)
      const resultAny = result as any;
      if ((resultAny.message && resultAny.message.includes('endpoint ready') && resultAny.note && resultAny.note.includes('models finish loading')) ||
          (resultAny.error && resultAny.error.includes('models are still loading')) ||
          (resultAny.status === 'models_loading')) {
        console.log('Models are still loading on server');
        toast.error('AI models are still initializing. Please wait a few minutes and try again.');
        return;
      }
      
      if (!result.summary) {
        console.error('Missing summary in result:', result);
        console.error('Expected summary field with: total_unique_vehicles, dangerous_vehicles, risky_vehicles, safe_vehicles');
        
        // Check if we have results but no summary - create a basic summary
        if (result.results && Array.isArray(result.results) && result.results.length > 0) {
          console.log('Found results array but no summary. Creating basic summary from results...');
          
          // Create a basic summary from the results array
          const vehicleIds = new Set(result.results.map((r: any) => r.id));
          const riskCounts = result.results.reduce((acc: Record<string, number>, r: any) => {
            const risk = r.risk_level || 'SAFE';
            acc[risk] = (acc[risk] || 0) + 1;
            return acc;
          }, {} as Record<string, number>);
          
          result.summary = {
            total_unique_vehicles: vehicleIds.size,
            dangerous_vehicles: riskCounts.DANGEROUS || 0,
            risky_vehicles: riskCounts.RISKY || 0,
            safe_vehicles: riskCounts.SAFE || 0
          };
          
          console.log('Created summary:', result.summary);
        } else {
          toast.error('Video processed but no vehicles were detected. The video may not contain visible vehicles or the detection confidence may be too low.');
          return;
        }
      }

      console.log('Summary:', result.summary);
      toast.success('Video processed successfully!');
      onUploadComplete(result);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to process video. Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress(null);
    }
  }, [onUploadComplete, onUploadStart]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
    },
    multiple: false,
    disabled: isUploading
  });

  const removeFile = () => {
    setUploadedFile(null);
    setUploadProgress(null);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <AnimatePresence mode="wait">
        {!uploadedFile ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <div
              {...getRootProps()}
              className={`
                relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                transition-all duration-300 ease-in-out
                ${isDragActive 
                  ? 'border-primary-500 bg-primary-50 scale-105' 
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                }
                ${isUploading ? 'pointer-events-none opacity-60' : ''}
              `}
            >
              <input {...getInputProps()} />
              
              <motion.div
                animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
                transition={{ duration: 0.2 }}
              >
                <Upload className={`
                  mx-auto h-12 w-12 mb-4 transition-colors duration-300
                  ${isDragActive ? 'text-primary-600' : 'text-gray-400'}
                `} />
              </motion.div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {isDragActive ? 'Drop your video here' : 'Upload a video file'}
              </h3>
              
              <p className="text-gray-500 mb-4">
                Drag & drop your video file here, or click to browse
              </p>
              
              <div className="text-sm text-gray-400 mb-6">
                <p>Supported formats: MP4, AVI, MOV, WMV, FLV, WebM</p>
                <p>Maximum file size: 100MB</p>
              </div>

              <Button
                variant="primary"
                size="lg"
                disabled={isUploading}
                icon={<Upload className="w-4 h-4" />}
              >
                Choose File
              </Button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="file-preview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white rounded-xl border border-gray-200 p-6"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <File className="h-8 w-8 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {uploadedFile.name}
                  </h4>
                  <p className="text-sm text-gray-500">
                    {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              
              {!isUploading && (
                <button
                  onClick={removeFile}
                  className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>

            {uploadProgress && (
              <div className="mb-4">
                <ProgressBar
                  progress={uploadProgress.percentage}
                  color="primary"
                  showPercentage={true}
                />
                <div className="flex justify-between items-center mt-2 text-sm text-gray-500">
                  <span>
                    {(uploadProgress.loaded / (1024 * 1024)).toFixed(1)} MB of{' '}
                    {(uploadProgress.total / (1024 * 1024)).toFixed(1)} MB
                  </span>
                  <span>{uploadProgress.percentage}%</span>
                </div>
              </div>
            )}

            <div className="flex items-center space-x-2">
              {isUploading ? (
                <>
                  <div className="flex items-center space-x-2 text-primary-600">
                    <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm font-medium">Processing video...</span>
                  </div>
                </>
              ) : (
                <div className="flex items-center space-x-2 text-success-600">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Ready to process</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FileUpload;