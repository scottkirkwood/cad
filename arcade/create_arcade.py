import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def inch_to_m(val):
    return val * 0.0254

def m_to_inch(val):
    return val / 0.0254

# ==========================================
# Robust Scene Cleanup (Pure Data API)
# ==========================================
def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves):
        for item in list(block):
            block.remove(item, do_unlink=True)

clear_scene()

scene = bpy.context.scene
scene.unit_settings.system = 'IMPERIAL'
scene.unit_settings.length_unit = 'INCHES'

# ==========================================
# MASTER PARAMETERS (Inches)
# ==========================================
SIDE_WOOD_THICKNESS = 0.75     # 3/4" plywood for side panels
INTERNAL_WOOD_THICKNESS = 0.5  # 1/2" plywood for internal panels
SHELF_WOOD_THICKNESS = 0.75    # 3/4" plywood for CP shelf (cut from leftover Sheet 1)

CABINET_INNER_WIDTH = 23.0    # Internal width between side panels (fits 19" monitor + cleats, fits standard 30" door frames)
CABINET_DEPTH = 18.0          # Skinnier cabinet depth (fits 4x8 plywood sheet nesting)

# Control Console & Keyboard Drawer Parameters
CP_WIDTH = 31.5               # User's existing control box width (overhanging winged panel)
CP_DEPTH = 10.5               # Front-to-back depth of control box
CP_HEIGHT_FRONT = 3.0         # Front height of control box
CP_HEIGHT_BACK = 4.25         # Back height of control box (slanted top)
CP_SHELF_HEIGHT = 34.0        # Height of support shelf top off ground (top of box lands at 37" front, 38.25" back)
KEYBOARD_DRAWER_HEIGHT = 3.25 # Height for pull-out keyboard drawer under shelf

# Toe Kick Parameters (Adjusted per user request: moved up in Z, skinnier recess)
TOE_KICK_HEIGHT = 4.5         # Height of kickplate recess in Z (moved up from 3.5")
TOE_KICK_DEPTH = 1.5          # Depth of kickplate recess in X (skinnier, reduced from 2.5")

# Marquee & Upper Cabinet
MARQUEE_HEIGHT = 5.5          # Parametric marquee height (compact 5.5")
MONITOR_ORIENTATION = 'LANDSCAPE'  # 'LANDSCAPE' or 'PORTRAIT'
MONITOR_WIDTH = 16.2          # 19" Dell 5:4 width
MONITOR_HEIGHT = 13.5         # 19" Dell 5:4 height
SPEAKER_HOLE_DIA = 4.0        # 4" Pyle speakers

# Collections
col_cabinet = bpy.data.collections.new("Arcade_Cabinet")
scene.collection.children.link(col_cabinet)

col_controls = bpy.data.collections.new("Control_Panel")
col_cabinet.children.link(col_controls)

col_electronics = bpy.data.collections.new("Monitor_and_Audio")
col_cabinet.children.link(col_electronics)

col_cut_plan = bpy.data.collections.new("Cut_Sheets_2D")
scene.collection.children.link(col_cut_plan)

# Materials
def get_or_create_material(name, color, roughness=0.5, metallic=0.0, emission_color=None):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        if not mat.node_tree and hasattr(mat, "use_nodes"):
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
            if emission_color:
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emission_color
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emission_color
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = 2.0
    return mat

mat_black_paint = get_or_create_material("Cabinet_Black_Satin", (0.05, 0.05, 0.05, 1.0), roughness=0.35)
mat_plywood_edge = get_or_create_material("Plywood_Core", (0.82, 0.70, 0.52, 1.0), roughness=0.7)
mat_white_trim = get_or_create_material("White_T_Molding", (0.95, 0.95, 0.95, 1.0), roughness=0.2)
mat_bezel = get_or_create_material("Bezel_Dark_Gray", (0.02, 0.02, 0.02, 1.0), roughness=0.1)
mat_screen = get_or_create_material("Screen_Active", (0.1, 0.25, 0.45, 1.0), roughness=0.05, emission_color=(0.15, 0.35, 0.6, 1.0))
mat_speaker_mesh = get_or_create_material("Speaker_Mesh", (0.03, 0.03, 0.03, 1.0), roughness=0.8, metallic=0.8)
mat_marquee_glass = get_or_create_material("Marquee_Glass", (0.9, 0.9, 0.9, 1.0), roughness=0.1, emission_color=(1.0, 0.95, 0.85, 1.0))
mat_red_button = get_or_create_material("Button_Red", (0.8, 0.05, 0.05, 1.0), roughness=0.3)
mat_blue_button = get_or_create_material("Button_Blue", (0.05, 0.2, 0.8, 1.0), roughness=0.3)
mat_yellow_button = get_or_create_material("Button_Yellow", (0.9, 0.8, 0.05, 1.0), roughness=0.3)
mat_stick_shaft = get_or_create_material("Chrome", (0.9, 0.9, 0.9, 1.0), roughness=0.1, metallic=1.0)
mat_keyboard = get_or_create_material("Keyboard_Dark_Gray", (0.12, 0.12, 0.14, 1.0), roughness=0.4)

