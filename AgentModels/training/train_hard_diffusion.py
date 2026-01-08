"""
Entraîner modèle HARD avec approche diffusion-like (T5-base + LoRA aggressive)
"""

import json
import torch
from datasets import Dataset
from transformers import (
    T5Tokenizer, T5ForConditionalGeneration,
    DataCollatorForSeq2Seq, TrainingArguments, Trainer
)
from peft import LoraConfig, get_peft_model, TaskType

TRAIN_DATA = "data/diffusion_hard_train.json"
VAL_DATA = "data/diffusion_hard_val.json"
OUTPUT_DIR = "models/hard_models"

LEARNING_RATE = 3e-4
BATCH_SIZE = 4
NUM_EPOCHS = 8
MAX_INPUT_LENGTH = 256
MAX_TARGET_LENGTH = 150

def main():
    print("="*70)
    print("🔥 ENTRAÎNEMENT MODÈLE HARD (DIFFUSION-LIKE)")
    print("="*70)
    
    # Tokenizer
    print("\n[1/6] Tokenizer...")
    tokenizer = T5Tokenizer.from_pretrained("t5-base", legacy=False)
    
    # Modèle T5-base (plus grand que t5-small)
    print("[2/6] Modèle T5-base...")
    model = T5ForConditionalGeneration.from_pretrained(
        "t5-base",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    
    # LoRA avec config plus aggressive
    print("[3/6] LoRA config...")
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=32,  # Plus élevé pour complexité
        lora_alpha=64,
        lora_dropout=0.1,
        target_modules=["q", "k", "v", "o"],  # Plus de modules
        inference_mode=False
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Datasets
    print("[4/6] Datasets...")
    
    def load_dataset(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return Dataset.from_list(data)
    
    train_dataset = load_dataset(TRAIN_DATA)
    val_dataset = load_dataset(VAL_DATA)
    
    print(f"   Train: {len(train_dataset)}")
    print(f"   Val:   {len(val_dataset)}")
    
    # Tokenization
    print("[5/6] Tokenization...")
    
    def preprocess(examples):
        inputs = tokenizer(
            examples['input_text'],
            max_length=MAX_INPUT_LENGTH,
            padding='max_length',
            truncation=True,
            return_tensors=None
        )
        
        labels = tokenizer(
            examples['target_text'],
            max_length=MAX_TARGET_LENGTH,
            padding='max_length',
            truncation=True,
            return_tensors=None
        )
        
        labels_ids = [
            [(l if l != tokenizer.pad_token_id else -100) for l in label]
            for label in labels['input_ids']
        ]
        
        inputs['labels'] = labels_ids
        return inputs
    
    tokenized_train = train_dataset.map(preprocess, batched=True, remove_columns=train_dataset.column_names)
    tokenized_val = val_dataset.map(preprocess, batched=True, remove_columns=val_dataset.column_names)
    
    collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, padding=True)
    
    # Training args
    print("[6/6] Configuration...")
    
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        warmup_steps=300,
        weight_decay=0.01,
        eval_strategy="steps",
        eval_steps=300,
        save_strategy="steps",
        save_steps=300,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        logging_steps=50,
        report_to="none",
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=0,  # Windows fix
        gradient_accumulation_steps=4,
        greater_is_better=False
    )
    
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        data_collator=collator,
        processing_class=tokenizer
    )
    
    print("\n" + "="*70)
    print("🔥 DÉBUT TRAINING")
    print("="*70)
    
    trainer.train()
    
    print("\n💾 Sauvegarde...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print(f"\n✅ Modèle HARD sauvegardé dans {OUTPUT_DIR}")
    print("\n📊 Pour tester : python tests/test_hard.py")


if __name__ == "__main__":
    main()