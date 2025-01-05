from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)
from datasets import load_dataset
from pathlib import Path

# Specify the path to the last checkpoint
last_checkpoint = "./output/checkpoint-7000"

# Verify if the checkpoint path exists
checkpoint_path = Path(last_checkpoint)
if not checkpoint_path.exists():
    raise ValueError(f"Checkpoint path does not exist: {last_checkpoint}")

# Step 1: Load Amazon Reviews Dataset (Subset)
print("Loading Amazon Polarity dataset...")
dataset = load_dataset("amazon_polarity")

# Take a smaller subset for faster fine-tuning
train_dataset = dataset['train'].shuffle(seed=42).select(range(10000))  # 10,000 samples for training
test_dataset = dataset['test'].shuffle(seed=42).select(range(2000))    # 2,000 samples for testing

print(f"Train dataset size: {len(train_dataset)}")
print(f"Test dataset size: {len(test_dataset)}")

# Step 2: Load Pretrained Model and Tokenizer
model_name = "allenai/longformer-base-4096"  # Longformer model
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load model from checkpoint if the directory exists
try:
    print(f"Loading model from checkpoint: {last_checkpoint}")
    model = AutoModelForSequenceClassification.from_pretrained(last_checkpoint)
except Exception as e:
    print(f"Error loading checkpoint: {e}")
    print("Falling back to base pretrained model...")
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Step 3: Tokenize Data with Fixed Length
def tokenize_function(examples):
    return tokenizer(
        examples["content"], 
        padding="max_length",  # Pad to max_length
        truncation=True,       # Truncate if longer
        max_length=512         # Explicit max length
    )

print("Tokenizing datasets...")
tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_test = test_dataset.map(tokenize_function, batched=True)

# Step 4: Handle Padding Dynamically with DataCollator
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Step 5: Set Up Training Arguments with Frequent Checkpoints
training_args = TrainingArguments(
    output_dir="./output",           # Directory for checkpoints
    evaluation_strategy="steps",     # Evaluate at regular steps
    save_strategy="steps",           # Save checkpoints every few steps
    save_steps=500,                  # Save a checkpoint every 500 steps
    eval_steps=500,                  # Evaluate every 500 steps
    logging_steps=100,               # Log metrics every 100 steps
    save_total_limit=3,              # Keep only the 3 latest checkpoints
    num_train_epochs=3,              # Total epochs
    per_device_train_batch_size=4,   # Adjust batch size based on hardware
    per_device_eval_batch_size=4,    # Evaluation batch size
    learning_rate=2e-5,              # Learning rate
    weight_decay=0.01,               # Regularization
    load_best_model_at_end=True,     # Load best model at the end
    report_to="none"                 # Disable W&B logging (optional)
)

# Step 6: Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    data_collator=data_collator,  # Dynamic padding
)

# Step 7: Resume Training
print("Resuming training from checkpoint...")
trainer.train(resume_from_checkpoint=last_checkpoint)

# Step 8: Save the Final Trained Model
output_dir = "~/TrainedModel"
print(f"Saving final model to {output_dir}...")
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

print(f"Resumed training complete. Final model saved to '{output_dir}'.")