# Cut Sheet specific materials
mat_sheet_34 = get_or_create_material("Sheet_3_4_Wood", (0.75, 0.62, 0.45, 1.0), roughness=0.6)
mat_sheet_12 = get_or_create_material("Sheet_1_2_Wood", (0.85, 0.74, 0.55, 1.0), roughness=0.6)
mat_sheet_scrap = get_or_create_material("Sheet_Scrap", (0.35, 0.35, 0.35, 1.0), roughness=0.8)
mat_sheet_border = get_or_create_material("Sheet_Border", (0.15, 0.15, 0.15, 1.0), roughness=0.5)
mat_label_text = get_or_create_material("Label_Dark_Text", (0.02, 0.02, 0.02, 1.0), roughness=0.2)
mat_header_text = get_or_create_material("Header_White_Text", (0.95, 0.95, 0.95, 1.0), roughness=0.2)

# ==========================================
# Pure BMesh Geometry Builders
# ==========================================
def create_extruded_poly_mesh(name, points_2d, thickness):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [bm.verts.new((inch_to_m(pt[0]), 0, inch_to_m(pt[1]))) for pt in points_2d]
    face = bm.faces.new(verts)
    bmesh.ops.extrude_face_region(bm, geom=[face])
    for v in bm.verts:
        if v not in verts:
            v.co.y += inch_to_m(thickness)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def create_board_mesh(name, width, height, thickness):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    scale_vec = Vector((inch_to_m(thickness), inch_to_m(width), inch_to_m(height)))
    bmesh.ops.scale(bm, vec=scale_vec, verts=bm.verts)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def make_object(name, mesh, loc, rot, collection, material):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (inch_to_m(loc[0]), inch_to_m(loc[1]), inch_to_m(loc[2]))
    obj.rotation_euler = rot
    collection.objects.link(obj)
    if len(mesh.materials) == 0:
        mesh.materials.append(material)
    obj.material_slots[0].link = 'OBJECT'
    obj.material_slots[0].material = material
    return obj

def create_cylinder(name, radius, depth, loc, rot, collection, material, segments=24):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
    )
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(material)
    collection.objects.link(obj)
    return obj

def create_sphere(name, radius, loc, collection, material, u_segments=24, v_segments=16):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(
        bm,
        u_segments=u_segments,
        v_segments=v_segments,
        radius=radius,
    )
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.data.materials.append(material)
    collection.objects.link(obj)
    return obj

# ==========================================
# Coordinate Calculations
# ==========================================
cp_front_x = -CP_DEPTH / 2.0                             # -5.25"
cp_rear_x = CP_DEPTH / 2.0                               # 5.25"
shelf_bottom_z = CP_SHELF_HEIGHT - SHELF_WOOD_THICKNESS  # 33.25"
cp_rear_top_z = CP_SHELF_HEIGHT + CP_HEIGHT_BACK         # 38.25"

# Keyboard drawer housing
kb_bottom_z = shelf_bottom_z - KEYBOARD_DRAWER_HEIGHT    # 30.00"
kb_housing_bottom_z = kb_bottom_z - INTERNAL_WOOD_THICKNESS # 29.50"

# Diagonal support corbel: from front face X=0 up to front of keyboard housing X=-5.25
diag_front_z = 23.50                                     # Where diagonal connects to vertical coin door front

# Marquee & Roof Calculations
x_marquee_bottom = 9.0
z_marquee_bottom = 58.0
x_marquee_top = 7.75
z_marquee_top = z_marquee_bottom + MARQUEE_HEIGHT        # 63.5"
z_roof = z_marquee_top + INTERNAL_WOOD_THICKNESS         # 64.0" (roof flush with cabinet top)

# Exact side profile contour (Beefed up diagonal support, moved up toe kick)
side_profile = [
    (TOE_KICK_DEPTH, 0.0),               # P0:  Bottom toe-kick recess
    (TOE_KICK_DEPTH, TOE_KICK_HEIGHT),   # P1:  Top of toe-kick recess (moved up in Z)
    (0.0, TOE_KICK_HEIGHT),              # P2:  Front lower corner (skinnier kickplate cover)
    (0.0, diag_front_z),                 # P3:  Top of coin door vertical front
    (cp_front_x, kb_housing_bottom_z),   # P4:  Solid diagonal corbel support under console
    (cp_front_x, shelf_bottom_z),        # P5:  Front vertical face of keyboard drawer cavity
    (cp_rear_x, shelf_bottom_z),         # P6:  Rear edge of shelf ledge
    (cp_rear_x, cp_rear_top_z),          # P7:  Vertical rise behind control box
    (14.5, 52.0),                        # P8:  Top of monitor bezel
    (x_marquee_bottom, z_marquee_bottom),# P9:  Base of marquee / top of speaker panel
    (x_marquee_top, z_marquee_top),      # P10: Top of marquee / bottom of roof front
    (x_marquee_top, z_roof),             # P11: Front top corner of roof lip
    (CABINET_DEPTH, z_roof),             # P12: Top back roof corner
    (CABINET_DEPTH, 0.0),                # P13: Bottom back floor corner
]

# Create Side Panels (Shared Mesh between Left & Right)
side_panel_mesh = create_extruded_poly_mesh("Mesh_Side_Panel", side_profile, SIDE_WOOD_THICKNESS)
half_inner = CABINET_INNER_WIDTH / 2.0
obj_side_l = make_object("Side_Panel_Left", side_panel_mesh, (0, -half_inner - SIDE_WOOD_THICKNESS, 0), (0, 0, 0), col_cabinet, mat_black_paint)
obj_side_r = make_object("Side_Panel_Right", side_panel_mesh, (0, half_inner, 0), (0, 0, 0), col_cabinet, mat_black_paint)

# Registry of cut pieces for linked 2D cut plan
cut_registry = {}

