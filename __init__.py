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

bl_info = {
    "name" : "Mass Importer",
    "author" : "Goodluck Focus",
    "description" : "Mass-import OBJ files and keep track of where they came from",
    "blender" : (2, 82, 0),
    "version" : (1, 0, 0),
    "location" : "3D Viewport",
    "warning" : "",
    "category" : "Import"
}
import pathlib
import bpy

#TODO create mass reload operator to reload that iterates over all the object or all the selected objects

def mass_import_path(scene) -> pathlib.Path:
    abspath = bpy.path.abspath(scene.mass_import_path)
    return pathlib.Path(abspath)


class IMPORT_SCENE_OT_obj_mass(bpy.types.Operator):
    bl_idname = 'import_scene.obj_mass'
    bl_label = 'Mass-import OBJs'

    def execute(self, context):
        #Find the OBJ Files
        import_path = mass_import_path(context.scene)
        for import_fpath in import_path.glob('*.obj'):
            bpy.ops.import_scene.obj(filepath = str(import_fpath))
            for imported_ob in context.selected_objects:
                imported_ob.mass_import_fname = import_fpath.name
        #self.report(
         #   {'ERROR'},
          #  f'No code to load from{abspath}')
        return {'FINISHED'}


class IMPORT_SCENE_OT_obj_reload(bpy.types.Operator):
    bl_idname = 'import_scene.obj_reload'
    bl_label = 'Reload Mass-import OBJ'

    def execute(self, context):
        ob = context.object

        #Store what we want to remember
        mass_import_fname =ob.mass_import_fname
        matrix_world =ob.matrix_world.copy()
        #Remove object from Scene
        for collection in list(ob.users_collection):
            collection.objects.unlink(ob)

        if ob.users == 0:
            bpy.data.objects.remove(ob)
        del ob

        #Load the Obj File
        import_path = mass_import_path(context.scene)
        import_fpath = import_path / mass_import_fname
        bpy.ops.import_scene.obj(filepath=str(import_fpath))
        #Restore what we remember
        for imported_ob in context.selected_objects:
            imported_ob.mass_import_fname = import_fpath.name
            imported_ob.matrix_world = matrix_world
        return {'FINISHED'}





class VIEW3D_PT_mass_import(bpy.types.Panel):
    bl_space_type ='VIEW_3D'
    bl_region_type = 'UI'
    bl_category ='Monkeys'
    bl_label = 'Mass Import'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene, 'mass_import_path')
        col.operator('import_scene.obj_mass')

        col = layout.column(align=True)
        if context.object:
            col.prop(context.object, 'mass_import_fname')
            col.operator('import_scene.obj_reload')
        else:
            col.label(text = 'No Active Object')


blender_classes ={
    VIEW3D_PT_mass_import,
    IMPORT_SCENE_OT_obj_mass,
    IMPORT_SCENE_OT_obj_reload,
}


def register():
    bpy.types.Scene.mass_import_path = bpy.props.StringProperty(
        name ='OBJ Folder',
        subtype ='DIR_PATH',
    )
    bpy.types.Object.mass_import_fname = bpy.props.StringProperty(
        name = 'OBJ File',
    )
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
    ...

def unregister():
    del bpy.types.Scene.mass_import_path
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
