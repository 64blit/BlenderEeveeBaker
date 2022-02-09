
###############   IMPORTS
from random import Random, randrange
import bpy
from bpy.utils import previews
import os
import math
from math import pi
from easybpy import *
import mathutils
from mathutils.bvhtree import BVHTree as bvh
import numpy as np
import bmesh
from icecream import ic

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# This addon was created with the Serpens - Visual Scripting Addon.
# This code is generated from nodes and is not intended for manual editing.
# You can find out more about Serpens at <https://blendermarket.com/products/serpens>.


bl_info = {
    "name": "Eevee Baker",
    "description": "",
    "author": "64blit",
    "version": (1, 0, 0),
    "blender": (3, 0, 1),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"
}

random = Random()

###############   INITALIZE VARIABLES
###############   SERPENS FUNCTIONS
def exec_line(line):
    exec(line)

def sn_print(tree_name, *args):
    if tree_name in bpy.data.node_groups:
        item = bpy.data.node_groups[tree_name].sn_graphs[0].prints.add()
        for arg in args:
            item.value += str(arg) + ";;;"
        if bpy.context and bpy.context.screen:
            for area in bpy.context.screen.areas:
                area.tag_redraw()
    print(*args)

def sn_cast_string(value):
    return str(value)

def sn_cast_boolean(value):
    if type(value) == tuple:
        for data in value:
            if bool(data):
                return True
        return False
    return bool(value)

def sn_cast_float(value):
    if type(value) == str:
        try:
            value = float(value)
            return value
        except:
            return float(bool(value))
    elif type(value) == tuple:
        return float(value[0])
    elif type(value) == list:
        return float(len(value))
    elif not type(value) in [float, int, bool]:
        try:
            value = len(value)
            return float(value)
        except:
            return float(bool(value))
    return float(value)

def sn_cast_int(value):
    return int(sn_cast_float(value))

def sn_cast_boolean_vector(value, size):
    if type(value) in [str, bool, int, float]:
        return_value = []
        for i in range(size):
            return_value.append(bool(value))
        return tuple(return_value)
    elif type(value) == tuple:
        return_value = []
        for i in range(size):
            return_value.append(bool(value[i]) if len(value) > i else bool(value[0]))
        return tuple(return_value)
    elif type(value) == list:
        return sn_cast_boolean_vector(tuple(value), size)
    else:
        try:
            value = tuple(value)
            return sn_cast_boolean_vector(value, size)
        except:
            return sn_cast_boolean_vector(bool(value), size)

def sn_cast_float_vector(value, size):
    if type(value) in [str, bool, int, float]:
        return_value = []
        for i in range(size):
            return_value.append(sn_cast_float(value))
        return tuple(return_value)
    elif type(value) == tuple:
        return_value = []
        for i in range(size):
            return_value.append(sn_cast_float(value[i]) if len(value) > i else sn_cast_float(value[0]))
        return tuple(return_value)
    elif type(value) == list:
        return sn_cast_float_vector(tuple(value), size)
    else:
        try:
            value = tuple(value)
            return sn_cast_float_vector(value, size)
        except:
            return sn_cast_float_vector(sn_cast_float(value), size)

def sn_cast_int_vector(value, size):
    return tuple(map(int, sn_cast_float_vector(value, size)))

def sn_cast_color(value, use_alpha):
    length = 4 if use_alpha else 3
    value = sn_cast_float_vector(value, length)
    tuple_list = []
    for data in range(length):
        data = value[data] if len(value) > data else value[0]
        tuple_list.append(sn_cast_float(min(1, max(0, data))))
    return tuple(tuple_list)

def sn_cast_list(value):
    if type(value) in [str, tuple, list]:
        return list(value)
    elif type(value) in [int, float, bool]:
        return [value]
    else:
        try:
            value = list(value)
            return value
        except:
            return [value]

def sn_cast_blend_data(value):
    if hasattr(value, "bl_rna"):
        return value
    elif type(value) in [tuple, bool, int, float, list]:
        return None
    elif type(value) == str:
        try:
            value = eval(value)
            return value
        except:
            return None
    else:
        return None

def sn_cast_enum(string, enum_values):
    for item in enum_values:
        if item[1] == string:
            return item[0]
        elif item[0] == string.upper():
            return item[0]
    return string

