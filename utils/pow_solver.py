import subprocess
import json
import os
import random


class PowSolver:
    def solve(self, challenge_data):
        timestamp, challenge_hash, salt, token = challenge_data

        payload = json.dumps({
            "o09": challenge_hash,
            "d": 5,
            "_org_ts": str(timestamp),
            "_n": salt,
            "_2xa": token,
        })

        result = subprocess.run(
            ["node", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "solve.js"), payload],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(f"solve.js failed: {result.stderr}")

        wasm_result = json.loads(result.stdout)
        seal = self.mangle_seal(wasm_result["seal"], timestamp, salt)

        return [
            token,
            timestamp,
            challenge_hash,
            salt,
            seal,
            wasm_result["_oo"],
        ]

    def mangle_seal(self, seal, timestamp, salt):
        pos1 = timestamp % 10
        pos2 = 16 + (timestamp + (ord(salt[-1]) if salt else 48)) % 24
        seal = seal[:pos1] + random.choice("0123456789abcdef") + seal[pos1:]
        seal = seal[:pos2] + random.choice("0123456789abcdef") + seal[pos2:]
        return seal
