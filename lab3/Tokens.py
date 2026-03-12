from dataclasses import dataclass
from enum import StrEnum, auto
from typing import override


class TokenKind(StrEnum):
    LPAR = "L_PAR"
    RPAR = "R_PAR"
    identToken = "IDENT"
    intigerToken = "INTIGER"
    reservedToken = "RESERVED"


@dataclass
class Token:
    kind: TokenKind
    value: str | None = None

    def __str__(self):
        return f"{self.kind}('{self.value}')" if self.value else f"{self.kind}"


@dataclass(kw_only=True)
class ReservedToken(Token):

    value: str
    kind: TokenKind = TokenKind.identToken

    @override
    def __str__(self) -> str:
        return f"{self.value.upper()}"

    def __eq__(self, other):
        return str(self.value) == other
