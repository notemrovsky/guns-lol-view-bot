import base64
import hashlib
import itertools
import random
import struct

import blake3


class PowSolver:
    def solve(self, challenge_data):
        timestamp, challenge_hash, salt, token_b64 = challenge_data
        token = base64.urlsafe_b64decode(token_b64 + "==")

        difficulty = token[2]
        positions_unsorted = list(token[3:3 + difficulty])
        positions_sorted = sorted(positions_unsorted)
        target = token[21:80].decode("ascii")
        target_hash = bytes.fromhex(challenge_hash)
        key8 = token[13:21]
        suffix = (salt + str(timestamp)).encode()

        seal = self.brute_force(target, positions_sorted, target_hash, suffix)
        score = self.compute_score(seal, target_hash, salt, timestamp)
        nonce = self.build_nonce(seal, positions_unsorted, difficulty, key8, target_hash, score)
        seal = self.mangle_seal(seal, timestamp, salt)

        return [token_b64, timestamp, challenge_hash, salt, seal, nonce]

    def brute_force(self, target, positions, target_hash, suffix):
        for combo in itertools.product("0123456789abcdef", repeat=len(positions)):
            candidate = list(target)
            for pos, char in zip(positions, combo):
                candidate.insert(pos, char)
            candidate_str = "".join(candidate)
            if hashlib.sha256(candidate_str.encode() + suffix).digest() == target_hash:
                return candidate_str
        raise RuntimeError("no solution found")

    def compute_score(self, seal, challenge_hash_bytes, salt, timestamp):
        target = blake3.blake3(challenge_hash_bytes + salt.encode() + str(timestamp).encode()).digest()
        seal_hash = blake3.blake3(seal.encode()).digest()
        score = 0
        for i in range(32):
            if seal_hash[i] == target[i]:
                score += 8
            else:
                xor = seal_hash[i] ^ target[i]
                clz = 0
                for bit in range(7, -1, -1):
                    if xor & (1 << bit):
                        break
                    clz += 1
                score |= clz
                return score
        return 256

    def build_nonce(self, seal, positions, difficulty, key8, challenge_hash_bytes, score):
        nonce_hex = "".join(seal[p] for p in positions)
        partial = bytes([0x51, difficulty]) + nonce_hex.encode() + struct.pack("<I", score)
        integrity = blake3.blake3(partial + key8 + challenge_hash_bytes).digest()[:8]
        return base64.urlsafe_b64encode(partial + integrity).rstrip(b"=").decode()

    def mangle_seal(self, seal, timestamp, salt):
        pos1 = timestamp % 10
        pos2 = 16 + (timestamp + (ord(salt[-1]) if salt else 48)) % 24
        seal = seal[:pos1] + random.choice("0123456789abcdef") + seal[pos1:]
        seal = seal[:pos2] + random.choice("0123456789abcdef") + seal[pos2:]
        return seal
