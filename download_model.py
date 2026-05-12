from transformers import pipeline

print("Downloading model...")
model_name = "ealvaradob/bert-finetuned-phishing"
classifier = pipeline("text-classification", model=model_name)
classifier.save_pretrained("./backend/ml/offline_bert_model")
print("Model saved to ./backend/ml/offline_bert_model")
