
from typing import Annotated, Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from churn.config import TARGET_ALIASES, TARGET_COLUMN
from churn.logger import get_logger

logger = get_logger(__name__)

YesNo = Literal["Yes", "No"]
NonNegFloat = Annotated[float, Field(ge=0)]
NonNegInt = Annotated[int, Field(ge=0)]

MAX_REPORTED_ERRORS = 20


class ChurnRecord(BaseModel):
    """Uma linha do dataset bruto de churn."""

    model_config = ConfigDict(extra="ignore")

    CustomerID: int
    Churn: YesNo

    # Uso e faturamento (podem vir ausentes no dataset bruto).
    MonthlyRevenue: float | None
    MonthlyMinutes: NonNegFloat | None
    TotalRecurringCharge: float | None
    DirectorAssistedCalls: NonNegFloat | None
    OverageMinutes: NonNegFloat | None
    RoamingCalls: NonNegFloat | None
    PercChangeMinutes: float | None
    PercChangeRevenues: float | None

    # Chamadas.
    DroppedCalls: NonNegFloat
    BlockedCalls: NonNegFloat
    UnansweredCalls: NonNegFloat
    CustomerCareCalls: NonNegFloat
    ThreewayCalls: NonNegFloat
    ReceivedCalls: NonNegFloat
    OutboundCalls: NonNegFloat
    InboundCalls: NonNegFloat
    PeakCallsInOut: NonNegFloat
    OffPeakCallsInOut: NonNegFloat
    DroppedBlockedCalls: NonNegFloat
    CallForwardingCalls: NonNegFloat
    CallWaitingCalls: NonNegFloat

    # Conta e aparelhos.
    MonthsInService: NonNegInt
    UniqueSubs: NonNegInt
    ActiveSubs: NonNegInt
    ServiceArea: str | None
    Handsets: NonNegFloat | None
    HandsetModels: NonNegFloat | None
    CurrentEquipmentDays: float | None
    AgeHH1: NonNegFloat | None
    AgeHH2: NonNegFloat | None

    # Perfil do cliente.
    ChildrenInHH: YesNo
    HandsetRefurbished: YesNo
    HandsetWebCapable: YesNo
    TruckOwner: YesNo
    RVOwner: YesNo
    Homeownership: Literal["Known", "Unknown"]
    BuysViaMailOrder: YesNo
    RespondsToMailOffers: YesNo
    OptOutMailings: YesNo
    NonUSTravel: YesNo
    OwnsComputer: YesNo
    HasCreditCard: YesNo
    RetentionCalls: NonNegInt
    RetentionOffersAccepted: NonNegInt
    NewCellphoneUser: YesNo
    NotNewCellphoneUser: YesNo
    ReferralsMadeBySubscriber: NonNegInt
    IncomeGroup: Annotated[int, Field(ge=0, le=9)]
    OwnsMotorcycle: YesNo
    AdjustmentsToCreditRating: NonNegInt
    HandsetPrice: str
    MadeCallToRetentionTeam: YesNo
    CreditRating: Literal[
        "1-Highest", "2-High", "3-Good", "4-Medium", "5-Low", "6-VeryLow", "7-Lowest"
    ]
    PrizmCode: Literal["Other", "Rural", "Suburban", "Town"]
    Occupation: Literal[
        "Clerical", "Crafts", "Homemaker", "Other", "Professional", "Retired", "Self", "Student"
    ]
    MaritalStatus: Literal["Yes", "No", "Unknown"]


CHURN_RECORDS_ADAPTER = TypeAdapter(list[ChurnRecord])


def _format_errors(error: ValidationError, index: pd.Index) -> str:
    """Resume os erros de validação indicando a linha original do DataFrame."""

    errors = error.errors()
    lines = []
    for err in errors[:MAX_REPORTED_ERRORS]:
        position, *field = err["loc"]
        column = ".".join(map(str, field))
        lines.append(f"linha {index[position]}, coluna {column!r}: {err['msg']} (valor={err.get('input')!r})")
    if len(errors) > MAX_REPORTED_ERRORS:
        lines.append(f"... e mais {len(errors) - MAX_REPORTED_ERRORS} erros")
    return f"{len(errors)} erros de validação no dataset bruto:\n" + "\n".join(lines)


def validate_raw_churn_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Valida o dataset bruto aceitando aliases conhecidos da coluna alvo."""

    target_column = next((column for column in TARGET_ALIASES if column in df.columns), None)
    if target_column is None:
        logger.error(f"Coluna alvo ausente. Use uma destas colunas: {TARGET_ALIASES}")
        raise ValueError(f"Coluna alvo ausente. Use uma destas colunas: {TARGET_ALIASES}")
    normalized = df.rename(columns={target_column: TARGET_COLUMN})

    missing = [name for name in ChurnRecord.model_fields if name not in normalized.columns]
    if missing:
        logger.error(f"Colunas ausentes no dataset bruto: {missing}")
        raise ValueError(f"Colunas ausentes no dataset bruto: {missing}")

    # Pydantic não entende NaN como ausente; converte para None antes de validar.
    records = normalized.astype(object).where(normalized.notna(), None).to_dict(orient="records")
    try:
        validated = CHURN_RECORDS_ADAPTER.validate_python(records)
    except ValidationError as error:
        message = _format_errors(error, normalized.index)
        logger.error(message)
        raise ValueError(message) from error

    logger.info(f"Dataset bruto validado com sucesso: {len(validated)} linhas.")
    return pd.DataFrame(
        [record.model_dump() for record in validated],
        index=normalized.index,
        columns=list(ChurnRecord.model_fields),
    )