def register_board(name, width, height, thickness, loc, rot, collection, material):
    mesh = create_board_mesh(f"Mesh_{name}", width, height, thickness)
    obj_3d = make_object(name, mesh, loc, rot, collection, material)
    cut_registry[name] = {
        "mesh": mesh,
        "obj_3d": obj_3d,
        "width": width,
        "length": height,
        "thickness": thickness
    }
    return obj_3d

# 1. Base floor plate (1/2" Plywood: X=2.0 to X=17.5, Z=0.0 to 0.5)
bottom_plate_start_x = TOE_KICK_DEPTH + INTERNAL_WOOD_THICKNESS
bottom_plate_end_x = CABINET_DEPTH - INTERNAL_WOOD_THICKNESS
bottom_plate_len = bottom_plate_end_x - bottom_plate_start_x
bottom_plate_mid_x = (bottom_plate_start_x + bottom_plate_end_x) / 2.0
register_board("Bottom_Plate", CABINET_INNER_WIDTH, bottom_plate_len, INTERNAL_WOOD_THICKNESS,
               (bottom_plate_mid_x, 0, INTERNAL_WOOD_THICKNESS / 2.0), (0, math.radians(90), 0), col_cabinet, mat_black_paint)

# 2. Toe Kick Board (1/2" Plywood: X=1.5 to 2.0, Z=0.0 to 4.5)
register_board("Toe_Kick_Board", CABINET_INNER_WIDTH, TOE_KICK_HEIGHT, INTERNAL_WOOD_THICKNESS,
               (TOE_KICK_DEPTH + INTERNAL_WOOD_THICKNESS / 2.0, 0, TOE_KICK_HEIGHT / 2.0), (0, 0, 0), col_cabinet, mat_black_paint)

# 3. Toe Kick Ceiling / Kickplate Cover (1/2" Plywood: X=0.0 to 1.5, Z=4.0 to 4.5 - Moved up and skinnier!)
register_board("Toe_Kick_Ceiling", CABINET_INNER_WIDTH, TOE_KICK_DEPTH, INTERNAL_WOOD_THICKNESS,
               (TOE_KICK_DEPTH / 2.0, 0, TOE_KICK_HEIGHT - INTERNAL_WOOD_THICKNESS / 2.0), (0, math.radians(90), 0), col_cabinet, mat_black_paint)

# 4. Lower Front Panel (1/2" Plywood: Coin Door Area, X=0.0 to 0.5, Z=4.5 to 23.5)
coin_panel_height = diag_front_z - TOE_KICK_HEIGHT
register_board("Lower_Front_Panel", CABINET_INNER_WIDTH, coin_panel_height, INTERNAL_WOOD_THICKNESS,
               (INTERNAL_WOOD_THICKNESS / 2.0, 0, (TOE_KICK_HEIGHT + diag_front_z) / 2.0), (0, 0, 0), col_cabinet, mat_black_paint)

# 5. Console Diagonal Apron (1/2" Plywood: Solid diagonal knee shield from (0.0, 23.5) to (-5.25, 29.5))
dx_diag = cp_front_x - 0.0
dz_diag = kb_housing_bottom_z - diag_front_z
diag_len = math.sqrt(dx_diag*dx_diag + dz_diag*dz_diag)
angle_diag = math.atan2(dx_diag, dz_diag) # Negative angle
cos_d = math.cos(angle_diag)
sin_d = math.sin(angle_diag)
diag_mid_x = (0.0 + cp_front_x) / 2.0
diag_mid_z = (diag_front_z + kb_housing_bottom_z) / 2.0
# Offset inward so front face is flush with side profile diagonal edge
diag_center_x = diag_mid_x + cos_d * (INTERNAL_WOOD_THICKNESS / 2.0)
diag_center_z = diag_mid_z - sin_d * (INTERNAL_WOOD_THICKNESS / 2.0)

register_board("Console_Diagonal_Apron", CABINET_INNER_WIDTH, diag_len, INTERNAL_WOOD_THICKNESS,
               (diag_center_x, 0, diag_center_z), (0, angle_diag, 0), col_cabinet, mat_black_paint)

# 6. Keyboard Housing Bottom Plate (1/2" Plywood: X=-5.25 to 0.0, Z=29.5 to 30.0)
kb_plate_len = abs(cp_front_x)
register_board("Keyboard_Bottom_Plate", CABINET_INNER_WIDTH, kb_plate_len, INTERNAL_WOOD_THICKNESS,
               (cp_front_x / 2.0, 0, kb_housing_bottom_z + INTERNAL_WOOD_THICKNESS / 2.0), (0, math.radians(90), 0), col_cabinet, mat_black_paint)

# Slide-out Keyboard Tray (Mounted on slides at Z=30.25")
mesh_kb = create_board_mesh("Mesh_Keyboard_Tray", 21.0, 9.0, 0.5)
make_object("Keyboard_Tray", mesh_kb, (-0.75, 0, kb_bottom_z + 0.35), (0, math.radians(90), 0), col_controls, mat_keyboard)

# 7. Control Panel Support Shelf (3/4" Plywood: X=-5.25 to 5.25, Z=33.25 to 34.0, Width=31.5")
shelf_mid_z = shelf_bottom_z + SHELF_WOOD_THICKNESS / 2.0
register_board("Control_Panel_Shelf", CP_WIDTH, CP_DEPTH, SHELF_WOOD_THICKNESS,
               (0.0, 0.0, shelf_mid_z), (0, math.radians(90), 0), col_cabinet, mat_black_paint)