def refresh_all_areas():
    for wm in bpy.data.window_managers:
        for w in wm.windows:
            for area in w.screen.areas:
                area.tag_redraw()
###############   IMPERATIVE CODE
###############   EVALUATED CODE
#######   Eevee Baker
class SNA_OT_Eeveebake(bpy.types.Operator):
    bl_idname = "sna.eeveebake"
    bl_label = "EeveeBake"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

        
    def TriangulateMesh(self, obj ):
        dg = bpy.context.window.view_layer.depsgraph

        bm = bmesh.new()

        n = len(bm.verts)
        bm.from_object(obj, dg)
        bmesh.ops.transform(
                bm,
                verts=bm.verts[n:],
                matrix=obj.matrix_world,
                )
            
        bmesh.ops.triangulate(
                bm,
                faces=bm.faces,
                )
                
        return bm

    def bounding_sphere(self, objects, mode='GEOMETRY'):
        # return the bounding sphere center and radius for objects (in global coordinates)
        if not isinstance(objects, list):
            objects = [objects]
        points_co_global = []
        if mode == 'GEOMETRY':
            # GEOMETRY - by all vertices/points - more precis, more slow
            for obj in objects:
                points_co_global.extend([obj.matrix_world @ vertex.co for vertex in obj.data.vertices])
        elif mode == 'BBOX':
            # BBOX - by object bounding boxes - less precis, quick
            for obj in objects:
                points_co_global.extend([obj.matrix_world @ Vector(bbox) for bbox in obj.bound_box])

        def get_center(l):
            return (max(l) + min(l)) / 2 if l else 0.0

        x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
        b_sphere_center = Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
        b_sphere_radius = max(((point - b_sphere_center) for point in points_co_global)) if b_sphere_center else None
        return b_sphere_center, b_sphere_radius.length


    def render(self):
        # render_image(True)
        path = os.path.join(bpy.app.tempdir, "render_temp_save.png")
        saved_path = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        for img in bpy.data.images:
            if img.type == 'RENDER_RESULT':
                path = os.path.join(bpy.app.tempdir, "render_temp_save.png")
                img.save_render(path)
                loaded_img = bpy.data.images.load(path)
                loaded_img.pixels[0] # this makes no sense, but it is necessary to load pixels array internally
                ret = [i for i in loaded_img.pixels]
                
                bpy.data.images.remove(loaded_img)
                os.remove(path)
                bpy.context.scene.render.filepath = saved_path

                return ret

        bpy.context.scene.render.filepath = saved_path

    def create_empty(self, name, location):
        o = bpy.data.objects.new( name, None )
        bpy.context.scene.collection.objects.link( o )
        # empty_draw was replaced by empty_display
        o.empty_display_size = 2
        o.empty_display_type = 'PLAIN_AXES'   
        o.location = location
        return o


    def get_raycasted_uv_point(self, cam, target, bake_resolution):
        
        bpy.context.scene.camera = cam
        # perform the actual ray casting
        if self.tree is None:
            # self.target = self.TriangulateMesh(target)
            # self.tree = bvh.FromBMesh(self.target)
            self.tree = bvh.FromObject(target, bpy.context.window.view_layer.depsgraph)
        
        matrixWorld = target.matrix_world
        matrixWorldInverted = matrixWorld.inverted()
        origin = matrixWorldInverted @ cam.matrix_world.translation
        frame = cam.data.view_frame(scene=bpy.context.scene)
        topRight = frame[0]
        bottomRight = frame[1]
        bottomLeft = frame[2]
        topLeft = frame[3]
        
        # setup vectors to match pixels
        if self.xRange is None:
            self.xRange = np.linspace(topLeft[0], topRight[0], bake_resolution)
            self.yRange = np.linspace(topLeft[1], bottomLeft[1], bake_resolution)
            self.xPixel = self.xRange[int(bake_resolution/2.0)]
            self.yPixel = self.yRange[int(bake_resolution/2.0)]

        # get current pixel vector from camera center to pixel
        pixelVector = Vector((self.xPixel, self.yPixel, topLeft[2]))
        
        # rotate that vector according to camera rotation
        pixelVector.rotate(cam.matrix_world.to_quaternion())

        # calculate direction vector
        destination = matrixWorldInverted @ (pixelVector + cam.matrix_world.translation) 
        direction = (destination - origin).normalized()
        
        # perform the actual ray casting
        # hit, location, norm, face =  target.ray_cast(origin, direction)
        hit_location, norm, face_index, dist = self.tree.ray_cast(origin, direction)

        # print(hit_location, norm, face_index, dist)
        if hit_location is None:
            return
      
        vertices = target.data.polygons[face_index].vertices

        vert1, vert2, vert3 = [target.data.vertices[vertices[i]].co for i in range(3)]

        #from the face's index calculated by the BVHTree finds the coresponding UVs as a list
        uvMap_indices = target.data.polygons[face_index].loop_indices

        #for the lookup, gets the UV map in use 
        uvMap = target.data.uv_layers.active

        #decompose the UVs list in individual components
        uv_1, uv_2, uv_3 = [uvMap.data[uvMap_indices[i]].uv for i in range(3)]

        #conversion of the UV locations to a 3D vector, as the barycentric calculation uses an more generic implementation (3D), z will be 0

        uv1 = uv_1.to_3d()
        uv2 = uv_2.to_3d()
        uv3 = uv_3.to_3d()

        #barycentric calculation of the coresponding point in the uv space
        b_point = mathutils.geometry.barycentric_transform( hit_location, vert1, vert2, vert3, uv1, uv2, uv3 )

        #reduces the 3d vector back to a 2d vector
        b_point.resize_2d()
        

        #gets the x,y coordinates of the pixel and finds the (ungefähr) pixel in the array. rounding errors are expected to occur
        uv_x = round(b_point[0]*bake_resolution)
        uv_y = round(b_point[1]*bake_resolution)


        # reset view mode
        # bpy.context.area.type = mode

        return uv_x, uv_y


    def setup(self):
        
        bpy.context.window_manager.progress_begin(0, 100)
        set_render_resolution(self.btex_res,self.btex_res)
                
        self.bobj = get_active_object()
            # set all objects to holdout except baking obj
        all_objs = get_all_objects()
        for o in all_objs:
            o.is_holdout = True
            
        self.bobj.is_holdout = False
        
        # create bake cam
        if object_exists('EeveeBakeCamera'):
            delete_object('EeveeBakeCamera')

        camera_data = bpy.data.cameras.new(name='EeveeBakeCamera')
        self.cam = bpy.data.objects.new('EeveeBakeCamera', camera_data)
        self.cam = get_object('EeveeBakeCamera')

        # make empty cam parent
        if object_exists( "EeveeBakeCamera_parent"):
            delete_object( "EeveeBakeCamera_parent")

        self.cam_parent = self.create_empty( "EeveeBakeCamera_parent" , Vector())
        
        set_parent( self.cam, self.cam_parent )
        location(self.cam, Vector())

        deselect_all_objects()
        
        set_parent( self.cam_parent, self.bobj )
        
        location(self.cam_parent, self.bobj.location)
        

        # add camera constraint
        bpy.context.scene.collection.objects.link(self.cam)


        bsphere, bounding_radius = self.bounding_sphere( [ self.bobj ] )
        
        select_object(self.cam)
        damped_track = add_damped_track_constraint(self.cam)
        damped_track.target = self.bobj
        damped_track.track_axis = 'TRACK_NEGATIVE_Z'
        translate_along_z(bounding_radius*2, self.cam)
        
        deselect_all_objects()


        #create bake texture
        if self.bobj.data.name_full + "_bake" in bpy.data.images:
            delete_image(self.bobj.data.name_full+"_bake")

        self.btex = create_image(name=self.bobj.data.name_full+"_bake",width=self.btex_res, height=self.btex_res)
        
        self.tree = None
        self.xRange = None
        self.yRange = None
        self.xPixel = 0
        self.yPixel = 0
        bpy.context.scene.camera = self.cam
    
    def modal(self, context, event):
        context.area.tag_redraw()
        if self.finished or event.type in {'ESC'}:
            context.window_manager.progress_end()
            self.report({'INFO'}, "Finished baking")
            context.window_manager.event_timer_remove(self._timer)
            return {'CANCELLED'}
        
        if self.bake_pass == 0:
            self.setup()

        self.cam_parent.rotation_euler[0] = self.x * pi/180
        self.cam_parent.rotation_euler[2] = self.z * pi/180
        
        if self.z >= 360:
            self.x += self.step
            self.z = 0
        if self.x >= 180:
            self.finished = True
        

        self.bake_pass += 1
        self.z += self.step
        

        res = get_render_resolution()
        img = self.render()
        i = res[0] / 2 + res[1] / 2
        i = int(i) * 4
        middle_pixel = img[i  : i + 4]
        
        # middle_pixel = [random.random(),random.random(),random.random(),1.0]

        point = self.get_raycasted_uv_point(self.cam, self.bobj, self.btex_res)
        # print(middle_pixel)
        print(point)
        if point is None:
            return {'RUNNING_MODAL'}

        uv_pixel1= ((point[0] * point[1]) * 4)
        uv_pixel = len(self.btex.pixels) - uv_pixel1
        # print(uv_pixel1, uv_pixel)

        self.btex.pixels[uv_pixel : uv_pixel + 4] = middle_pixel
        
        context.window_manager.progress_update(int( (self.x/360.0)*100 ))

        # self.finished = True
        # self.report({'INFO'}, "Baking progress: {percent:.2f}%. Press [Esc] to cancel. ".format(percent= (self.x/360.0)*100))
        

        return {'RUNNING_MODAL'}


    def execute(self, context):
        try:
        
            pass
        
            cls = lambda: os.system('cls')
            cls()
        
            bobj = get_active_object()
            if bobj is None or bobj.type != 'MESH':
                self.report({'WARNING'}, "No active mesh selected, could not bake")
                return {'CANCELLED'}
            
            else:
                self.finished = False
                self.bake_pass = 0
                self.x = 1
                self.z = 1
                self.step = 10
                self.btex_res = 100
                
                self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
                context.window_manager.modal_handler_add(self)
                # timer event needed to refresh the macro between bakes

                self.report({'INFO'}, "Baking progress: {percent:.2f}%. Press [Esc] to cancel. ".format(percent= (self.x/360.0)*100))
                return {'RUNNING_MODAL'}
        
        except Exception as exc:
        
            print(str(exc) + " | Error in execute function of EeveeBake")
        
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


