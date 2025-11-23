"""
LOCAL MODEL TRAINING FOR EXAM BOT
Train a small Q&A model on your dataset for offline use
Compatible with Raspberry Pi (lightweight approach)
"""

import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    Trainer, 
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import os

# ============================================
# STEP 1: CREATE YOUR TRAINING DATASET
# ============================================

def create_exam_dataset():
    """
    Create a dataset of exam questions and answers
    Format: Question -> Answer pairs
    """
    
    # Sample exam Q&A pairs - EXPAND THIS WITH YOUR OWN DATA
    qa_pairs = [
        {
            "question": "Explain the primary purpose of object-oriented programming",
            "answer": "Object-oriented programming enables code reusability, modularity, and easier maintenance through encapsulation, inheritance, and polymorphism principles."
        },
        {
            "question": "What is object-oriented programming used for",
            "answer": "Object-oriented programming is used to organize code into reusable objects that model real-world entities, making software easier to develop and maintain."
        },
        {
            "question": "Which data structure uses LIFO principle",
            "answer": "A stack data structure uses the LIFO (Last In First Out) principle where the last element added is the first one to be removed."
        },
        {
            "question": "What does LIFO mean in data structures",
            "answer": "LIFO stands for Last In First Out, a principle where the most recently added item is the first to be accessed or removed, commonly used in stack implementations."
        },
        {
            "question": "What does API stand for in software development",
            "answer": "API stands for Application Programming Interface, which allows different software applications to communicate and share data with each other."
        },
        {
            "question": "Explain what an API is",
            "answer": "An API is an Application Programming Interface that defines how software components should interact, enabling different programs to exchange information."
        },
        {
            "question": "What is a database",
            "answer": "A database is an organized collection of structured data stored electronically, designed for efficient storage, retrieval, and management of information."
        },
        {
            "question": "Explain the concept of inheritance in OOP",
            "answer": "Inheritance in object-oriented programming allows a class to inherit properties and methods from a parent class, promoting code reuse and hierarchical relationships."
        },
        {
            "question": "What is a variable in programming",
            "answer": "A variable is a named storage location in memory that holds a value which can change during program execution."
        },
        {
            "question": "What is the difference between a stack and a queue",
            "answer": "A stack uses LIFO (Last In First Out) while a queue uses FIFO (First In First Out) for managing elements."
        },
        {
            "question": "What is encapsulation in programming",
            "answer": "Encapsulation is the bundling of data and methods that operate on that data within a single unit or class, restricting direct access to some components."
        },
        {
            "question": "What is a loop in programming",
            "answer": "A loop is a programming construct that repeats a block of code multiple times until a specified condition is met."
        },
        {
            "question": "What is recursion",
            "answer": "Recursion is a programming technique where a function calls itself to solve a problem by breaking it down into smaller, similar subproblems."
        },
        {
            "question": "What is an algorithm",
            "answer": "An algorithm is a step-by-step procedure or set of rules designed to solve a specific problem or perform a computation."
        },
        {
            "question": "What is the purpose of a constructor",
            "answer": "A constructor is a special method that initializes a newly created object and sets up its initial state when an instance of a class is created."
        }
    ]
    
    # Format for training: "Question: X\nAnswer: Y"
    formatted_data = []
    for qa in qa_pairs:
        text = f"Question: {qa['question']}\nAnswer: {qa['answer']}"
        formatted_data.append({"text": text})
    
    # Save dataset to JSON
    with open("exam_dataset.json", "w") as f:
        json.dump(formatted_data, f, indent=2)
    
    print(f"✅ Created dataset with {len(formatted_data)} examples")
    print(f"📁 Saved to: exam_dataset.json")
    
    return formatted_data

# ============================================
# STEP 2: TRAIN THE MODEL (Lightweight)
# ============================================