# 8. User's 31.5" x 10.5" Control Box (Pre-built console resting on the shelf)
def create_control_box():
    mesh = bpy.data.meshes.new("User_Control_Box")
    bm = bmesh.new()
    w2 = inch_to_m(CP_WIDTH / 2.0)
    d = inch_to_m(CP_DEPTH)
    h_f = inch_to_m(CP_HEIGHT_FRONT)
    h_b = inch_to_m(CP_HEIGHT_BACK)
    x_f = inch_to_m(cp_front_x)
    x_b = inch_to_m(cp_rear_x)
    z_base = inch_to_m(CP_SHELF_HEIGHT)
    
    v0 = bm.verts.new((x_f, -w2, z_base))
    v1 = bm.verts.new((x_f,  w2, z_base))
    v2 = bm.verts.new((x_b,  w2, z_base))
    v3 = bm.verts.new((x_b, -w2, z_base))
    v4 = bm.verts.new((x_f, -w2, z_base + h_f))
    v5 = bm.verts.new((x_f,  w2, z_base + h_f))
    v6 = bm.verts.new((x_b,  w2, z_base + h_b))
    v7 = bm.verts.new((x_b, -w2, z_base + h_b))
    
    bm.faces.new([v0, v1, v5, v4]) # Front
    bm.faces.new([v1, v2, v6, v5]) # Right
    bm.faces.new([v2, v3, v7, v6]) # Back
    bm.faces.new([v3, v0, v4, v7]) # Left
    bm.faces.new([v4, v5, v6, v7]) # Top
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("User_Control_Box_31_5", mesh)
    col_controls.objects.link(obj)
    obj.data.materials.append(mat_black_paint)
    obj.data.materials.append(mat_white_trim)
    
    top_angle = math.atan2(h_b - h_f, d)
    z_mid = z_base + (h_f + h_b) / 2.0
    
    for side, p_name in [(-inch_to_m(7.5), "P1"), (inch_to_m(7.5), "P2")]:
        shaft_loc = (-inch_to_m(2.0), side - inch_to_m(2.5), z_mid + inch_to_m(1.2))
        create_cylinder(f"{p_name}_Joystick_Shaft", inch_to_m(0.2), inch_to_m(2.0), shaft_loc, (0, -top_angle, 0), col_controls, mat_stick_shaft)
        
        ball_loc = (-inch_to_m(2.0), side - inch_to_m(2.5), z_mid + inch_to_m(2.2))
        ball_mat = mat_red_button if p_name == "P1" else mat_blue_button
        create_sphere(f"{p_name}_Joystick_Ball", inch_to_m(0.7), ball_loc, col_controls, ball_mat)
        
        for row in range(2):
            for col_b in range(3):
                bx = -inch_to_m(2.8) + col_b * inch_to_m(1.2)
                by = side + inch_to_m(0.5) + col_b * inch_to_m(0.2) + row * inch_to_m(1.2)
                bz = z_base + h_f + (bx - x_f) * math.tan(top_angle) + inch_to_m(0.1)
                btn_mat = mat_red_button if row == 0 else (mat_blue_button if col_b == 0 else mat_yellow_button)
                create_cylinder(f"{p_name}_Button_{row}_{col_b}", inch_to_m(0.55), inch_to_m(0.15), (bx, by, bz), (0, -top_angle, 0), col_controls, btn_mat)

create_control_box()

# 9. Monitor Bezel Board (1/2" Plywood: Flush front face on line P7 -> P8)
dx_bezel = 14.5 - cp_rear_x
dz_bezel = 52.0 - cp_rear_top_z
bezel_len = math.sqrt(dx_bezel*dx_bezel + dz_bezel*dz_bezel)
angle_bezel = math.atan2(dx_bezel, dz_bezel)
mid_x_bezel = (cp_rear_x + 14.5) / 2.0
mid_z_bezel = (cp_rear_top_z + 52.0) / 2.0

cos_b = math.cos(angle_bezel)
sin_b = math.sin(angle_bezel)
bezel_center_x = mid_x_bezel + cos_b * (INTERNAL_WOOD_THICKNESS / 2.0)
bezel_center_z = mid_z_bezel - sin_b * (INTERNAL_WOOD_THICKNESS / 2.0)

register_board("Monitor_Bezel_Board", CABINET_INNER_WIDTH, bezel_len, INTERNAL_WOOD_THICKNESS,
               (bezel_center_x, 0, bezel_center_z), (0, angle_bezel, 0), col_electronics, mat_bezel)

# 19" Active Screen (flush on front face of bezel)
scr_w, scr_h = (MONITOR_HEIGHT, MONITOR_WIDTH) if MONITOR_ORIENTATION == 'PORTRAIT' else (MONITOR_WIDTH, MONITOR_HEIGHT)
screen_thick = 0.2
scr_offset = screen_thick / 2.0 + 0.02
scr_x = mid_x_bezel - cos_b * scr_offset
scr_z = mid_z_bezel + sin_b * scr_offset
create_board_mesh("Mesh_Screen", scr_w, scr_h, screen_thick)
make_object("Dell_P1913Sf_19in_Screen", bpy.data.meshes["Mesh_Screen"], (scr_x, 0, scr_z), (0, angle_bezel, 0), col_electronics, mat_screen)

# 10. Speaker Board (1/2" Plywood: Flush front face on line P8 -> P9)
dx_spk = x_marquee_bottom - 14.5
dz_spk = z_marquee_bottom - 52.0
panel_len_spk = math.sqrt(dx_spk*dx_spk + dz_spk*dz_spk)
angle_spk = math.atan2(dx_spk, dz_spk)
mid_x_spk = (14.5 + x_marquee_bottom) / 2.0
mid_z_spk = (52.0 + z_marquee_bottom) / 2.0

