import os
import ast
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import joblib

def extract_text(data_str):
    try:
        parsed = ast.literal_eval(data_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed[0]
        return ""
    except Exception:
        return ""

def main():
    print("Downloading Hugging Face dataset (bvk/SpamAssassin-spam)...")
    dataset = load_dataset('bvk/SpamAssassin-spam')
    
    # This dataset only has a 'train' split
    data = dataset['train']
    
    print("Parsing text data...")
    # Extract the actual text from the string representation of lists
    X = [extract_text(item) for item in data['data']]
    y = data['label'] # 1 is spam/phishing, 0 is safe
    
    print("Splitting into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training on {len(X_train)} emails, testing on {len(X_test)}...")
    
    # Create the pipeline
    model = make_pipeline(TfidfVectorizer(stop_words='english', max_features=50000), LogisticRegression(max_iter=500))
    
    # Train the model
    print("Training the model... this might take a minute.")
    model.fit(X_train, y_train)
    
    # Evaluate the model
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc * 100:.2f}%\n")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Phishing']))
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'phishguard_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model successfully saved to {model_path}!")

if __name__ == "__main__":
    main()
