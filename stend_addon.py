# -*- coding: utf-8 -*-
# Аддон «Пульт мотора» v1.1 для тест-стендов гитары
# Панель: 3D-вид -> N-панель -> вкладка «Стенд»
# v1.1: ползунок задаёт ЦЕЛЬ, мотор доворачивается сам с ограничением скорости
# (как настоящий шаговик) — резкие движения руки больше не рвут физику.
bl_info = {
    "name": "Стенд гитары: пульт мотора",
    "author": "Владимир + Claude",
    "version": (1, 1),
    "blender": (4, 0, 0),
    "location": "3D View > N-панель > Стенд",
    "description": "Крутилка кривошипа с плавным приводом, пуск физики и сброс",
    "category": "Object",
}
import bpy
import math
from bpy.app.handlers import persistent


def _crank(scene):
    for ob in scene.objects:
        if ob.name.startswith("ptest_crank"):
            return ob
    return None


_state = {"actual": None}


@persistent
def _drive(scene, depsgraph=None):
    """Каждый кадр: мотор доворачивается к цели не быстрее stend_speed °/кадр.
    Работаем через bpy.data (обработчику даётся копия сцены — записи в неё
    пропадают), а текущий угол держим в модуле."""
    sc = bpy.data.scenes.get(scene.name)
    if sc is None or not hasattr(sc, "stend_angle"):
        return
    ck = None
    for ob in sc.objects:
        if ob.name.startswith("ptest_crank"):
            ck = bpy.data.objects.get(ob.name)
            break
    if not ck:
        return
    cur = _state["actual"]
    if cur is None:
        cur = sc.get("stend_actual", 0.0)
    err = sc.stend_angle - cur
    step = sc.stend_speed
    if abs(err) > step:
        cur += step if err > 0 else -step
    else:
        cur = sc.stend_angle
    _state["actual"] = cur
    sc["stend_actual"] = cur
    ck.rotation_euler = (0, 0, math.radians(-90 + cur))


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
        ctx.scene["stend_actual"] = 0.0
        _state["actual"] = 0.0
        ck = _crank(ctx.scene)
        if ck:
            ck.rotation_euler = (0, 0, math.radians(-90))
        return {'FINISHED'}


class STEND_OT_nudge(bpy.types.Operator):
    bl_idname = "stend.nudge"
    bl_label = "Повернуть на шаг"
    bl_description = "Довернуть мотор на заданный угол"
    delta: bpy.props.FloatProperty(default=15.0)

    def execute(self, ctx):
        ctx.scene.stend_angle += self.delta
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
        col.label(text="Цель (мотор доедет сам):")
        col.prop(ctx.scene, "stend_angle", slider=True)
        row = col.row(align=True)
        for d in (-90, -15, 15, 90):
            op = row.operator("stend.nudge", text=("%+d°" % d))
            op.delta = d
        col.prop(ctx.scene, "stend_speed")
        fact = ctx.scene.get("stend_actual", 0.0)
        col.label(text="Мотор сейчас: %.0f°" % fact)
        col.separator()
        col.operator("stend.reset", icon='FILE_REFRESH')


classes = (STEND_OT_play, STEND_OT_reset, STEND_OT_nudge, STEND_PT_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.stend_angle = bpy.props.FloatProperty(
        name="Угол мотора", description="Цель поворота кривошипа, градусы",
        min=-1080.0, max=1080.0, default=0.0, step=100)
    bpy.types.Scene.stend_actual = bpy.props.FloatProperty(
        name="Факт", default=0.0)
    bpy.types.Scene.stend_speed = bpy.props.FloatProperty(
        name="Скорость, °/кадр", description="Предел скорости мотора",
        min=0.2, max=10.0, default=1.5)
    if _drive not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(_drive)


def unregister():
    if _drive in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(_drive)
    del bpy.types.Scene.stend_speed
    del bpy.types.Scene.stend_actual
    del bpy.types.Scene.stend_angle
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
