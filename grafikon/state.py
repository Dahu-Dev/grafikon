from functools import wraps
from typing import Callable
from uuid import UUID

from .primitives import Attribute, Entity, Layer

def updates_ui(*args, callbackAttr='ui_callback'):
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], str):
        targetFunc = args[0]
        @wraps(targetFunc)
        def wrapper_func(self, *innerArgs, **innerKwargs):
            result = targetFunc(self, *innerArgs, **innerKwargs)
            callback = getattr(self, callbackAttr, None)
            if callback is not None:
                callback()
            return result
        return wrapper_func

    passAttrs = args
    def decorator_func(targetFunc):
        @wraps(targetFunc)
        def wrapper_func(self, *innerArgs, **innerKwargs):
            result = targetFunc(self, *innerArgs, **innerKwargs)
            callback = getattr(self, callbackAttr, None)
            if callback is not None:
                attrValues = [getattr(self, attr) for attr in passAttrs]
                callback(*attrValues)
            return result
        return wrapper_func
    return decorator_func

class LayerTree:
    def __init__(self, layers: dict[UUID|str, Layer] = {}):
        self.layers = layers
        if self.layers == {}:
            root = Layer(label="0", id="0")
            self.layers[root.id] = root

        self.ui_callback = None

    @updates_ui('tree')
    def add_layer(self, layer: Layer):
        if layer.id in self.layers:
            raise KeyError(f"Layer with UUID {layer.id!r} is already in the layer tree")
        if layer.parent is not None and layer.parent not in self.layers:
            raise ValueError("Attempted to add a layer with a parent that does not exist")
        
        self.layers[layer.id] = layer
        if layer.parent is not None:
            self.layers[self.layers[layer.parent].id].children.append(layer.id)

    @updates_ui('tree')
    def del_layer(self, id: UUID):
        if id not in self.layers:
                    raise KeyError(f"Layer with UUID {id} does not exist")
        del self.layers[id]
        ###NEED TO ADD TO THIS MANAGEMENT OF STRANDED CHILD LAYERS...WILL DO LATER

    def _build_tree(self, layer_id: UUID | str) -> list:
        layer = self.layers[layer_id]
        children = [self._build_tree(child_id) for child_id in layer.children]
        return [layer.id, layer.label, children]

    @property
    def tree(self):
        return self._build_tree("0")


class Model:
    def __init__(self,
                 entityList: dict[UUID, Entity],###might be better just to make these pandas or geopandas objects later for search by any propert as well as intersection search
                 layerTree: LayerTree
                 ):
        self.entityList = entityList
        self.layerTree = layerTree

        # testLayer1 = Layer(label="Test - 1", parent="0")
        # testLayer2 = Layer(label="Test - 2", parent="0")
        
        # testLayer3 = Layer(label="Test - 3", parent=testLayer2.id)
        # self.layerTree.add_layer(testLayer1)
        # self.layerTree.add_layer(testLayer2)
        # self.layerTree.add_layer(testLayer3)
        
    def add_entity(self, entity: Entity):
        self.entityList[entity.id] = entity

    def del_entity(self, id: UUID):
        del self.entityList[id]


class Layout:
    pass

class GrafikonState:
    def __init__(self,
                 availableAttributes: dict[str, Attribute],
                 Model: Model,
                 layouts: dict[str, Layout]
                 ):
        self.availableAttributes = availableAttributes
        self.model = Model
        self.layouts = layouts

    def add_attribute(self, attribute: Attribute):
        if attribute.name in self.availableAttributes:
            raise KeyError(f"Attribute with name {attribute.name} already exists and cannot be overwritten")
        self.availableAttributes[attribute.name] = attribute

    def del_attribute(self, name: str):
        if name not in self.availableAttributes:
            raise KeyError(f"Attribute with name {name} does not exist")
        del self.availableAttributes[name]

    def set_ui_callback(self, visualSpace: str, guiElement: str, callback: Callable):
        if visualSpace == "MODEL":
            spaceObj = self.model
        elif visualSpace in self.layouts:
            spaceObj = self.layouts[visualSpace]
        else:
            raise ValueError(f"Visual space {visualSpace} does not exist, cannot set a callback to it")

        if guiElement == "layer_tree":
            spaceObj.layerTree.ui_callback = callback        
    
    def sync(self):
        if self.model.layerTree.ui_callback is not None:
            self.model.layerTree.ui_callback(self.model.layerTree.tree)
        
