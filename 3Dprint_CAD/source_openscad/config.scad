plate_sidelength = 100;
//hole_radius = 25/6;
gridsize = plate_sidelength/(4*10-1);
plate_thickness = 3;
bot_plate_maze_space = 10;
wall_height = 6;
hole_out_r = 4;
slide_width = 8;
camera_height = 150;
holder_wall_width = 35;
camera_width = 10;
fn = 100;

box_height = 90; // change
box_shift = 0;
box_width = 72;
box_width1 = box_width + box_shift;
servo_h_offset = 18; // change
h_clip = 30; // change
max_angle = 20;
w_arm = 17 - plate_thickness;
w_arm_full = w_arm + box_width/2;
pivot_offset = 15; // 0 would be in the middle

clip_cutout_w = 2;
clip_scale = 46/h_clip;


hole_coords = [[0,0], [6,0], [8,1], [6,2], [1,3], [3,4], [6,4], [2,5], [5,5], [2,6], [9,6], [1,7], [4,8], [8,8], [1,8], [5,8], [8,3]];
wall_coords_h = [[0,3], [0,5], [1,1], [1,3], [1,4], [1,6], [2,1], [2,4], [2,5], [2,6], [3,1], [3,8], [4,1], [4,2], [4,5], [5,1], [5,3], [5,7], [6,1], [6,7], [7,1], [7,7], [8,1], [8,4], [5,6], [6,6], [7,5]];
wall_coords_v = [[0,7], [0,8], [0,9], [1,1], [2,0], [2,2], [2,3], [3,6], [3,7], [4,3], [5,4], [7,5], [7,6], [7,7], [8,2], [8,3], [8,4], [6,9], [4,1], [6,6]];
corner_coords = [[0,3], [0,6], [0,7], [0,8], [1,1], [1,4], [1,6], [2,1], [2,2], [2,3], [3,1], [3,5], [3,6], [3,8], [4,1], [4,2], [4,3], [5,1], [5,3], [5,7], [6,1], [6,7], [7,1], [7,4], [7,5], [7,6], [7,7], [8,1], [8,2], [8,3], [8,4], [2,4], [3,7], [4,5], [5,4], [4,7], [6,5], [6,6], [5,6]];
