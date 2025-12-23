import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

class ConversationClassifier:
    def __init__(self):
        # Adjusted Anchors: Lowered requirements for 'Healthy' vibes
        # Features: [ReplyBalance, InitBalance, SentStability, LengthBalance, EmojiDensity]
        self.anchors = np.array([
            [0.70, 0.70, 0.85, 0.70, 0.15], # Cluster 0: Synchronized Duo (Lowered Emoji)
            [0.10, 0.10, 0.40, 0.20, 0.05], # Cluster 1: One-Sided
            [0.50, 0.50, 0.90, 0.40, 0.00], # Cluster 2: Professional / Dry
            [0.60, 0.60, 0.30, 0.60, 0.40]  # Cluster 3: High-Energy / Emotional
        ])
        
        self.scaler = MinMaxScaler()
        self.model = KMeans(n_clusters=4, init=self.anchors, n_init=1)
        
        self.persona_names = {
            0: "Synchronized Duo",
            1: "One-Sided / Ghosting Risk",
            2: "Professional / Dry Texter",
            3: "High-Energy / Emotional"
        }

    def predict(self, features: dict):
        # 1. HARD OVERRIDE (The "Human Vibe" Logic)
        # If the length balance is perfect and they are using emojis, 
        # it's NOT Professional, even if reply time is a bit off.
        if features['msg_length_balance'] > 0.8 and features['emoji_density'] > 0.1:
            return self.persona_names[0] # Force "Synchronized Duo"

        # 2. VECTOR PREDICTION
        vector = np.array([[
            features['reply_time_balance'],
            features['initiation_balance'],
            features['sentiment_stability'],
            features['msg_length_balance'],
            features['emoji_density']
        ]])
        
        combined_data = np.vstack([self.anchors, vector])
        scaled_data = self.scaler.fit_transform(combined_data)
        
        self.model.fit(scaled_data[:-1])
        cluster_id = self.model.predict(scaled_data[-1:])
        
        predicted_persona = self.persona_names[cluster_id[0]]

        # 3. SAFETY CHECK
        # If categorized as Dry but has good sentiment and length balance, shift it up.
        if predicted_persona == "Professional / Dry Texter" and features['sentiment_stability'] > 0.8:
            if features['reply_time_balance'] > 0.3:
                return self.persona_names[0] # Upgrade to Synchronized Duo

        return predicted_persona