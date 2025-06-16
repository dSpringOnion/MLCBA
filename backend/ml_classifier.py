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
    
    def train_model(self, training_data=None):
        """Train the model with synthetic data or provided data"""
        if training_data is None:
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