cos_s = math.cos(angle_spk)
sin_s = math.sin(angle_spk)
spk_center_x = mid_x_spk + cos_s * (INTERNAL_WOOD_THICKNESS / 2.0)
spk_center_z = mid_z_spk - sin_s * (INTERNAL_WOOD_THICKNESS / 2.0)

register_board("Speaker_Board", CABINET_INNER_WIDTH, panel_len_spk, INTERNAL_WOOD_THICKNESS,
               (spk_center_x, 0, spk_center_z), (0, angle_spk, 0), col_electronics, mat_black_paint)

# Speaker Grills
grill_depth = 0.2
gx = mid_x_spk - cos_s * (grill_depth / 2.0 + 0.02)
gz = mid_z_spk + sin_s * (grill_depth / 2.0 + 0.02)
cyl_rot = (0, angle_spk - math.radians(90), 0)
for side, name in [(-inch_to_m(6.0), "Left"), (inch_to_m(6.0), "Right")]:
    create_cylinder(f"Speaker_Grill_4in_{name}", inch_to_m(SPEAKER_HOLE_DIA / 2.0), inch_to_m(grill_depth), (inch_to_m(gx), side, inch_to_m(gz)), cyl_rot, col_electronics, mat_speaker_mesh)

# 11. Marquee Header (1/4" Acrylic: Flush front face on line P9 -> P10)
dx_marq = x_marquee_top - x_marquee_bottom
dz_marq = z_marquee_top - z_marquee_bottom
marquee_len = math.sqrt(dx_marq*dx_marq + dz_marq*dz_marq)
angle_marq = math.atan2(dx_marq, dz_marq)
mid_x_marq = (x_marquee_bottom + x_marquee_top) / 2.0
mid_z_marq = (z_marquee_bottom + z_marquee_top) / 2.0
cos_m = math.cos(angle_marq)
sin_m = math.sin(angle_marq)
marq_thick = 0.25
marq_center_x = mid_x_marq + cos_m * (marq_thick / 2.0)
marq_center_z = mid_z_marq - sin_m * (marq_thick / 2.0)

mesh_marq = create_board_mesh("Mesh_Marquee_Sign_Backlit", CABINET_INNER_WIDTH, marquee_len, marq_thick)
make_object("Marquee_Sign_Backlit", mesh_marq, (marq_center_x, 0, marq_center_z), (0, angle_marq, 0), col_cabinet, mat_marquee_glass)

# 12. Top Roof Panel (1/2" Plywood: X=7.75 to 18.0, Z=63.5 to 64.0)
roof_len = CABINET_DEPTH - x_marquee_top
roof_mid_x = (x_marquee_top + CABINET_DEPTH) / 2.0
register_board("Top_Roof_Panel", CABINET_INNER_WIDTH, roof_len, INTERNAL_WOOD_THICKNESS,
               (roof_mid_x, 0, z_roof - INTERNAL_WOOD_THICKNESS / 2.0), (0, math.radians(90), 0), col_cabinet, mat_black_paint)

# 13. Rear Back Access Door (1/2" Plywood: X=17.5 to 18.0, Z=0.5 to 63.5)
back_door_x = CABINET_DEPTH - INTERNAL_WOOD_THICKNESS / 2.0
back_door_bottom = INTERNAL_WOOD_THICKNESS
back_door_top = z_roof - INTERNAL_WOOD_THICKNESS
back_door_height = back_door_top - back_door_bottom
back_door_z = (back_door_top + back_door_bottom) / 2.0
register_board("Back_Access_Door", CABINET_INNER_WIDTH, back_door_height, INTERNAL_WOOD_THICKNESS,
               (back_door_x, 0, back_door_z), (0, 0, 0), col_cabinet, mat_black_paint)

# ==========================================
# 2D Cut Sheet Generator (CLONED & LINKED TO 3D MODEL)
# ==========================================
def create_sheet_outline(name, x_pos, y_pos, label):
    mesh = bpy.data.meshes.new(f"Outline_{name}")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    scale_vec = Vector((inch_to_m(96.0), inch_to_m(48.0), inch_to_m(0.1)))
    bmesh.ops.scale(bm, vec=scale_vec, verts=bm.verts)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(f"Outline_{name}", mesh)
    obj.location = (inch_to_m(x_pos + 48.0), inch_to_m(y_pos + 24.0), inch_to_m(-0.1))
    obj.data.materials.append(mat_sheet_border)
    col_cut_plan.objects.link(obj)
    
    cu = bpy.data.curves.new(f"Header_{name}", type='FONT')
    cu.body = label
    cu.size = inch_to_m(2.2)
    cu.extrude = 0.004
    t_obj = bpy.data.objects.new(f"Header_{name}", cu)
    t_obj.location = (inch_to_m(x_pos + 1.0), inch_to_m(y_pos + 49.0), inch_to_m(0.2))
    t_obj.data.materials.append(mat_header_text)
    col_cut_plan.objects.link(t_obj)

