"""
Crisis Detection Model Training Script
Trains DistilBERT on Suicide Detection Dataset
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from datasets import Dataset
import torch
import os
from pathlib import Path

print("="*70)
print("Crisis Detection Model Training")
print("="*70)

# Configuration
DATA_PATH = "app/ml/crisis_detection/datasets/Suicide_Detection.csv"
OUTPUT_DIR = "app/ml/crisis_detection/pretrained_models/crisis_detector"
MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 128
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5
SAMPLE_SIZE = 50000  # Use 50k samples for faster training (or None for all data)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Load Dataset
print(f"\n📂 Loading dataset from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)
print(f"   Total samples: {len(df):,}")
print(f"   Columns: {df.columns.tolist()}")

# Step 2: Prepare Data
print("\n🔧 Preparing data...")

# Clean data
df = df.dropna(subset=['text', 'class'])
df['text'] = df['text'].astype(str).str.strip()
df = df[df['text'].str.len() > 10]  # Remove very short texts

# Convert labels to binary
df['label'] = (df['class'] == 'suicide').astype(int)

print(f"   After cleaning: {len(df):,} samples")
print(f"   Suicide cases: {df['label'].sum():,} ({df['label'].mean()*100:.1f}%)")
print(f"   Non-suicide cases: {(df['label']==0).sum():,} ({(1-df['label'].mean())*100:.1f}%)")

# Sample data if needed (for faster training)
if SAMPLE_SIZE and len(df) > SAMPLE_SIZE:
    print(f"\n⚡ Sampling {SAMPLE_SIZE:,} examples for faster training...")
    # Stratified sampling to keep class balance
    df = df.groupby('label', group_keys=False).apply(
        lambda x: x.sample(min(len(x), SAMPLE_SIZE//2), random_state=42)
    )
    print(f"   Sampled: {len(df):,} samples")
    print(f"   Suicide: {df['label'].sum():,}, Non-suicide: {(df['label']==0).sum():,}")

# Split data: 80% train, 10% val, 10% test
print("\n✂️  Splitting data...")
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'])

print(f"   Train: {len(train_df):,} samples")
print(f"   Validation: {len(val_df):,} samples")
print(f"   Test: {len(test_df):,} samples")

# Step 3: Tokenization
print(f"\n🔤 Loading tokenizer: {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(
        examples['text'],
        padding='max_length',
        truncation=True,
        max_length=MAX_LENGTH
    )

# Convert to HuggingFace Dataset
train_dataset = Dataset.from_pandas(train_df[['text', 'label']])
val_dataset = Dataset.from_pandas(val_df[['text', 'label']])
test_dataset = Dataset.from_pandas(test_df[['text', 'label']])

print("   Tokenizing datasets...")
train_dataset = train_dataset.map(tokenize_function, batched=True)
val_dataset = val_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# Step 4: Load Model
print(f"\n🧠 Loading model: {MODEL_NAME}...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    problem_type="single_label_classification"
)

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   Using device: {device}")

# Step 5: Training Configuration
print("\n⚙️  Configuring training...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    push_to_hub=False,
    logging_dir=f"{OUTPUT_DIR}/logs",
    logging_steps=100,
    save_total_limit=2,
)

# Define metrics
def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    accuracy = accuracy_score(labels, predictions)
    return {"accuracy": accuracy}

# Step 6: Train Model
print("\n🚀 Starting training...")
print(f"   Epochs: {EPOCHS}")
print(f"   Batch size: {BATCH_SIZE}")
print(f"   Learning rate: {LEARNING_RATE}")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# Train!
print("\n" + "="*70)
print("Training Started...")
print("="*70)
trainer.train()

# Step 7: Evaluate on Test Set
print("\n" + "="*70)
print("📊 Evaluating on Test Set...")
print("="*70)

predictions = trainer.predict(test_dataset)
pred_labels = np.argmax(predictions.predictions, axis=1)
true_labels = predictions.label_ids

# Calculate metrics
accuracy = accuracy_score(true_labels, pred_labels)
print(f"\n✅ Test Accuracy: {accuracy*100:.2f}%")

print("\n📈 Classification Report:")
print(classification_report(
    true_labels,
    pred_labels,
    target_names=['Non-Suicide', 'Suicide']
))

print("\n📉 Confusion Matrix:")
cm = confusion_matrix(true_labels, pred_labels)
print(f"                 Predicted")
print(f"                 Non-Suicide  Suicide")
print(f"Actual Non-Suicide   {cm[0][0]:6d}      {cm[0][1]:6d}")
print(f"       Suicide       {cm[1][0]:6d}      {cm[1][1]:6d}")

# Step 8: Save Model
print("\n💾 Saving model and tokenizer...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# Save metrics
metrics = {
    "accuracy": float(accuracy),
    "model": MODEL_NAME,
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "learning_rate": LEARNING_RATE,
    "train_samples": len(train_df),
    "val_samples": len(val_df),
    "test_samples": len(test_df)
}

import json
with open(f"{OUTPUT_DIR}/metrics.json", 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\n✅ Model saved to: {OUTPUT_DIR}")

# Step 9: Test with Sample Messages
print("\n" + "="*70)
print("🧪 Testing with Sample Messages")
print("="*70)

test_messages = [
    "I'm so happy today! Everything is going great!",
    "I feel really sad and lonely right now.",
    "I feel hopeless and worthless. I can't go on anymore.",
    "I want to kill myself",
    "Everything is wonderful!"
]

model.eval()
model.to(device)

for msg in test_messages:
    inputs = tokenizer(msg, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)
        prediction = torch.argmax(probs, dim=-1).item()
        confidence = probs[0][prediction].item()

    label = "CRISIS" if prediction == 1 else "NO CRISIS"
    print(f"\n'{msg}'")
    print(f"  → {label} (confidence: {confidence*100:.1f}%)")

print("\n" + "="*70)
print("✅ Training Complete!")
print("="*70)
print(f"\nModel location: {OUTPUT_DIR}")
print("\nNext steps:")
print("1. Test the model: python test_crisis_debug.py")
print("2. Run full pipeline: python test_ml_integration.py")
print("3. Start API: uvicorn app.main:app --reload")
