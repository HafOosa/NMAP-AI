"""
Agent HARD - Génération de commandes complexes avec évasion IDS/Firewall
"""

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from peft import PeftModel
from agents.hard_command_processor import HardNmapCommandProcessor

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

from agents.hard_command_processor import HardNmapCommandProcessor

import os
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from peft import PeftModel

# from Project.agents.hard_command_processor import HardNmapCommandProcessor

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ADAPTER_PATH = os.path.join(PROJECT_ROOT, "models", "hard_models")
BASE_MODEL = "t5-base"

class HardGeneratorAgent:
    """Agent pour scans HARD avec évasion IDS/Firewall"""
    
    def __init__(self):
        print("[INFO] Chargement HardGeneratorAgent...")
        print(f"[INFO] Device = {DEVICE}")
        print(f"[INFO] Dtype = {DTYPE}")

        base_model = T5ForConditionalGeneration.from_pretrained(
            BASE_MODEL,
            torch_dtype=DTYPE,
            low_cpu_mem_usage=True
        )

        base_model = base_model.to(DEVICE)

        self.model = PeftModel.from_pretrained(
            base_model,
            ADAPTER_PATH,
            torch_dtype=DTYPE
        )

        self.model.to(DEVICE)
        self.model.eval()

        # IMPORTANT pour VRAM
        self.model.config.use_cache = False

        self.tokenizer = T5Tokenizer.from_pretrained(BASE_MODEL)
        self.processor = HardNmapCommandProcessor()
    
    def generate(self, instruction: str) -> str:
        inputs = self.tokenizer(
            instruction,
            return_tensors="pt",
            truncation=True,
            max_length=128
        )

        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=64,
                do_sample=False,
                num_beams=1
            )

        raw_command = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return self.processor.process(raw_command, instruction)


    
    def _generate_once(self, input_text: str, max_length: int) -> str:
        """Une itération de génération"""
        
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=256,
            truncation=True,
            padding=True
        ).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=7,
                early_stopping=True,
                no_repeat_ngram_size=2,
                temperature=0.8,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.3
            )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result
    
    def _post_process(self, command: str, instruction: str) -> str:
        """Nettoyer et valider"""
        
        import re
        
        command = command.strip()
        command = re.sub(r'^(generate|refine|advanced|nmap command|:)+\s*', '', command, flags=re.IGNORECASE)
        command = re.sub(r'\s+', ' ', command)
        
        if not command.startswith('nmap'):
            command = f"nmap {command}"
        
        instruction_lower = instruction.lower()
        
        if 'stealth' in instruction_lower or 'covert' in instruction_lower:
            if '-T' not in command:
                command = command.replace('nmap', 'nmap -T1')
        
        if 'fragmentation' in instruction_lower or 'fragment' in instruction_lower:
            if '-f' not in command:
                parts = command.split()
                parts.insert(1, '-f')
                command = ' '.join(parts)
        
        if 'decoy' in instruction_lower and '-D' not in command:
            parts = command.split()
            parts.insert(1, '-D RND:10')
            command = ' '.join(parts)
        
        return command.strip()


if __name__ == "__main__":
    agent = HardGeneratorAgent()
    
    tests = [
        "Stealthy scan with fragmentation on 192.168.1.0/24",
        "Bypass IDS on 10.0.0.0/24 using decoys",
        "Covert UDP scan with spoofing on 172.16.0.0/24",
        "Maximum evasion scan on 192.168.1.1"
    ]
    
    print("\n" + "="*70)
    print("TEST AGENT HARD")
    print("="*70)
    
    for instr in tests:
        print(f"\n📝 {instr}")
        print(f"💻 {agent.generate(instr)}")