def create_scrap_box(name, length_in, width_in, pos_x, pos_y, label="Scrap"):
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    scale_vec = Vector((inch_to_m(length_in), inch_to_m(width_in), inch_to_m(0.1)))
    bmesh.ops.scale(bm, vec=scale_vec, verts=bm.verts)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(f"Cut_{name}", mesh)
    obj.location = (inch_to_m(pos_x + length_in / 2.0), inch_to_m(pos_y + width_in / 2.0), inch_to_m(0.05))
    obj.data.materials.append(mat_sheet_scrap)
    col_cut_plan.objects.link(obj)
    
    if label:
        cu = bpy.data.curves.new(f"Label_{name}", type='FONT')
        cu.body = label
        cu.size = inch_to_m(1.4)
        t_obj = bpy.data.objects.new(f"Label_{name}", cu)
        t_obj.location = (inch_to_m(pos_x + 1.5), inch_to_m(pos_y + width_in / 2.0 - 0.7), inch_to_m(0.15))
        t_obj.data.materials.append(mat_label_text)
        col_cut_plan.objects.link(t_obj)

def place_cloned_board_on_sheet(name, pos_x, pos_y, material, label_text=""):
    entry = cut_registry[name]
    mesh = entry["mesh"]
    length_in = entry["length"]
    width_in = entry["width"]
    thick_in = entry["thickness"]
    
    obj_cut = bpy.data.objects.new(f"Cut_{name}", mesh)
    obj_cut.rotation_euler = (0, math.radians(90), 0)
    obj_cut.location = (
        inch_to_m(pos_x + length_in / 2.0),
        inch_to_m(pos_y + width_in / 2.0),
        inch_to_m(thick_in / 2.0)
    )
    col_cut_plan.objects.link(obj_cut)
    
    obj_cut.material_slots[0].link = 'OBJECT'
    obj_cut.material_slots[0].material = material
    
    if label_text:
        cu = bpy.data.curves.new(f"Label_{name}", type='FONT')
        cu.body = label_text
        cu.extrude = 0.003
        text_obj = bpy.data.objects.new(f"Label_{name}", cu)
        
        if length_in < 9.0:
            cu.size = inch_to_m(1.2)
            text_obj.location = (
                inch_to_m(pos_x + length_in / 2.0 + 0.4),
                inch_to_m(pos_y + 2.0),
                inch_to_m(thick_in + 0.1)
            )
            text_obj.rotation_euler = (0, 0, math.radians(90))
        else:
            cu.size = inch_to_m(1.4)
            text_obj.location = (
                inch_to_m(pos_x + 1.5),
                inch_to_m(pos_y + width_in / 2.0 - 1.2),
                inch_to_m(thick_in + 0.1)
            )
            text_obj.rotation_euler = (0, 0, 0)
            
        text_obj.data.materials.append(mat_label_text)
        col_cut_plan.objects.link(text_obj)
    return obj_cut

def place_cloned_side_panel_on_sheet(name, pos_x, pos_y, material, label_text=""):
    obj_cut = bpy.data.objects.new(f"Cut_{name}", side_panel_mesh)
    obj_cut.rotation_euler = (math.radians(90), 0, math.radians(90))
    obj_cut.location = (
        inch_to_m(pos_x),
        inch_to_m(pos_y - cp_front_x),
        0.0
    )
    col_cut_plan.objects.link(obj_cut)
    
    obj_cut.material_slots[0].link = 'OBJECT'
    obj_cut.material_slots[0].material = material
    
    if label_text:
        cu = bpy.data.curves.new(f"Label_{name}", type='FONT')
        cu.body = label_text
        cu.size = inch_to_m(1.8)
        cu.extrude = 0.003
        t_obj = bpy.data.objects.new(f"Label_{name}", cu)
        t_obj.location = (inch_to_m(pos_x + 8.0), inch_to_m(pos_y + 10.0), inch_to_m(SIDE_WOOD_THICKNESS + 0.1))
        t_obj.data.materials.append(mat_label_text)
        col_cut_plan.objects.link(t_obj)
    return obj_cut

# Cut Plan Coordinates
sheet1_x = 40.0
sheet1_y = -52.0
sheet2_x = 40.0
sheet2_y = 6.0

# --- SHEET 1: 3/4" Plywood (48" x 96") ---
create_sheet_outline("Sheet1_3_4", sheet1_x, sheet1_y, "SHEET 1: 3/4\" Plywood (48\" x 96\") - Linked Side Panels & CP Shelf")

side_bbox_len = z_roof                  # 64.0"
side_bbox_w = CABINET_DEPTH - cp_front_x # 23.25"

# Place real cloned side panels (linked to 3D side panels!)
place_cloned_side_panel_on_sheet("Side_Panel_Left", sheet1_x, sheet1_y, mat_sheet_34, f"Side Panel Left (3/4\" Plywood)\n{side_bbox_len:.2f}\" x {side_bbox_w:.2f}\" (Contoured)")
place_cloned_side_panel_on_sheet("Side_Panel_Right", sheet1_x, sheet1_y + 24.25, mat_sheet_34, f"Side Panel Right (3/4\" Plywood)\n{side_bbox_len:.2f}\" x {side_bbox_w:.2f}\" (Contoured)")

# Control Panel Shelf placed in leftover 3/4" space
place_cloned_board_on_sheet("Control_Panel_Shelf", sheet1_x + side_bbox_len + 1.0, sheet1_y, mat_sheet_34, f"CP Support Shelf (3/4\")\n{CP_WIDTH:.2f}\" x {CP_DEPTH:.2f}\"")
create_scrap_box("Sheet1_Scrap", 96.0 - (side_bbox_len + CP_DEPTH + 1.5), 48.0, sheet1_x + side_bbox_len + CP_DEPTH + 1.5, sheet1_y, "Leftover 3/4\" Scrap\n(Cleats & Braces)")

# --- SHEET 2: 1/2" Plywood (48" x 96") ---
create_sheet_outline("Sheet2_1_2", sheet2_x, sheet2_y, "SHEET 2: 1/2\" Plywood (48\" x 96\") - Linked Internal Panels (All 23\" Width)")

