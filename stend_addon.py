# -*- coding: utf-8 -*-
# Аддон «Пульт мотора» для тест-стендов гитары (Стенд_ручной.blend и др.)
# Панель: 3D-вид -> N-панель -> вкладка «Стенд»
bl_info = {
    "name": "Стенд гитары: пульт мотора",
    "author": "Владимир + Claude",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "3D View > N-панель > Стенд",
    "description": "Крутилка кривошипа, пуск физики и сброс, если всё разлетелось",
    "category": "Object",
}
import bpy
import math


def _crank(ctx):
    for ob in ctx.scene.objects:
        if ob.name.startswith("ptest_crank"):
            return ob
    return None


def _upd(self, ctx):
    ck = _crank(ctx)
    if ck:
        ck.rotation_euler = (0, 0, math.radians(-90 + self.stend_angle))


class STEND_OT_play(bpy.types.Operator):
    bl_idname = "stend.play"
    bl_label = "Пуск / пауза физики"
    bl_description = "Запустить или приостановить симуляцию"

    def execute(self, ctx):
        bpy.ops.screen.animation_play()
        return {'FINISHED'}


class STEND_OT_reset(bpy.types.Operator):
    bl_idname = "stend.reset"
    bl_label = "Собрать заново"
    bl_description = "Вернуть все детали на места (если разлетелось)"

    def execute(self, ctx):
        if ctx.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)
        try:
            bpy.ops.ptcache.free_bake_all()
        except RuntimeError:
            pass
        ctx.scene.frame_set(1)
        ctx.scene.stend_angle = 0.0
        return {'FINISHED'}


class STEND_PT_panel(bpy.types.Panel):
    bl_label = "Пульт мотора"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Стенд"

    def draw(self, ctx):
        col = self.layout.column(align=True)
        col.operator("stend.play", icon='PLAY')
        col.separator()
        col.label(text="Крути (тяни мышью):")
        col.prop(ctx.scene, "stend_angle", slider=True)
        row = col.row(align=True)
        for d in (-90, -15, 15, 90):
            op = row.operator("stend.nudge", text=("%+d°" % d))
            op.delta = d
        col.separator()
        col.operator("stend.reset", icon='FILE_REFRESH')


class STEND_OT_nudge(bpy.types.Operator):
    bl_idname = "stend.nudge"
    bl_label = "Повернуть на шаг"
    bl_description = "Довернуть мотор на заданный угол"
    delta: bpy.props.FloatProperty(default=15.0)

    def execute(self, ctx):
        ctx.scene.stend_angle += self.delta
        return {'FINISHED'}


classes = (STEND_OT_play, STEND_OT_reset, STEND_OT_nudge, STEND_PT_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.stend_angle = bpy.props.FloatProperty(
        name="Угол мотора", description="Поворот кривошипа от нейтрали, градусы",
        min=-1080.0, max=1080.0, default=0.0, step=100, update=_upd)


def unregister():
    del bpy.types.Scene.stend_angle
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
