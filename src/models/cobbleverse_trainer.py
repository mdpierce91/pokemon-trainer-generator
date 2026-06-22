
from pydantic import BaseModel


class TrainerName(BaseModel):
    literal: str

class CobbleverseAIData(BaseModel):
    moveBias: float | None = None
    switchBias: float | None = None
    statMoveBias: float | None = None
    itemBias: float | None = None
    maxSelectMargin: float | None = None
    canTera: bool | None = None
    teraTarget: str | None = None

class CobbleverseAI(BaseModel):
    type: str
    data: CobbleverseAIData | None = None

class CobbleverseBattleRules(BaseModel):
    maxItemUses: int | None = None

class CobbleverseItem(BaseModel):
    item: str
    quantity: int

class PokemonStats(BaseModel):
    hp: int | None = None
    atk: int | None = None
    spa: int | None = None
    spd: int | None = None
    spe: int | None = None

class PokemonGimicks(BaseModel):
    tera: str | None = None
    teraType: str | None = None

class TeamMember(BaseModel):
    species: str
    form: str | None = None
    gender: str | None = None
    level: int | None = None
    nature: str | None = None
    ability: str | None = None
    moveset: list | None = None
    ivs: PokemonStats | None = None
    evs: PokemonStats | None = None
    heldItem: str | list |  None = None
    gimmicks: PokemonGimicks | None = None


class CobbleverseTrainer(BaseModel):
    name: TrainerName
    identity: str | None = None
    ai: CobbleverseAI
    battleFormat: str
    battleRules: CobbleverseBattleRules | None = None
    bag: list[CobbleverseItem] | None = None
    team: list[TeamMember]

class CobbleverseTrainerFile():
    filename: str
    data: CobbleverseTrainer

    def __init__(self, filename, data):
        self.filename=filename
        self.data=data