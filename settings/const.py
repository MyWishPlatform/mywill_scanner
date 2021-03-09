from enum import Enum


class ContractTypes(Enum):
    # Based on https://app.simplenote.com/p/cbglT1

    LastWill = 0
    LostKey = 1
    DelayedPayment = 2
    Ico = 4
    Token = 5
    NeoToken = 6
    NeoIco = 7
    Airdrop = 8
    InvestmentPool = 9
    EosToken = 10
    EosAccount = 11
    EosIco = 12
    EosAirdrop = 13
    EosTokenStandalone = 14
    TronToken = 15
    TronGameAssets = 16
    TronAirdrop = 17
    TronLostKey = 18
    LostKeyForTokens = 19
    Swaps = 20
    Swaps2 = 21
    WavesSto = 22
    TokenProtector = 23
    BinanceLastWill = 24
    BinanceLostKey = 25
    BinanceDelayedPayment = 26
    BinanceIco = 27
    BinanceToken = 28
    BinanceAirdrop = 29
    BinanceInvestmentPool = 30
    BinanceLostKeyForTokens = 31
    MaticIco = 32
    MaticToken = 33
    MaticAirdrop = 34
