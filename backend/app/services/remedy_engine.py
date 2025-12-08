import pandas as pd
import os

class RemedyEngine:
    def __init__(self):
        self.df = None
        self.load_data()

    def load_data(self):
        """Loads the MEDICATION.csv file into a Pandas DataFrame."""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_path, '..', 'ml_assets', 'MEDICATION.csv')
            
            if os.path.exists(csv_path):
                self.df = pd.read_csv(csv_path)
                # Normalize column names to be safe
                self.df.columns = [c.strip() for c in self.df.columns]
                print("✅ Remedy Engine: Knowledge Base Loaded")
            else:
                print(f"❌ Remedy Engine: CSV not found at {csv_path}")
        except Exception as e:
            print(f"❌ Remedy Engine Error: {e}")

    def get_remedy(self, condition_name):
        """
        Searches for a condition (e.g., 'Depression') and returns the full remedy details.
        It uses case-insensitive partial matching.
        """
        if self.df is None:
            return {"error": "Database not loaded"}

        # Search for the condition (case-insensitive)
        # We check if the search term is IN the 'Mental Condition' column
        mask = self.df['Mental Condition'].str.contains(condition_name, case=False, na=False)
        result = self.df[mask]

        if result.empty:
            return None

        # Get the first match
        row = result.iloc[0]

        return {
            "condition": row['Mental Condition'],
            "symptoms": row['Symptoms'],
            "treatments": row['Recommended Treatments'],
            "medications": row['Medications'],
            "dosage": row['Dosage'],
            "gita_remedy": row['Advanced Remedies']  # This is the story/advice
        }

# Singleton instance
remedy_engine = RemedyEngine()