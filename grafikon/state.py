from functools import wraps
from typing import Callable
from uuid import UUID

from .primitives import Attribute, Entity, Layer, Coordinate, Point, Polyline

###!!! Consider adding logger which can then be used to add messages in main GUI also

def updates_ui(*args, callbackAttr='draw'):
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
            self.layers["0"] = Layer(label="0", id="0")

        self.draw = None
        self.active = ["0"]
        self.visible = ["0"]
        self.selected = ["0"]

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
    def tree(self):#add typehint!
        return self._build_tree("0")
        
    def get_current_layer(self, layerMode: str) -> list[str]:
        return {"active":self.active, "selected":self.selected, "visible":self.visible}[layerMode]
        


class Model:
    def __init__(self,
                 entityList: dict[UUID, Entity],###might be better just to make these pandas or geopandas objects later for search by any propert as well as intersection search
                 layerTree: LayerTree
                 ):
        self.entityList = entityList
        self.layerTree = layerTree
        self.draw = None
        
    def add_entity(self, entity: Entity):
        self.entityList[entity.id] = entity

    def del_entity(self, id: UUID):
        del self.entityList[id]

    @updates_ui('visible') #need to change this to the filtered list
    def draw_polyline(self, points: tuple[tuple[float, float, float|None]], layerMode: str):
        # points should be tuple of tuples of x, y, z
        #need to add more stuff here on controling the point and line style, perhaps in an inherrited way
        coords = [Coordinate(x=p[0], y=p[1], z=p[2]) for p in points]
        for current in self.layerTree.get_current_layer(layerMode):
            points = [Point(coordinate=c, layer=current) for c in coords]
            polyline = Polyline(layer=current, points=points)
            self.add_entity(polyline)

    @property
    def visible(self): #need to change this to the filtered list
        return list(self.entityList.values())

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
            spaceObj.layerTree.draw = callback        

        if guiElement == "visual_space_draw":
            spaceObj.draw = callback
    
    def sync(self):
        if self.model.layerTree.draw is not None:
            self.model.layerTree.draw(self.model.layerTree.tree)
        if self.model.draw is not None:
            self.model.draw(self.model.visible)#need to change this to the filtered list
        
