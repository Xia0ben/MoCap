
    

    
import json
from math import *
import bpy,bmesh
import mathutils
import numpy as np
import copy as c
from bpy.props import *
import http.server
from threading import Thread
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
servThread=None
timeInit=-1
interFrames=1
timePeriod=1.0/30
area=None
class myHandler(BaseHTTPRequestHandler):
    #Handler for the GET requests
    def do_GET(self):
        if self.path=="/":
            self.path="/index_example3.html"

        try:
            #Check the file extension required and
            #set the right mime type

            print(self.path)
            return

        except IOError:
            print(404,'File Not Found: %s' % self.path)

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data =self.rfile.read(length).decode('UTF-8')
        sensorData=json.loads(data)
        angles=[sensorData["sensor"]["quaternion"]["w"],sensorData["sensor"]["quaternion"]["x"],sensorData["sensor"]["quaternion"]["y"],sensorData["sensor"]["quaternion"]["z"]]
        isValid=sensorData["sensor"]["isDataValid"]
        pbase=bpy.data.objects["Armature"].pose.bones['Tronc']
        pbase.rotation_mode = 'QUATERNION'
        pbase.rotation_quaternion = mathutils.Quaternion((angles[0],angles[1],angles[2],angles[3]))
        global timeInit
        global interFrames
        global timePeriod
        if(time.process_time()-timeInit>=timePeriod):
            #bpy.context.scene.active = bpy.data.scenes["Scene"].(null)
            timeInit=time.process_time()
            bpy.context.scene.frame_set(bpy.context.scene.frame_current+interFrames)
            bpy.ops.anim.keyframe_insert_menu(type='__ACTIVE__')
            #pbase.keyframe_insert('location',group="LocRot")
            #pbase.keyframe_insert("rotation_quaternion",group="LocRot")
        return



class VIEW3D_PT_MotioCapture(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Animation"
    bl_label = "MotionCapture"
    
    

    def draw(self, context) :
        TheCol = self.layout.column(align = True)
        TheCol.operator("object.motiocapture", text = "MotionCapture")
        TheCol.operator("object.motiocapturestop", text = "MotionCaptureStop")
            
        


class MotioCapture(bpy.types.Operator):
    bl_idname = "object.motiocapture"
    bl_label = "MotioCapture"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
        
    def execute(self, context):
        print('launching script..')       
        bpy.ops.object.posemode_toggle()
        scn = bpy.context.scene
        scn.frame_start = 0
        scn.frame_end = 250
        global servThread
        global area
        area=bpy.context.area
        servThread=ThreadListener()
        servThread.start()
        
        return {'FINISHED'}
    #end invoke

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


class ThreadListener(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        self.PORT = 80
        self.server_address = ("", self.PORT)

        
        self.httpd = None
       
        print("Serveur actif sur le port :", self.PORT)
        
 
    def run(self):
        global area
        area.type = 'VIEW_3D'
        server = http.server.HTTPServer
        self.httpd = server(self.server_address, myHandler)
        global timeInit
        timeInit=time.process_time()
        bpy.context.scene.frame_set(0)
        self.httpd.serve_forever()
        

        
def register():
    bpy.utils.register_module(__name__)
    print("loading plugin")
    
    


def unregister():
    

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()