#######   Interface
class SNA_PT_Eevee_Baker_test_D8C05(bpy.types.Panel):
    bl_label = "Eevee Baker [test]"
    bl_idname = "SNA_PT_Eevee_Baker_test_D8C05"
    bl_parent_id = "RENDER_PT_context"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = 'render'
    bl_options = {"DEFAULT_CLOSED",}


    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        try:
            layout = self.layout
        except Exception as exc:
            print(str(exc) + " | Error in Eevee Baker [test] subpanel header")

    def draw(self, context):
        try:
            layout = self.layout
            layout.label(text=r"Bake",icon_value=0)
            op = layout.operator("sna.eeveebake",text=r"Bake Selected",emboss=True,depress=False,icon_value=0)
        except Exception as exc:
            print(str(exc) + " | Error in Eevee Baker [test] subpanel")


###############   REGISTER ICONS
def sn_register_icons():
    icons = []
    bpy.types.Scene.eevee_baker_icons = bpy.utils.previews.new()
    icons_dir = os.path.join( os.path.dirname( __file__ ), "icons" )
    for icon in icons:
        bpy.types.Scene.eevee_baker_icons.load( icon, os.path.join( icons_dir, icon + ".png" ), 'IMAGE' )

def sn_unregister_icons():
    bpy.utils.previews.remove( bpy.types.Scene.eevee_baker_icons )


###############   REGISTER PROPERTIES
def sn_register_properties():
    pass

def sn_unregister_properties():
    pass


###############   REGISTER ADDON
def register():
    sn_register_icons()
    sn_register_properties()
    bpy.utils.register_class(SNA_OT_Eeveebake)
    bpy.utils.register_class(SNA_PT_Eevee_Baker_test_D8C05)


###############   UNREGISTER ADDON
def unregister():
    sn_unregister_icons()
    sn_unregister_properties()
    bpy.utils.unregister_class(SNA_PT_Eevee_Baker_test_D8C05)
    bpy.utils.unregister_class(SNA_OT_Eeveebake)
