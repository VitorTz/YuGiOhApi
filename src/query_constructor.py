from typing import Any
from enum import Enum, auto


class Comparation(Enum):

    LESS = auto()
    LESS_OR_EQUAL = auto()

    GREATER = auto()
    GREATER_OR_EQUAL = auto()

    EQUAL = auto()
    NOT_EQUAL = auto()

    SEARCH_TERM = auto()


COMP_TO_STR: dict[Comparation, str] = {
    Comparation.LESS: "<",
    Comparation.LESS_OR_EQUAL: "<=",
    
    Comparation.GREATER: ">",
    Comparation.GREATER: ">=",

    Comparation.EQUAL: "=",
    Comparation.NOT_EQUAL: "!=",

    Comparation.SEARCH_TERM: "ILIKE"
}
    

class QueryComp:

    def __init__(self, column: str, comp: Comparation, value: Any):
        self.__column = column
        self.__comp = comp
        self.__value = value

    @property
    def is_valid_query(self) -> bool:
        return self.__value is not None
        
    def query(self, prefix: str = "") -> str:
        return f"{prefix}{self.__column} {COMP_TO_STR[self.__comp]} %s"
    
    def value(self) -> Any:
        if self.__comp == Comparation.SEARCH_TERM:
            return f"%{self.__value}%"
        return self.__value


class QueryConstructor:

    def __init__(self, table_prefix: str = "", logic_gate: str = 'AND'):
        self.__prefix = table_prefix
        self.__logic_gate = logic_gate
        self.__queries: list[str] = []
        self.__values: list[Any] = []    

    @property
    def is_empty(self) -> bool:
        return not self.__values
     
    def add(self, comp: QueryComp, prefix: str = None) -> None:
        if prefix is None: prefix = self.__prefix
        if comp.is_valid_query:
            self.__queries.append(comp.query(prefix))
            self.__values.append(comp.value())

    def add_coalesce(self, queries: list[QueryComp], prefix: str = None) -> None:                
        for q in queries:
            if q.is_valid_query:
                self.add(q, prefix)
    
    def query(self) -> str:
        if self.__values:
            return 'WHERE ' +  f" {self.__logic_gate} ".join(self.__queries)
        return ""
    
    def values(self) -> tuple[str] | None:
        if not self.__values:
            return None
        if len(self.__values) == 1:
            return (self.__values[0], )
        return tuple(self.__values)
    