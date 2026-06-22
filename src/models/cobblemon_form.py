
from pydantic import BaseModel

from consts import BASE_FORM


class BaseStats(BaseModel):
    hp: int | None = None
    attack: int | None = None
    defence: int | None = None
    special_attack: int | None = None
    special_defence: int | None = None
    speed: int | None = None

class EVYield(BaseModel):
    hp: int | None = None
    attack: int | None = None
    defence: int | None = None
    special_attack: int | None = None
    special_defence: int | None = None
    speed: int | None = None

class HitBox(BaseModel):
    width: float | None = None
    height: float | None = None
    fixed: bool | None = None

class Walk(BaseModel):
    walkSpeed: float | str | None = None

class Swim(BaseModel):
    avoidsWater: bool | None = None

class Fly(BaseModel):
    avoidsWater: bool | None = None
    canFly: bool | None = None

class Moving(BaseModel):
    walk: Walk | None = None
    swim: Swim | None = None
    fly: Fly | None = None

class Resting(BaseModel):
    canSleep: bool | None = None
    light: str | int | None = None
    times: list[str] | None = None
    drowsyChance: float | None = None
    rouseChance: float | None = None

class PokemonLeader(BaseModel):
    pokemon: str | None = None
    tier: int | None = None


class Herd(BaseModel):
      maxSize: str | None = None
      toleratedLeaders: list[PokemonLeader] | None = None

class Combat(BaseModel):
    willDefendSelf: bool | None = None
    willDefendOwner: bool | None = None
    willFlee: bool | None = None

class Behaviour(BaseModel):
    moving: Moving | None = None
    resting: Resting | None = None
    herd: Herd | None = None
    combat: Combat | None = None

class Item(BaseModel):
    item: str | None = None
    quantityRange: str | None = None
    percentage: float | None = None

class Drops(BaseModel):
    amount: int | None = None
    entries: list[Item]    

class EvolutionRequirement(BaseModel):
    variant: str | None = None
    minLevel: int | None = None

class RideSound(BaseModel):
    muffleEnabled: bool | None = None
    pitchExpr: str | None = None
    playForNonPassengers: bool | None = None
    soundLocation: str | None = None
    volumeExpr: str | None = None

class RideStats(BaseModel):
    ACCELERATION: str | None = None
    JUMP: str | None = None
    SKILL: str | None = None
    SPEED: str | None = None
    STAMINA: str | None = None

class SingleRidingBehavior(BaseModel):
    key: str | None = None
    rideSounds: list[RideSound] | None = None
    stats: RideStats | None = None

class RidingBehaviors(BaseModel):
    LAND: SingleRidingBehavior | None = None
    AIR: SingleRidingBehavior | None = None
    WATER: SingleRidingBehavior | None = None

class Riding(BaseModel):
    behaviours: RidingBehaviors | None = None

class Evolution(BaseModel):
    id: str | None = None
    variant: str | None = None
    result: str | None = None
    consumeHeldItem: bool | None = None
    learnableMoves: list[str] | None = None
    requirements: list[EvolutionRequirement] | None = None

class CobblemonForm(BaseModel):
    implemented: bool | None = None
    nationalPokedexNumber: int | None = None
    name: str | None = None
    primaryType: str | None = None
    secondaryType: str | None = None
    maleRatio: float | None = None
    height: float | None = None
    weight: float | None = None
    pokedex: list[str] | None = None
    labels: list[str] | None = None
    aspects: list[str] | None = None
    abilities: list[str] | None = None
    eggGroups: list[str] | None = None
    baseStats: BaseStats | None = None
    evYield: EVYield | None = None
    baseExperienceYield: int | None = None
    experienceGroup: str | None = None
    catchRate: int | None = None
    eggCycles: int | None = None
    baseFriendship: int | None = None
    baseScale: float | None = None
    hitbox: HitBox | None = None
    riding: Riding | None = None
    behaviour: Behaviour | None = None
    drops: Drops | None = None
    moves: list[str] | None = None
    preEvolution: str | None = None
    evolutions: list[Evolution] | None = None

class CobblemonSpecies(CobblemonForm):
    forms: list[CobblemonForm] | None = None
    def form_stats(self, form_name: str):
        # if not base form
        if form_name != BASE_FORM:
            for form in self.forms:
                # found form
                if form_name == form.name:
                    # if form has new basestats, return those
                    if form.baseStats:
                        return form.baseStats
                    else:
                        return self.baseStats
        
        return self.baseStats
