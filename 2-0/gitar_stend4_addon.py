# -*- coding: utf-8 -*-
# Аддон «Пульт четырёх моторов» для сцены Гитара_физика4_ручная.blend
# Панель: 3D-вид -> N-панель -> вкладка «Стенд»
# Четыре ползунка задают ЦЕЛЬ угла каждого кривошипа; мотор доворачивается
# сам с ограничением скорости (как шаговик), всё остальное — живая физика
# Bullet: лента, плечо, штырь в вилке, тележка. Никакой ручной анимации.
bl_info = {
    "name": "Гитара: пульт четырёх моторов",
    "author": "Владимир + Claude",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "3D View > N-панель > Стенд",
    "description": "Четыре кривошипа с плавным приводом, пуск физики и сброс",
    "category": "Object",
}
import bpy
import math
from bpy.app.handlers import persistent

N = 4
_actual = [0.0] * N


def _crank(k):
    return bpy.data.objects.get("кривошип%d" % k)


@persistent
def _drive(scene, depsgraph=None):
    """Каждый кадр: каждый мотор доворачивается к своей цели не быстрее
    stend4_speed °/кадр. Пишем через bpy.data (обработчику дают копию сцены)."""
    sc = bpy.data.scenes.get(scene.name)
    if sc is None or not hasattr(sc, "stend4_speed"):
        return
    step = sc.stend4_speed
    for k in range(N):
        ck = _crank(k)
        if not ck:
            continue
        goal = getattr(sc, "stend4_angle%d" % k)
        cur = _actual[k]
        err = goal - cur
        if abs(err) > step:
            cur += step if err > 0 else -step
        else:
            cur = goal
        _actual[k] = cur
        sc["stend4_actual%d" % k] = cur
        ck.rotation_euler = (0, 0, math.radians(cur))


class STEND4_OT_play(bpy.types.Operator):
    bl_idname = "stend4.play"
    bl_label = "Пуск / пауза физики"
    bl_description = "Запустить или приостановить симуляцию (пробел тоже работает)"

    def execute(self, ctx):
        bpy.ops.screen.animation_play()
        return {'FINISHED'}


class STEND4_OT_reset(bpy.types.Operator):
    bl_idname = "stend4.reset"
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
        for k in range(N):
            setattr(ctx.scene, "stend4_angle%d" % k, 0.0)
            ctx.scene["stend4_actual%d" % k] = 0.0
            _actual[k] = 0.0
            ck = _crank(k)
            if ck:
                ck.rotation_euler = (0, 0, 0)
        return {'FINISHED'}


class STEND4_OT_nudge(bpy.types.Operator):
    bl_idname = "stend4.nudge"
    bl_label = "Повернуть на шаг"
    bl_description = "Довернуть мотор станции на заданный угол"
    k: bpy.props.IntProperty(default=0)
    delta: bpy.props.FloatProperty(default=15.0)

    def execute(self, ctx):
        name = "stend4_angle%d" % self.k
        v = getattr(ctx.scene, name) + self.delta
        setattr(ctx.scene, name, max(-80.0, min(80.0, v)))
        return {'FINISHED'}


class STEND4_OT_zero(bpy.types.Operator):
    bl_idname = "stend4.zero"
    bl_label = "Все в ноль"
    bl_description = "Цели всех четырёх моторов — 0°"

    def execute(self, ctx):
        for k in range(N):
            setattr(ctx.scene, "stend4_angle%d" % k, 0.0)
        return {'FINISHED'}


class STEND4_PT_panel(bpy.types.Panel):
    bl_label = "Пульт четырёх моторов"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Стенд"

    def draw(self, ctx):
        sc = ctx.scene
        col = self.layout.column(align=True)
        col.operator("stend4.play", icon='PLAY')
        col.label(text="Сектор ±80°: 0 = тележка в центре")
        for k in range(N):
            box = col.box()
            row = box.row(align=True)
            row.label(text="Станция %d (тележка %d)" % (k, k + 1))
            fact = sc.get("stend4_actual%d" % k, 0.0)
            row.label(text="мотор %.0f°" % fact)
            box.prop(sc, "stend4_angle%d" % k, slider=True, text="цель")
            row = box.row(align=True)
            for d in (-60, -15, 15, 60):
                op = row.operator("stend4.nudge", text=("%+d°" % d))
                op.k = k
                op.delta = d
        col.separator()
        col.prop(sc, "stend4_speed")
        row = col.row(align=True)
        row.operator("stend4.zero", icon='RECOVER_LAST')
        row.operator("stend4.reset", icon='FILE_REFRESH')


classes = (STEND4_OT_play, STEND4_OT_reset, STEND4_OT_nudge, STEND4_OT_zero, STEND4_PT_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    for k in range(N):
        setattr(bpy.types.Scene, "stend4_angle%d" % k, bpy.props.FloatProperty(
            name="Угол %d" % k, description="Цель поворота кривошипа станции %d, градусы" % k,
            min=-80.0, max=80.0, default=0.0, step=100))
    bpy.types.Scene.stend4_speed = bpy.props.FloatProperty(
        name="Скорость, °/кадр", description="Предел скорости моторов",
        min=0.2, max=10.0, default=1.5)
    if _drive not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(_drive)


def unregister():
    if _drive in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(_drive)
    del bpy.types.Scene.stend4_speed
    for k in range(N):
        delattr(bpy.types.Scene, "stend4_angle%d" % k)
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
