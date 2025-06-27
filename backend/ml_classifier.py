import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class MLBehaviorClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, behavior_data):
        """Extract features from behavior analysis data"""
        features = []
        
        for vehicle_id, data in behavior_data.items():
            feature_vector = [
                data.get('speed', 0),
                data.get('acceleration', 0) if data.get('acceleration') is not None else 0,
                data.get('lane_changes', 0),
                data.get('erratic_movements', 0),
                data.get('behavior_score', 0)
            ]
            features.append(feature_vector)
        
        return np.array(features) if features else np.array([]).reshape(0, 5)
    
    def train_model(self, training_data=None, use_real_data=True):
        """Train the model with real processed data or synthetic data"""
        if training_data is None:
            if use_real_data:
                # Try to load real training data from processed videos
                X, y = self._load_real_training_data()
                if len(X) == 0:
                    print("No real training data available, using synthetic data")
                    X, y = self._generate_synthetic_data()
                else:
                    print(f"Using {len(X)} real training samples from processed videos")
            else:
                # Generate synthetic training data
                X, y = self._generate_synthetic_data()
        else:
            X, y = training_data
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print(f"Model trained with {len(X)} samples")
        return self.model.score(X_scaled, y)
    
    def predict(self, behavior_data):
        """Predict behavior classification"""
        if not self.is_trained:
            self.train_model()
        
        features = self.extract_features(behavior_data)
        if len(features) == 0:
            return {}
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Make predictions
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        results = {}
        vehicle_ids = list(behavior_data.keys())
        
        for i, vehicle_id in enumerate(vehicle_ids):
            results[vehicle_id] = {
                'prediction': predictions[i],
                'confidence': max(probabilities[i]),
                'probabilities': {
                    'SAFE': probabilities[i][2],
                    'RISKY': probabilities[i][1], 
                    'DANGEROUS': probabilities[i][0]
                }
            }
        
        return results
    
    def _generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic training data"""
        np.random.seed(42)
        
        # Features: [speed, acceleration, lane_changes, erratic_movements, behavior_score]
        X = []
        y = []
        
        # Safe driving patterns
        for _ in range(n_samples // 3):
            speed = np.random.normal(30, 10)
            acceleration = np.random.normal(0, 5)
            lane_changes = np.random.poisson(0.5)
            erratic_movements = np.random.poisson(0.2)
            behavior_score = np.random.uniform(0, 30)
            
            X.append([speed, acceleration, lane_changes, erratic_movements, behavior_score])
            y.append('SAFE')
        
        # Risky driving patterns
        for _ in range(n_samples // 3):
            speed = np.random.normal(60, 15)
            acceleration = np.random.normal(0, 15)
            lane_changes = np.random.poisson(2)
            erratic_movements = np.random.poisson(1)
            behavior_score = np.random.uniform(30, 70)
            
            X.append([speed, acceleration, lane_changes, erratic_movements, behavior_score])
            y.append('RISKY')
        
        # Dangerous driving patterns
        for _ in range(n_samples // 3):
            speed = np.random.normal(100, 20)
            acceleration = np.random.normal(0, 25)
            lane_changes = np.random.poisson(4)
            erratic_movements = np.random.poisson(3)
            behavior_score = np.random.uniform(60, 100)
            
            X.append([speed, acceleration, lane_changes, erratic_movements, behavior_score])
            y.append('DANGEROUS')
        
        return np.array(X), np.array(y)
    
    def _load_real_training_data(self):
        """Load real training data from processed video results"""
        training_data_file = 'real_training_data.json'
        
        if not os.path.exists(training_data_file):
            return np.array([]).reshape(0, 5), np.array([])
        
        try:
            import json
            with open(training_data_file, 'r') as f:
                data = json.load(f)
            
            X = []
            y = []
            
            for sample in data:
                features = [
                    sample['speed'],
                    sample['acceleration'],
                    sample['lane_changes'],
                    sample['erratic_movements'],
                    sample['behavior_score']
                ]
                X.append(features)
                y.append(sample['risk_level'])
            
            return np.array(X), np.array(y)
        
        except Exception as e:
            print(f"Error loading real training data: {e}")
            return np.array([]).reshape(0, 5), np.array([])
    
    def save_training_data(self, behavior_data, filepath='real_training_data.json'):
        """Save processed behavior data for training"""
        import json
        
        # Load existing data
        existing_data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # Add new data
        for vehicle_id, data in behavior_data.items():
            training_sample = {
                'vehicle_id': vehicle_id,
                'speed': float(data.get('speed', 0)),
                'acceleration': float(data.get('acceleration', 0)) if data.get('acceleration') is not None else 0,
                'lane_changes': int(data.get('lane_changes', 0)),
                'erratic_movements': int(data.get('erratic_movements', 0)),
                'behavior_score': float(data.get('behavior_score', 0)),
                'risk_level': data.get('risk_level', 'SAFE')
            }
            existing_data.append(training_sample)
        
        # Save updated data
        with open(filepath, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"Saved {len(behavior_data)} training samples to {filepath}")
    
    def save_model(self, filepath='behavior_model.pkl'):
        """Save trained model and scaler"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='behavior_model.pkl'):
        """Load trained model and scaler"""
        if os.path.exists(filepath):
            try:
                model_data = joblib.load(filepath)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = model_data['is_trained']
                print(f"Model loaded from {filepath}")
                return True
            except Exception as e:
                print(f"Error loading saved model: {e}")
                print("Training new model instead...")
                self.train_model()
                self.save_model(filepath)
                return True
        return False