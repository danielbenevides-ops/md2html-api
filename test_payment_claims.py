from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch
import urllib.error

import payment_claims


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class PaymentClaimVerificationTests(unittest.TestCase):
    def test_sums_only_outputs_to_configured_wallet(self):
        txid = "c" * 64
        wallet = "Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG"
        payload = {
            "hash": txid,
            "confirmations": 3,
            "outputs": [
                {"addresses": [wallet], "value": 60_000},
                {"addresses": ["Lother"], "value": 999_999},
                {"addresses": [wallet], "value": 40_000},
            ],
        }
        with patch("payment_claims.urllib.request.urlopen", return_value=_Response(payload)):
            verified = payment_claims.verify_ltc_transaction(txid, wallet)

        self.assertEqual(verified["txid"], txid)
        self.assertEqual(verified["value_satoshis"], 100_000)
        self.assertEqual(verified["confirmations"], 3)

    def test_rejects_mismatched_transaction_hash(self):
        txid = "d" * 64
        payload = {"hash": "e" * 64, "confirmations": 2, "outputs": []}
        with patch("payment_claims.urllib.request.urlopen", return_value=_Response(payload)):
            with self.assertRaises(payment_claims.VerificationError) as raised:
                payment_claims.verify_ltc_transaction(txid, "Lwallet")
        self.assertEqual(raised.exception.status, 502)

    def test_maps_not_found_without_leaking_provider_body(self):
        txid = "f" * 64
        error = urllib.error.HTTPError("url", 404, "not found", {}, io.BytesIO(b"provider detail"))
        with patch("payment_claims.urllib.request.urlopen", side_effect=error):
            with self.assertRaises(payment_claims.VerificationError) as raised:
                payment_claims.verify_ltc_transaction(txid, "Lwallet")
        self.assertEqual(raised.exception.status, 404)
        self.assertEqual(raised.exception.message, "Litecoin transaction not found")


if __name__ == "__main__":
    unittest.main()
class BlockchairFallbackTests(unittest.TestCase):
    def test_fallback_sums_outputs_to_wallet(self):
        txid = "a" * 64
        wallet = "Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG"
        data = {"data": {txid: {"confirmations": 2, "outputs": [
            {"recipient": wallet, "value": 100000},
            {"recipient": "Lother", "value": 50000},
        ]}}}
        with patch("payment_claims.urllib.request.urlopen", return_value=_Response(data)):
            verified = payment_claims._verify_via_blockchair(txid, wallet)
        self.assertEqual(verified["value_satoshis"], 100000)
        self.assertEqual(verified["confirmations"], 2)

    def test_fallback_raises_404_when_unknown(self):
        txid = "b" * 64
        data = {"data": {}}
        with patch("payment_claims.urllib.request.urlopen", return_value=_Response(data)):
            with self.assertRaises(payment_claims.VerificationError) as raised:
                payment_claims._verify_via_blockchair(txid, "Lwallet")
        self.assertEqual(raised.exception.status, 404)

    def test_blockcypher_404_falls_back(self):
        txid = "c" * 64
        wallet = "Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG"
        blockchair = {"data": {txid: {"confirmations": 1, "outputs": [
            {"recipient": wallet, "value": 100000}]}}}
        error = urllib.error.HTTPError("url", 404, "nf", {}, io.BytesIO(b"x"))
        def side_effect(req, timeout=0):
            if "blockcypher" in getattr(req, "full_url", ""):
                raise error
            return _Response(blockchair)
        with patch("payment_claims.urllib.request.urlopen", side_effect=side_effect):
            verified = payment_claims.verify_ltc_transaction(txid, wallet)
        self.assertEqual(verified["value_satoshis"], 100000)
