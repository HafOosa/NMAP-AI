"""
FINE-TUNING OPTIMISÉ avec :
- Hyperparamètres corrects
- Early stopping
- Meilleur format de données
- Logging détaillé
"""

import json
import torch
from datasets import Dataset
from transformers import (
    T5Tokenizer, 
    T5ForConditionalGeneration,
    DataCollatorForSeq2Seq,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback
)
from peft import LoraConfig, get_peft_model, TaskType

# Paths
TRAIN_DATA = "data/t5_balanced_train.json"
VAL_DATA = "data/t5_balanced_val.json"

OUTPUT_DIR = "models/medium_models"

# Hyperparams OPTIMISÉS
LEARNING_RATE = 2e-4  # Plus bas = meilleur
BATCH_SIZE = 8  # Augmenté si GPU permet
NUM_EPOCHS = 5  # Plus d'epochs
MAX_INPUT_LENGTH = 256  # Augmenté pour instructions longues
MAX_TARGET_LENGTH = 128

print("="*70)
print("🚀 FINE-TUNING T5 MEDIUM (VERSION OPTIMISÉE)")
print("="*70)

# 1. Charger tokenizer
print("\n[1/6] Chargement du tokenizer...")
tokenizer = T5Tokenizer.from_pretrained("t5-small", legacy=False)

# 2. Charger modèle base
print("[2/6] Chargement du modèle T5-small...")
model = T5ForConditionalGeneration.from_pretrained(
    "t5-small",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

# 3. Appliquer LoRA
print("[3/6] Application de LoRA...")
lora_config = LoraConfig(
    task_type=TaskType.SEQ_2_SEQ_LM,
    r=16,  # Augmenté de 8 à 16
    lora_alpha=32,  # Augmenté proportionnellement
    lora_dropout=0.1,
    target_modules=["q", "v"],  # Attention layers
    inference_mode=False
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# 4. Charger datasets
print("[4/6] Chargement des datasets...")

def load_json_dataset(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return Dataset.from_list(data)

train_dataset = load_json_dataset(TRAIN_DATA)
val_dataset = load_json_dataset(VAL_DATA)

print(f"   Train: {len(train_dataset)} exemples")
print(f"   Val:   {len(val_dataset)} exemples")

# 5. Tokenization
print("[5/6] Tokenization...")

def preprocess_function(examples):
    """Tokenize input et target"""
    
    # Tokenize inputs
    model_inputs = tokenizer(
        examples['input_text'],
        max_length=MAX_INPUT_LENGTH,
        padding='max_length',
        truncation=True,
        return_tensors=None  # Important pour Dataset
    )
    
    # Tokenize targets
    labels = tokenizer(
        examples['target_text'],
        max_length=MAX_TARGET_LENGTH,
        padding='max_length',
        truncation=True,
        return_tensors=None
    )
    
    # Remplacer padding par -100 (ignore dans loss)
    labels_input_ids = labels['input_ids']
    labels_input_ids = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label]
        for label in labels_input_ids
    ]
    
    model_inputs['labels'] = labels_input_ids
    
    return model_inputs

# Appliquer tokenization
tokenized_train = train_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=train_dataset.column_names
)

tokenized_val = val_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=val_dataset.column_names
)

# Data collator
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True
)

# 6. Training arguments OPTIMISÉS
print("[6/6] Configuration du training...")

# ... (tout le code reste pareil jusqu'à TrainingArguments)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    
    # Epochs & Batch
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    
    # Learning rate
    learning_rate=LEARNING_RATE,
    warmup_steps=500,
    weight_decay=0.01,
    
    # Evaluation
    eval_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=500,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    
    # Logging
    logging_dir=f"{OUTPUT_DIR}/logs",
    logging_steps=100,
    report_to="none",
    
    # Performance
    fp16=torch.cuda.is_available(),
    dataloader_num_workers=0,  # ← CHANGÉ DE 4 À 0 (désactive multiprocessing)
    gradient_accumulation_steps=2,
    
    # Early stopping
    greater_is_better=False,
)

# ... (reste du code)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    data_collator=data_collator,
    tokenizer=tokenizer,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
)

# TRAIN !
print("\n" + "="*70)
print("🔥 DÉBUT DU TRAINING")
print("="*70)

trainer.train()

# Sauvegarder
print("\n💾 Sauvegarde du modèle...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"\n✅ TERMINÉ ! Modèle sauvegardé dans {OUTPUT_DIR}")
print("\n📊 Pour tester : python tests/test_medium.py")