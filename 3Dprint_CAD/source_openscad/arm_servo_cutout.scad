d1 = 17;
d = 4;
m1 = 8;
m2 = 6;
l1 = 17;
l2 = 14;
fn = 50;

module L(){
    union(){
        polygon([[0,-m1/2], [0,m1/2], 
                 [-l1,d/2], [-l1,-d/2]]);
        translate([-l1,0])
        circle(d/2, $fn=fn);
    }
}
module R(){
    union(){
        polygon([[0,-m2/2], [0,m2/2], 
                [l2,d/2], [l2,-d/2]]);
        translate([l2,0])
        circle(d/2, $fn=fn);
    }
}
module M(){
    l = d1-d;
    union(){
        polygon([[d/2,-l/2], [d/2,l/2], 
                 [-d/2,l/2], [-d/2,-l/2]]);
        translate([0,l/2])
        circle(d/2, $fn=fn);
        translate([0,-l/2])
        circle(d/2, $fn=fn);
    }
}

module servo_cutout(){
    difference(){
        linear_extrude(2){
            L();
            R();
            M();
        }
        union(){
            translate([0,0,1])
            linear_extrude(2){
                circle(2.5, $fn=fn);
            }
            translate([0,0,0])
            linear_extrude(1){
                circle(1, $fn=fn);
            }
        }
    }
}



module servo_pin_extension(){
    h_pin = 4;
    translate([0,0,-h_pin])
    cylinder(h_pin,1, $fn=fn);
}

servo_cutout();
servo_pin_extension();












