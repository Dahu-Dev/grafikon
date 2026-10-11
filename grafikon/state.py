from .primitives import Attribute, Entity, Layer, UUID



class ModelSpace_LayerTree:
    pass

class ModelSpace:
    def __init__(self,
                 entityList: dict[UUID, Entity],
                 layerTree: ModelSpace_LayerTree
                 ):
        self.entityList = entityList
        self.layerTree = layerTree
        
    def add_entity(self, entity: Entity):
        self.entityList[entity.id] = entity

    def del_entity(self, id: UUID):
        del self.entityList[id]

class Layout:
    pass

class GrafikonState:
    def __init__(self,
                 availableAttributes: dict[str, Attribute],
                 modelSpace: ModelSpace,
                 layouts: dict[str, Layout]
                 ):
        self.availableAttributes = availableAttributes
        self.modelSpace = modelSpace
        self.layouts = layouts

    def add_attribute(self, attribute: Attribute):
        if attribute.name in self.availableAttributes:
            raise KeyError(f"Attribute with name {attribute.name} already exists and cannot be overwritten")
        self.availableAttributes[attribute.name] = attribute

    def del_attribute(self, name: str):
        if name not in self.availableAttributes:
            raise KeyError(f"Attribute with name {name} does not exist")
        del self.availableAttributes[name]
