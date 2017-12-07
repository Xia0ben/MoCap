import bpy
import bpy.app
#---------------------------------------Observer--------------------------------------------------------------------------------------
#list of all the observers.
observers = []
#This is to function to call in your scripts. use it to have your function called everytime an object property changes.
#object : Object to watch,
#property : property to be wathed.
#function to execute every time the property of the given object changes.
#function will be given this parameters :
#    object : the object.
#    value : new value of the property
#    old : old value of the property. 
#    frame : current frame.
def observe(object, property, function):
    observers.append(Observer(object,property,function))

#Called at every frame. This will call the function that are listening.
def frameUpdate(frame):
    print("hello")
    for observer in observers:
        observer.update(frame)
    return 0.0



#Each time we call observe we create an observer object. 
class Observer:
    def __init__(self, object, property, function):
        #if the property object needs deep copy 
        try :
            self.oldValue = object[property].copy()
            self.newValue = object[property].copy()
        #if the property object doesn't need it (and don't have a copy method).
        except AttributeError:
            self.oldValue = object[property]
            self.newValue = object[property]

        self.object = object
        self.property = property
        self.function = function

    #Call the function if the object property changed.    
    def update(self, frame):
        #if the object needs deep copy 
        try :
            self.oldValue = self.newValue.copy()
            self.newValue = getattr(self.object, self.property).copy()
        #if the object doesn't need it (and don't have a copy method).
        except AttributeError:
            self.oldValue = self.newValue
            self.newValue = getattr(self.object, self.property)

        if self.oldValue != self.newValue:
            self.function(object = self.object, value = self.newValue, old = self.oldValue, frame = frame)