# Strip A: 23" width rip (Y = sheet2_y to sheet2_y + 23")
strip_a_y = sheet2_y
cur_x = sheet2_x
place_cloned_board_on_sheet("Back_Access_Door", cur_x, strip_a_y, mat_sheet_12, f"Back Access Door (1/2\")\n{back_door_height:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += back_door_height + 0.25

place_cloned_board_on_sheet("Bottom_Plate", cur_x, strip_a_y, mat_sheet_12, f"Bottom Floor Plate (1/2\")\n{bottom_plate_len:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += bottom_plate_len + 0.25

place_cloned_board_on_sheet("Speaker_Board", cur_x, strip_a_y, mat_sheet_12, f"Speaker Board (1/2\")\n{panel_len_spk:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += panel_len_spk + 0.25

strip_a_scrap = 96.0 - (cur_x - sheet2_x)
create_scrap_box("Strip_A_Scrap", strip_a_scrap, CABINET_INNER_WIDTH, cur_x, strip_a_y, f"Scrap\n{strip_a_scrap:.1f}\" x 23\"")

# Strip B: 23" width rip (Y = sheet2_y + 24" to sheet2_y + 47")
strip_b_y = sheet2_y + 24.0
cur_x = sheet2_x
place_cloned_board_on_sheet("Lower_Front_Panel", cur_x, strip_b_y, mat_sheet_12, f"Coin Door Front (1/2\")\n{coin_panel_height:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += coin_panel_height + 0.25

place_cloned_board_on_sheet("Console_Diagonal_Apron", cur_x, strip_b_y, mat_sheet_12, f"Console Diag Apron (1/2\")\n{diag_len:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += diag_len + 0.25

place_cloned_board_on_sheet("Monitor_Bezel_Board", cur_x, strip_b_y, mat_sheet_12, f"Monitor Bezel (1/2\")\n{bezel_len:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += bezel_len + 0.25

place_cloned_board_on_sheet("Top_Roof_Panel", cur_x, strip_b_y, mat_sheet_12, f"Top Roof Panel (1/2\")\n{roof_len:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += roof_len + 0.25

place_cloned_board_on_sheet("Keyboard_Bottom_Plate", cur_x, strip_b_y, mat_sheet_12, f"Keyboard Base (1/2\")\n{kb_plate_len:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += kb_plate_len + 0.25

place_cloned_board_on_sheet("Toe_Kick_Board", cur_x, strip_b_y, mat_sheet_12, f"Toe Kick Riser (1/2\")\n{TOE_KICK_HEIGHT:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += TOE_KICK_HEIGHT + 0.25

place_cloned_board_on_sheet("Toe_Kick_Ceiling", cur_x, strip_b_y, mat_sheet_12, f"Kickplate Cover (1/2\")\n{TOE_KICK_DEPTH:.2f}\" x {CABINET_INNER_WIDTH:.1f}\"")
cur_x += TOE_KICK_DEPTH + 0.25

strip_b_scrap = 96.0 - (cur_x - sheet2_x)
create_scrap_box("Strip_B_Scrap", strip_b_scrap, CABINET_INNER_WIDTH, cur_x, strip_b_y, f"Scrap / Spares\n{strip_b_scrap:.1f}\" x 23\"")

# ==========================================
# Camera and Studio Lighting
# ==========================================
# 1. 3D Perspective Camera
cam_data = bpy.data.cameras.new("Arcade_Camera")
cam_data.lens = 45
cam_obj = bpy.data.objects.new("Arcade_Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_pos = Vector((-2.8, -2.6, 1.5))
target_pos = Vector((0.2, 0.0, 0.9))
direction = (target_pos - cam_pos).normalized()
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.location = cam_pos
cam_obj.rotation_euler = rot_quat.to_euler()

# 2. 2D Cut Plan Orthographic Camera
cam_cut_data = bpy.data.cameras.new("Cut_Plan_Camera")
cam_cut_data.type = 'ORTHO'
cam_cut_data.sensor_fit = 'VERTICAL'
cam_cut_data.ortho_scale = inch_to_m(126)
cam_cut_obj = bpy.data.objects.new("Cut_Plan_Camera", cam_cut_data)
scene.collection.objects.link(cam_cut_obj)
cam_cut_obj.location = (inch_to_m(88.0), inch_to_m(2.0), inch_to_m(150))
cam_cut_obj.rotation_euler = (0, 0, 0)

# Studio Lights
light_data = bpy.data.lights.new(name="Key_Light", type='AREA')
light_data.energy = 300
light_data.size = 2.0
light_obj = bpy.data.objects.new("Key_Light", light_data)
scene.collection.objects.link(light_obj)
light_obj.location = (inch_to_m(-25), -inch_to_m(35), inch_to_m(75))
light_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
fill_light_data.energy = 120
fill_light_data.size = 3.0
fill_light_obj = bpy.data.objects.new("Fill_Light", fill_light_data)
scene.collection.objects.link(fill_light_obj)
fill_light_obj.location = (inch_to_m(25), inch_to_m(35), inch_to_m(60))

cut_light_data = bpy.data.lights.new(name="Cut_Plan_Light", type='SUN')
cut_light_data.energy = 3.0
cut_light_obj = bpy.data.objects.new("Cut_Plan_Light", cut_light_data)
scene.collection.objects.link(cut_light_obj)
cut_light_obj.location = (inch_to_m(88.0), inch_to_m(2.0), inch_to_m(180))

# Embed generator script directly into the blend file
script_text = bpy.data.texts.new("parametric_arcade_generator.py")
with open("/home/scott/20p/cad/arcade/parametric_arcade_generator.py", "r") as f:
    script_text.from_string(f.read())

# Also embed an interactive live measurements updater script!
updater_script = bpy.data.texts.new("update_cut_plan_measurements.py")
updater_script.from_string('''import bpy
from mathutils import Vector

def m_to_in(m):
    return m / 0.0254

print("\\n" + "="*60)
print(" LIVE CUT LIST MEASUREMENTS (Measured directly from meshes)")
print("="*60)

for obj in bpy.data.collections.get("Arcade_Cabinet").all_objects:
    if obj.type == "MESH" and not obj.name.startswith("User_Control_Box") and not "Joystick" in obj.name and not "Button" in obj.name and not "Grill" in obj.name and not "Screen" in obj.name:
        dx = m_to_in(obj.dimensions.x)
        dy = m_to_in(obj.dimensions.y)
        dz = m_to_in(obj.dimensions.z)
        dims = sorted([dx, dy, dz])
        print(f" {obj.name:25s} : Thickness={dims[0]:.2f}\", Width={dims[1]:.2f}\", Length={dims[2]:.2f}\"")
        
        label_obj = bpy.data.objects.get(f"Label_{obj.name}")
        if label_obj and hasattr(label_obj.data, "body"):
            lines = label_obj.data.body.split("\\n")
            lines[-1] = f"{dims[2]:.2f}\\\" x {dims[1]:.2f}\\\""
            label_obj.data.body = "\\n".join(lines)

print("="*60 + "\\n")
''')

# Save main blend file
output_path = "/home/scott/20p/cad/arcade/arcade_cabinet_parametric.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"Arcade CAD model successfully generated and saved to: {output_path}")

# ==========================================
# Print Cut List Summary
# ==========================================
print("\n" + "="*70)
print("             ARCADE CABINET CUT PLAN & MATERIAL SUMMARY")
print("="*70)
print(f"Cabinet Outer Dimensions: {CABINET_DEPTH}\" Deep x {CABINET_INNER_WIDTH + 2 * SIDE_WOOD_THICKNESS:.2f}\" Wide x {z_roof:.2f}\" High")
print(f"Cabinet Inner Width:      {CABINET_INNER_WIDTH:.2f}\"")
print(f"Control Panel Span:       {CP_WIDTH:.2f}\" Wide x {CP_DEPTH:.2f}\" Deep (Overhanging Wings)")
print(f"Keyboard Drawer Cavity:   {KEYBOARD_DRAWER_HEIGHT}\" Clear Height x 23.00\" Width")
print(f"Toe Kick Recess:          {TOE_KICK_HEIGHT}\" Height x {TOE_KICK_DEPTH}\" Depth (Kickplate Cover: {TOE_KICK_DEPTH}\" x 23.00\")")
print("\n--- SHEET 1: 3/4\" PLYWOOD (48\" x 96\") ---")
print(f" 1. Side Panel Left:       {side_bbox_len:.2f}\" x {side_bbox_w:.2f}\"  (Shape Cut, Linked, Beefed-up Diagonal)")
print(f" 2. Side Panel Right:      {side_bbox_len:.2f}\" x {side_bbox_w:.2f}\"  (Shape Cut, Linked, Beefed-up Diagonal)")
print(f" 3. Control Panel Shelf:   {CP_WIDTH:.2f}\" x {CP_DEPTH:.2f}\"  (Heavy-Duty Support, Linked)")
print(f"    Leftover Scrap on Sheet 1: ~19.0\" x 48.0\" (Extra cleats & braces)")
print("\n--- SHEET 2: 1/2\" PLYWOOD (48\" x 96\") ---")
print(" Rip Sheet 2 into TWO 23.0\" wide strips along the 96\" length:")
print(" * Strip A (23.0\" Wide x 96.0\" Long):")
print(f"   - Back Access Door:     {back_door_height:.2f}\" x 23.00\" (Linked)")
print(f"   - Bottom Floor Plate:   {bottom_plate_len:.2f}\" x 23.00\" (Linked)")
print(f"   - Speaker Board:        {panel_len_spk:.2f}\" x 23.00\" (Linked, Dual 4\" Speaker Holes)")
print(f"   - Strip A Scrap:        ~{strip_a_scrap:.1f}\" x 23.00\"")
print(" * Strip B (23.0\" Wide x 96.0\" Long):")
print(f"   - Lower Front Coin Door: {coin_panel_height:.2f}\" x 23.00\" (Linked)")
print(f"   - Console Diag Apron:   {diag_len:.2f}\" x 23.00\" (Linked, Diagonal Support Cover)")
print(f"   - Monitor Bezel:        {bezel_len:.2f}\" x 23.00\" (Linked, 19\" Dell 5:4 Cutout)")
print(f"   - Top Roof Panel:       {roof_len:.2f}\" x 23.00\" (Linked)")
print(f"   - Keyboard Base Plate:  {kb_plate_len:.2f}\" x 23.00\" (Linked)")
print(f"   - Toe Kick Riser:       {TOE_KICK_HEIGHT:.2f}\" x 23.00\" (Linked)")
print(f"   - Kickplate Cover:      {TOE_KICK_DEPTH:.2f}\" x 23.00\" (Linked, Skinnier 1.5\"!)")
print(f"   - Strip B Scrap:        ~{strip_b_scrap:.1f}\" x 23.00\"")
print("="*70 + "\n")
