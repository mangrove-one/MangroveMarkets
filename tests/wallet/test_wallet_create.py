"""Tests for wallet creation."""
from src.wallet import service


class DummyWallet:
    def __init__(self, seed_phrase: str | None = None) -> None:
        self.classic_address = "rTestAddress"
        self.seed = "sTestSecret"
        if seed_phrase is not None:
            self.seed_phrase = seed_phrase


def test_create_wallet_includes_secret_and_warnings(monkeypatch):
    calls: dict[str, object] = {}

    def fake_generate_faucet_wallet(client, debug=False):
        calls["debug"] = debug
        return DummyWallet(seed_phrase="twelve word phrase")

    monkeypatch.setattr(service, "generate_faucet_wallet", fake_generate_faucet_wallet)

    response = service.create_wallet(network="testnet")

    assert response["address"] == "rTestAddress"
    assert response["secret"] == "sTestSecret"
    assert response["seed_phrase"] == "twelve word phrase"
    assert response["is_funded"] is True
    assert calls["debug"] is False
    assert any("not be stored" in warning.lower() for warning in response["warnings"])


def test_create_wallet_handles_missing_seed_phrase(monkeypatch):
    def fake_generate_faucet_wallet(client, debug=False):
        return DummyWallet()

    monkeypatch.setattr(service, "generate_faucet_wallet", fake_generate_faucet_wallet)

    response = service.create_wallet(network="testnet")

    assert response["seed_phrase"] is None
