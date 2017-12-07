
    

    
import json
from math import *
import bpy,bmesh
import mathutils
import numpy as np
import copy as c
from bpy.props import *
import http.server
from threading import Thread
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
import time
bl_info = {
    "name": "Plugin de MotionCapture",
    "author": "Arkmut",
    "version": (0, 0, 1),
    "blender": (2, 74, 5),
    "location": "object mode>tools",
    "description": "crée un serveur pour que l'hardware puisse se connecter dessus. Récupère les données de rotation envoyé par les capteurs",
    "warning": "version alpha!!",
    "wiki_url": "",
    "category": "",
}
#thread listening for the posts
#TODO having one thread per sensor?
servThread=None
#init message from broadcast
initMsg="MoCapInit"
#TODO variable keeping the time since last received msg
#TODO one per sensor!!
timeInit=-1
#size between frames
interFrames=1
#time period before storing a new keyframe
timePeriod=1.0/30
#timePeriod=1

#blender variable to store the area where to apply the script
area=None
#list of messages received (for each sensor => matrix)
pileQuaternions={}
#lock when modifying the stack of quaternions and triggering the async function
threadLock = None


#---------------------------------------------------- Server-----------------------------------------------------       
            

def asyncReading(object,value,frame):
    #print("trigger Async: "+value)
    global area
    area.type = 'VIEW_3D'
    pbase=object.pose.bones[value]
    pbase.rotation_mode = 'QUATERNION'
    arm=object.data
    global pileQuaternions
    angles = pileQuaternions[value]
    
    #apply rotation
    pbase.rotation_quaternion = mathutils.Quaternion((angles[0],angles[1],angles[2],angles[3]))
    global timeInit
    global interFrames
    global timePeriod
    #inserting keyframe
    if(time.process_time()-timeInit>=timePeriod):
        #bpy.context.scene.active = bpy.data.scenes["Scene"].(null)
        timeInit=time.process_time()
        #bpy.ops.anim.keyframe_insert_menu(type='__ACTIVE__')
        #pbase.keyframe_insert('location',group="LocRot")
        
        pbase.keyframe_insert(data_path='rotation_quaternion',frame=bpy.context.scene.frame_current+interFrames)
        bpy.context.scene.frame_set(bpy.context.scene.frame_current+interFrames)        
    object["trigger"]=""
def my_handler(scene):
    global pileQuaternions
    if(bpy.data.objects["Armature"]["trigger"]!="" and len(pileQuaternions)>0):
        asyncReading(bpy.data.objects["Armature"],bpy.data.objects["Armature"]["trigger"],scene.frame_current)

class myHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        global initMsg
        if(self.path.contains(initMsg)):
            self._set_headers()
            self.wfile.write(initMsg)
    def do_POST(self):
        #receive the quaternions from the sensors, then distribute it to the right bone
        
        #length of data
        length = int(self.headers['Content-Length'])
        #data received
        data =self.rfile.read(length).decode('UTF-8')
        #print("receiving msg:" +data)
        #data deserialised (with json)
        sensorData=json.loads(data)
        #angles is a matrix of size 1*4, containing a quaternion received
        angles=[sensorData["sensor"]["quaternion"]["w"],sensorData["sensor"]["quaternion"]["x"],sensorData["sensor"]["quaternion"]["y"],sensorData["sensor"]["quaternion"]["z"]]
        #check if the data is valid (and not cut by the network, or even broken before sending)
        isValid=sensorData["sensor"]["isDataValid"]
        pileQuaternions["Tronc"]=angles
        #TODO detect bone concerned by the data
        #example for one bone
        global threadLock
        with threadLock:
            #print("triggerUpdate")
            bpy.data.objects["Armature"]["trigger"]="Tronc"        
        return 


'''blender infrastructure for plugins'''
#ui class
class VIEW3D_PT_MotioCapture(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Animation"
    bl_label = "MotionCapture"
    
    

    def draw(self, context) :
        TheCol = self.layout.column(align = True)
        #adding buttons to launch and stop the recording
        TheCol.operator("object.motiocapture", text = "MotionCapture")
        TheCol.operator("object.motiocapturestop", text = "MotionCaptureStop")
            
        

#operator to start the server (and the recording)
class MotioCapture(bpy.types.Operator):
    bl_idname = "object.motiocapture"
    bl_label = "MotioCapture"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
        
    def execute(self, context):
        print('launching script..')   
        #setting the trigger to call the asyncReading, and store the bone's name
        
        
        bpy.ops.object.posemode_toggle()
        scn = bpy.context.scene
        scn.frame_start = 0
        scn.frame_end = 250
        global servThread
        global area
        
        area=bpy.context.area
        
        global threadLock
        threadLock=threading.Lock()
        servThread=ThreadListener()
        servThread.start()
        return {'FINISHED'}
    
    #end invoke

    
#operator to stop the server
class MotioCaptureStop(bpy.types.Operator):
    bl_idname = "object.motiocapturestop"
    bl_label = "MotioCaptureStop"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
   
    def execute(self, context):
        print('stopping script')
        global servThread
        if not(servThread==None):
            servThread.httpd.shutdown()
        return {'FINISHED'}
    #end invoke

#class wrapping the server in a thread
class ThreadListener(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        self.PORT = 5678
        self.server_address = ("", self.PORT)

        
        self.httpd = None
        
 
    def run(self):
        global area
        print("debut serv")

        area.type = 'VIEW_3D'
        server = http.server.HTTPServer
        self.httpd = server(self.server_address, myHandler)
        global timeInit
        timeInit=time.process_time()
        bpy.context.scene.frame_set(0)
        print("Serveur actif sur le port :", self.PORT)
        self.httpd.serve_forever()
 
 

        
def register():
    bpy.utils.register_module(__name__)
    bpy.app.handlers.scene_update_pre.append(my_handler) 
    print("loading plugin")
    
    


def unregister():
    

    bpy.utils.unregister_module(__name__)
    bpy.app.handlers.scene_update_pre.remove(my_handler)


if __name__ == "__main__":
    register()




