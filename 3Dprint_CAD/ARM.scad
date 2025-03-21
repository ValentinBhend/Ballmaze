include <config.scad>;
use <arm_servo_cutout.scad>;

function r(turn_angle) = 
    let (
        tilt_angle = -max_angle 
        + 2*max_angle*turn_angle/180,
        H = h_clip + servo_h_offset
    )
    H - w_arm_full * tan(tilt_angle);


function r1(turn_angle) = 
    let (
        tilt_angle = -max_angle 
        + 2*max_angle*turn_angle/180,
        H = h_clip + servo_h_offset,
        h1 = H + w_arm_full * tan(max_angle),
        h2 = H - w_arm_full * tan(max_angle)
    )
    h2 + (h1-h2) * (180-turn_angle)^2 / 180^2;


module spiral(){
    H = h_clip + servo_h_offset;
    h1 = H + w_arm_full * tan(max_angle);
    h2 = H - w_arm_full * tan(max_angle);
    d = plate_thickness;
    points = [for (i=[0:180]) [r1(i)*cos(i), r1(i)*sin(i)]];
    linear_extrude(d)
    polygon(points);
}

module arm(){
    d = plate_thickness;
    difference(){
        union(){
            spiral();
            linear_extrude(d)
            polygon([[-r(180),0], [-5,-10], 
                     [10,-10], [30,0], [r(0),0]]);
        }
        rotate(180)
        servo_cutout();
    }
    servo_pin_extension();
}

arm();







