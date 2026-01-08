"""
Post-processor HARD : renforce les techniques d’évasion IDS/Firewall
"""

import re

class HardNmapCommandProcessor:

    def process(self, command: str, instruction: str) -> str:
        instruction = instruction.lower()

        command = self._normalize(command)
        command = self._force_scan_type(command)
        command = self._apply_evasion_logic(command, instruction)
        command = self._fix_invalid_flags(command)
        command = self._remove_conflicts(command)

        return command.strip()

    def _normalize(self, command):
        command = re.sub(r'\s+', ' ', command).strip()
        if not command.startswith("nmap"):
            command = f"nmap {command}"
        return command

    def _force_scan_type(self, command):
        # Dataset HARD → quasi toujours SYN scan
        if not any(s in command for s in ['-sS', '-sU', '-sn']):
            parts = command.split()
            parts.insert(1, '-sS')
            return ' '.join(parts)
        return command

    def _apply_evasion_logic(self, command, instruction):
        # Timing
        if any(w in instruction for w in ['stealth', 'covert', 'sneaky', 'low-profile', 'evasion']):
            if not any(t in command for t in ['-T0', '-T1', '-T2']):
                command = self._insert(command, '-T1')

        # Fragmentation
        if 'fragment' in instruction and '-f' not in command:
            command = self._insert(command, '-f')

        # Decoys
        if any(w in instruction for w in ['decoy', 'hide', 'mask']):
            if '-D' not in command:
                command = self._insert(command, '-D RND:10')

        # Spoofing
        if 'spoof' in instruction and '--spoof-mac' not in command and '-S' not in command:
            command = self._insert(command, '--spoof-mac 0')

        # Advanced / maximum evasion
        if any(w in instruction for w in ['maximum', 'advanced', 'all evasion']):
            for flag in ['-f', '-T0', '--data-length 25']:
                if flag not in command:
                    command = self._insert(command, flag)

        return command

    def _fix_invalid_flags(self, command):
        command = command.replace('--f', '-f')
        return command

    def _remove_conflicts(self, command):
        # -sn incompatible avec scan agressif
        if '-sn' in command and any(x in command for x in ['-sS', '-A']):
            command = command.replace('-sn', '')
        return command

    def _insert(self, command, flag):
        parts = command.split()
        for i in range(len(parts)-1, -1, -1):
            if re.search(r'\d+\.\d+\.\d+\.\d+', parts[i]):
                parts.insert(i, flag)
                return ' '.join(parts)
        return f"{command} {flag}"
