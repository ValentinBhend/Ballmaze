/*
Author: Lukas M. Süss aka mechadense
License: CC-BY-SA-4.0
Description: 
Variation on tracta joint

This joint is 
- symmetric
- clip-on
- self-centering => o wobble or backlash
- resistant against torsion
- resistant against pressure
- not very resistant against tension
*/

use <CLIP.scad>
include <config.scad>;

$fa = 2; $fs = 0.5;
eps = 0.05;

own_globalfit = 1.01; //own for tighter fitting <1: tight
in_board_margin = 0.95;

// critical clip parameters
// optimal parameters strongly dependent on the material used
// ideally nylon (PA) or delrin (POM)
// PET sub-ideal but still better than PLA 
clrglobal = 0.15; // <<<<<<<<<<< CRITICAL for slottogether 0.15 standatrd
aglobal = 35; // <<<<<<<<<< CRITICAL clipover angle (12.5 a bit low)
tclipglobal = 5; // <<<<<<<<<< CRITICAL clip thickness 

// Main geometry parameters
tgrooveglobal = 3;
h0 = 14; // keep big enough to retain straight section in the middle
rmin = 14; // <<<<<<<<<<<<<<<




printplate();
//demoassembly();



module printplate()
{
  translate([rmin,rmin*1.25,0])
  {
    sleeve();
    translate([rmin*1.5,0,0]) slider(clrglobal);
  }
}

module demoassembly()
{
  sleeve();
  color([0.5,0.4,0.8]) rotate(90,[1,0,0]) rotate(180,[0,0,1]) 
    sleeve();

  slider(clrglobal);
  color("yellow") rotate(90,[1,0,0]) rotate(180,[0,0,1]) 
    slider(clrglobal);
}

module sleeve
  (
    a=aglobal // critical clipping angle <<<<<<<<<<<<<<<<<<<
  )
{
  //f=2/3;
  f=1;
  difference()
  {
    color([0.4,0.6,0.8]) //bcyl(14,h0+2*t2,2);
    union()
    {
      cutter(off=tclipglobal, cutoff1=0, cutoff2=0);
      color([1,1,1]*0.8) translate([-30,0,0]) 
        endplate(w=h0*f,h=h0);
    }
    
    color("red")
    rotate(-a,[0,0,1]) translate([50,+50,0])
      cube([100,100,100],center=true);
    color("red")
    rotate(+a,[0,0,1]) translate([50,-50,0]) 
      cube([100,100,100],center=true);
    scale([own_globalfit,own_globalfit,1])
    cutter(off=0, cutoff1=0, cutoff2 =1.0);
  }
}

module slider(t2=2,clr=0.15)
{
  difference()
  {
    cutter();
    // rectangular slot in cutout
    translate([rmin*2,0,0])
      cube([rmin*4, h0+clr*2, h0*1.2],center=true);
    // cut it hollow to save more material
    // needs more work so left for later ... evetually 
    //cutter(off=-2, cutoff1=1.0, cutoff2=0);
    //bcyl(rmin-1,h0+2*t2,2);
 
  }
}

module cutter(off=0, cutoff1=1.0, cutoff2 = 0.0, tgroove=tgrooveglobal)
{
  r2 = rmin+tgroove-cutoff1;
  translate([0,0,+h0/2-(2*tgroove)/2])
    bcyl(r2+cutoff1/2+off, 2*tgroove, tgroove-0.05-cutoff1/2);
  translate([0,0,-h0/2+(2*tgroove)/2])
    bcyl(r2+cutoff1/2+off, 2*tgroove, tgroove-0.05-cutoff1/2);
  color("orange") bcyl(rmin+cutoff2+off,h0+cutoff2-eps,0.5);
}



module bcyl(rr,hh,bb)
{
  hull()
  {
    cylinder(r=rr-00,h=hh-2*bb,center=true);    
    cylinder(r=rr-bb,h=hh-2*00,center=true);    
  }  
}

// just a simple X shaped strut for demo purpouses
// can be replaced byanything really
//color([1,1,1]*0.8) translate([-30,0,0]) crossstrut(w=h0*0.666,h=h0);
module crossstrut(t=1.5,w=6,h=10,l=60)
{
  hull()
  {
    translate([0,+w/2,+(h/2-t/2)]) cube([l,t,t],center=true);
    translate([0,-w/2,-(h/2-t/2)]) cube([l,t,t],center=true);
  }
  
  hull()
  {
    translate([0,-w/2,+(h/2-t/2)]) cube([l,t,t],center=true);
    translate([0,+w/2,-(h/2-t/2)]) cube([l,t,t],center=true);
  }
}



module endplate(t=1.5,w=6,h=10,l=60) //w=h0*f,h=h0
{
    d = 5;
    union(){
        translate([15,0,0])
        cube([14,40,h], center=true);
        translate([7-3*clip_scale,0,0])
        rotate([0,90,0])
        scale(clip_scale*in_board_margin)
        clip_cutout(10);
        //cylinder(h = 3, r1 = 20, r2 = 20, center = true);
        //cube([3,40,40], center=true);
    }
}




