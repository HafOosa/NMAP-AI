"""
Agent MEDIUM optimisé avec :
- Meilleur prompt engineering
- Post-processing intelligent
- Gestion d'erreurs
- Intégration du NmapCommandProcessor avancé
"""

import os
import sys
import torch
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration
from peft import PeftModel

# === Import processor intelligent ===
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.command_processor import NmapCommandProcessor


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ADAPTER_PATH = os.path.join(PROJECT_ROOT, "models", "medium_models")
BASE_MODEL = "t5-small"


class MediumGeneratorAgent:
    def __init__(self):
        print("[INFO] Chargement MediumGeneratorAgent...")

        # Tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(BASE_MODEL, legacy=False)

        # Modèle base
        base_model = T5ForConditionalGeneration.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )

        # Charger les poids LoRA
        self.model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
        self.model.eval()

        # === NOUVEAU : ajouter le processeur intelligent ===
        self.processor = NmapCommandProcessor()

        print("[OK] MediumGeneratorAgent prêt !")

    def generate(self, instruction: str, max_length: int = 128) -> str:
        """
        Générer commande Nmap à partir d'une instruction NLP.
        """

        # Format demandé lors du training
        input_text = f"translate to nmap: {instruction}"

        # Tokenisation
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=256,
            truncation=True,
            padding=True
        ).to(self.model.device)

        # Génération
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=5,
                early_stopping=True,
                no_repeat_ngram_size=2,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2
            )

        # Décodage brut
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Post-processing niveau 1 (nettoyage)
        result = self._post_process(result, instruction)

        # === NOUVEAU : Post-processing avancé (processor intelligent) ===
        result = self.processor.process(result, instruction)

        return result

    def _post_process(self, command: str, original_instruction: str) -> str:
        """
        Nettoyage et validation de la commande générée.
        """

        # Trim
        command = command.strip()

        # Supprimer un éventuel préfixe
        command = re.sub(r'^translate to nmap:\s*', '', command, flags=re.IGNORECASE)

        # S'assurer que la commande commence par 'nmap'
        if not command.startswith("nmap"):
            command = f"nmap {command}"

        # Nettoyer espaces multiples
        command = re.sub(r"\s+", " ", command)

        # Extraire cible IP/réseau depuis l'instruction utilisateur
        target_match = re.search(r"(\d+\.\d+\.\d+\.\d+(?:/\d+)?)", original_instruction)

        # Ajouter le target s'il manque
        if target_match and target_match.group(1) not in command:
            command = f"{command} {target_match.group(1)}"

        return command.strip()

    def generate_batch(self, instructions: list) -> list:
        """Générer plusieurs commandes."""
        return [self.generate(instr) for instr in instructions]


# ====================================================================
# Test local
# ====================================================================

if __name__ == "__main__":
    agent = MediumGeneratorAgent()

    tests = [
        "Scan port 22 on 192.168.1.0/24",
        "Detect OS version on 10.0.0.1",
        "Check all ports with service detection on 172.16.0.0/24",
        "Run vuln scripts on 192.168.1.100",
        "Quick ping scan on the network 10.10.10.0/24"
    ]

    print("\n" + "="*70)
    print("TEST AGENT MEDIUM")
    print("="*70)

    for instruction in tests:
        print(f"\n📝 {instruction}")
        print(f"💻 {agent.generate(instruction)}")
