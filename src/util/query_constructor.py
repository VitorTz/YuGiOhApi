from typing import Any

class QueryConstructor:

    def __init__(self, table_prefix: str = ""):
        self.__prefix = table_prefix
        self.__queries: list[str] = []
        self.__values: list[Any] = []
    
    def add_comp(self, column_name: str, comp: str, value: Any, table_prefix: str = None) -> None:
        if table_prefix is None:
            table_prefix = self.__prefix
        if value:                        
            self.__queries.append(f"{table_prefix}{column_name} {comp} %s")
            self.__values.append(value)
    
    def add_search_term(self, column_name: str, search_term, table_prefix: str = None) -> None:
        if table_prefix is None:
            table_prefix = self.__prefix
        if search_term:
            self.__queries.append(f"{table_prefix}{column_name} ILIKE %s")
            self.__values.append(f"%{search_term}%")
        
    def add_comp_coalesce(self, queries: list[tuple[str, str, str]], table_prefix: str = None) -> None:                
        for q in queries:
            if q[2]:
                self.add_comp(q[0], q[1], q[2], table_prefix)
                return
    
    def query(self) -> str:
        if self.__values:
            return 'WHERE ' +  ' AND '.join(self.__queries)
        return ""
    
    def values(self) -> tuple[str]:
        if not self.__values:
            return None
        if len(self.__values) == 1:
            return (self.__values[0], )
        return tuple(self.__values)
    
