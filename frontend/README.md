# Vehicle Behavior Detector - Frontend

React + TypeScript frontend for the AI-powered vehicle behavior detection system.

## 🚀 Quick Deploy

### Option 1: Vercel (Recommended)
1. Push this frontend folder to a GitHub repository
2. Connect to Vercel: https://vercel.com/new
3. Deploy automatically with zero configuration

### Option 2: Netlify
1. Push this frontend folder to a GitHub repository  
2. Connect to Netlify: https://app.netlify.com/start
3. Deploy automatically with zero configuration

### Option 3: Manual Deploy
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Upload the 'build' folder to any static hosting service
```

## 🔧 Configuration

The app is pre-configured to connect to your Railway backend:
- **Backend API**: `https://visionbasedvehiclebehavior-production.up.railway.app`

To change the backend URL, set the environment variable:
```
REACT_APP_API_URL=your-backend-url
```

## 📱 Features

- **Drag & Drop Upload**: Upload video files for analysis
- **Real-time Processing**: Watch analysis progress with live updates
- **Sample Videos**: Test with pre-loaded demo content
- **Professional UI**: Senior-level design with Tailwind CSS
- **Responsive Design**: Works on desktop and mobile
- **Results Dashboard**: Comprehensive analytics and risk visualization

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000
```

## 📊 Backend Integration

The frontend automatically connects to your Railway backend API which provides:
- **ML Model Status**: Real-time loading status
- **Video Processing**: Upload and analyze traffic footage
- **Sample Data**: Demo videos with different risk scenarios
- **Health Monitoring**: API status and model readiness

## 🎨 Tech Stack

- **React 18** + **TypeScript**
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Dropzone** for file uploads
- **Axios** for API communication
- **Lucide React** for icons