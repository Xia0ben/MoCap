
    

    
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
            
        


class MotioCapture(bpy.types.Operator):
    bl_idname = "object.motiocapture"
    bl_label = "MotioCapture"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
   
    def execute(self, context):
        print('launching script..')
        

        
        servThread=ThreadListener()
        bpy.ops.object.posemode_toggle()
        servThread.start()
        
        return {'FINISHED'}
    #end invoke



class ThreadListener(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)
        self.PORT = 80
        self.server_address = ("", self.PORT)

        self.server = http.server.HTTPServer
        print("Serveur actif sur le port :", self.PORT)
        
 
    def run(self):
        httpd = self.server(self.server_address, myHandler)
        httpd.serve_forever()
        

        
def register():
    bpy.utils.register_module(__name__)
    print("loading plugin")
    
    


def unregister():
    

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()




