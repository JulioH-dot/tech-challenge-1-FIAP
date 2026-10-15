import os
from pathlib import Path

RANDOM_SEED = 42

TARGET_COLUMN = "Churn"
TARGET_ALIASES = ["Churn", "Churn?"]
ID_COLUMNS = ["CustomerID"]

# Permite rodar instalado como pacote, Docker ou diretamente na raiz do projeto.
PROJECT_ROOT = Path(os.getenv("CHURN_PROJECT_ROOT", Path.cwd())).resolve()
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

PREPROCESSOR_PATH = MODELS_DIR / "preprocessor.joblib"
MLP_MODEL_PATH = MODELS_DIR / "churn_mlp.pt"
BASELINE_MODEL_PATH = MODELS_DIR / "baseline_logreg.joblib"

# Colunas categóricas.
CATEGORICAL_COLUMNS = [
    "ChildrenInHH",
    "HandsetRefurbished",
    "HandsetWebCapable",
    "TruckOwner",
    "RVOwner",
    "Homeownership",
    "BuysViaMailOrder",
    "RespondsToMailOffers",
    "OptOutMailings",
    "NonUSTravel",
    "OwnsComputer",
    "HasCreditCard",
    "NewCellphoneUser",
    "NotNewCellphoneUser",
    "OwnsMotorcycle",
    "HandsetPriceUnknown",
    "MadeCallToRetentionTeam",
    "CreditRating",
    "PrizmCode",
    "Occupation",
    "MaritalStatus",
    "ServiceRegion",
]

# Colunas numéricas contínuas/discretas.
NUMERIC_COLUMNS = [
    "MonthlyRevenue",
    "MonthlyMinutes",
    "TotalRecurringCharge",
    "DirectorAssistedCalls",
    "OverageMinutes",
    "RoamingCalls",
    "PercChangeMinutes",
    "PercChangeRevenues",
    "DroppedCalls",
    "BlockedCalls",
    "UnansweredCalls",
    "CustomerCareCalls",
    "ThreewayCalls",
    "ReceivedCalls",
    "OutboundCalls",
    "InboundCalls",
    "PeakCallsInOut",
    "OffPeakCallsInOut",
    "DroppedBlockedCalls",
    "CallForwardingCalls",
    "CallWaitingCalls",
    "MonthsInService",
    "UniqueSubs",
    "ActiveSubs",
    "Handsets",
    "HandsetModels",
    "CurrentEquipmentDays",
    "AgeHH1",
    "AgeHH2",
    "RetentionCalls",
    "RetentionOffersAccepted",
    "ReferralsMadeBySubscriber",
    "IncomeGroup",
    "AdjustmentsToCreditRating",
    "HandsetPrice",
]