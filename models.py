from PySide6.QtCore import (
    QAbstractTableModel,
    Qt, 
    QModelIndex,
    QPersistentModelIndex,
)


class TableModel(QAbstractTableModel):
    def __init__(self, data: dict):
        super().__init__()

        self._data: dict = data
        self._rows: list[str] = list(self._data.keys())
        self._cols: list[str] = list(self._data[0].keys()) 


    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = 0) -> str | None:
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[self._rows[index.row()]][self._cols[index.column()]]
        
        return None


    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._rows)
        
        return 0
    

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._cols)
        
        return 0
    
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = 0) -> str | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._cols[section])
            
            if orientation == Qt.Orientation.Vertical:
                return str(self._rows[section])
            
        return None