def train_small_model():
    """
    Train a tiny model suitable for Raspberry Pi
    Uses DistilGPT2 - only 82MB, fast on CPU
    """
    
    print("\n" + "="*60)
    print("🚀 STARTING MODEL TRAINING")
    print("="*60)
    
    # Load tiny model (perfect for Pi)
    model_name = "distilgpt2"  # Only 82MB!
    print(f"\n📥 Loading base model: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Set padding token
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id
    
    # Load dataset
    print("\n📚 Loading training data...")
    with open("exam_dataset.json", "r") as f:
        data = json.load(f)
    
    dataset = Dataset.from_list(data)
    
    # Tokenize dataset
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=256,
            padding="max_length"
        )
    
    print("🔧 Tokenizing dataset...")
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training configuration (lightweight for Pi)
    training_args = TrainingArguments(
        output_dir="./exam_model",
        num_train_epochs=3,              # Quick training
        per_device_train_batch_size=2,   # Small batch for low RAM
        save_steps=50,
        save_total_limit=2,
        logging_steps=10,
        learning_rate=5e-5,
        warmup_steps=10,
        weight_decay=0.01,
        fp16=False,                      # No GPU needed
        push_to_hub=False,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal LM, not masked
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Train!
    print("\n🏋️ Training model (this may take 10-30 minutes on Pi)...")
    trainer.train()
    
    # Save the model
    print("\n💾 Saving trained model...")
    model.save_pretrained("./exam_model_final")
    tokenizer.save_pretrained("./exam_model_final")
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"📁 Model saved to: ./exam_model_final")
    print(f"📊 Model size: ~82MB")
    print(f"💡 Ready to use in your exam bot!")

# ============================================
# STEP 3: TEST THE TRAINED MODEL
# ============================================

def test_trained_model():
    """
    Test your trained model with sample questions
    """
    print("\n" + "="*60)
    print("🧪 TESTING TRAINED MODEL")
    print("="*60)
    
    # Load trained model
    print("\n📥 Loading your trained model...")
    tokenizer = AutoTokenizer.from_pretrained("./exam_model_final")
    model = AutoModelForCausalLM.from_pretrained("./exam_model_final")
    
    # Test questions
    test_questions = [
        "Question: What does API stand for in software development",
        "Question: Which data structure uses LIFO principle",
        "Question: Explain the primary purpose of object-oriented programming"
    ]
    
    print("\n📝 Generating answers...\n")
    
    for question in test_questions:
        print(f"❓ {question[10:]}")  # Remove "Question: " prefix
        
        inputs = tokenizer(question + "\nAnswer:", return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = full_text.split("Answer:")[-1].strip()
        
        print(f"💬 {answer}\n")

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print("\n" + "="*60)
    print("🎓 EXAM BOT MODEL TRAINER")
    print("="*60)
    print("\nThis script will:")
    print("1. Create a training dataset (exam_dataset.json)")
    print("2. Train a small model (DistilGPT2 - 82MB)")
    print("3. Test the trained model")
    print("\n⚠️  Training may take 10-30 minutes on Raspberry Pi")
    print("="*60)
    
    choice = input("\nProceed? [y/n]: ").lower().strip()
    
    if choice != 'y':
        print("Cancelled.")
        return
    
    # Step 1: Create dataset
    print("\n[STEP 1/3] Creating dataset...")
    create_exam_dataset()
    
    # Step 2: Train model
    print("\n[STEP 2/3] Training model...")
    try:
        train_small_model()
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        print("\nIf you see memory errors, try:")
        print("  - Close other programs")
        print("  - Reduce batch size in training_args")
        print("  - Use fewer training examples")
        return
    
    # Step 3: Test model
    print("\n[STEP 3/3] Testing model...")
    test_trained_model()
    
    print("\n" + "="*60)
    print("✅ ALL DONE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Add more Q&A pairs to exam_dataset.json")
    print("2. Re-run training to improve the model")
    print("3. Use ./exam_model_final in your exam bot")
    print("="*60)

if __name__ == "__main__":
    # Check dependencies
    try:
        import transformers
        import datasets
    except ImportError:
        print("\n❌ Missing dependencies!")
        print("\nInstall with:")
        print("  pip install transformers datasets torch")
        exit(1)
    
    main()