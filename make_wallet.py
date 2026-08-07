#!/usr/bin/env python3
"""Generates a BIP-39 mnemonic + ETH receive address. No KYC, no paid service.
Dependencies (all free, pure-Python):
    pip install mnemonic ecdsa pycryptodome
Run from a clean venv (do NOT inherit the Hermes agent venv):
    python make_wallet.py
"""
import sys, hmac, hashlib
# NOTE: eth-account/eth-utils pull in pydantic, which has a compiled core that
# mismatches across venvs on this host. We avoid that whole chain by importing
# only `mnemonic`, `ecdsa`, and `Crypto.Hash.keccak` -- none of which need
# pydantic. If six is not found, run:  python -m pip install six ecdsa
from mnemonic import Mnemonic
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import keccak

# 1. BIP-39 mnemonic (12 words, 128-bit entropy)
mnemonic_str = Mnemonic('english').generate(strength=128)
seed = Mnemonic.to_seed(mnemonic_str, passphrase='')

# 2. Minimal BIP-32 derivation (stdlib only)
def h512(k, m): return hmac.new(k, m, hashlib.sha512).digest()

def master(s):
    I = h512(b'Bitcoin seed', s)
    return int.from_bytes(I[:32], 'big'), I[32:]

def ckd(kp, cp, i):
    HARD = 0x80000000; n = SECP256k1.order
    if i >= HARD:
        data = b'\x00' + kp.to_bytes(32, 'big') + i.to_bytes(4, 'big')
    else:
        vk = SigningKey.from_secret(kp.to_bytes(32,'big'), curve=SECP256k1).verifying_key.to_string()
        x = int.from_bytes(vk[:32],'big'); y = int.from_bytes(vk[32:],'big')
        data = (b'\x02' if y%2==0 else b'\x03') + x.to_bytes(32,'big') + i.to_bytes(4,'big')
    I = h512(cp, data)
    return (int.from_bytes(I[:32],'big') + kp) % n, I[32:]

# 3. Derive m/44'/60'/0'/0/0 (canonical Ethereum external-receive path)
H = 0x80000000
k, c = master(seed)
for i in [44|H, 60|H, 0|H, 0, 0]:
    k, c = ckd(k, c, i)

# 4. ETH address = last 20 bytes of keccak256(pubkey)
pub = SigningKey.from_secret(k.to_bytes(32,'big'), curve=SECP256k1).verifying_key.to_string()
kh = keccak.new(digest_bits=256); kh.update(pub)
eth_address = '0x' + kh.hexdigest()[-40:]

print("MNEMONIC      :", mnemonic_str)
print("ETH_ADDRESS   :", eth_address)
print("PRIVKEY (hex) :", k.to_bytes(32,'big').hex())
