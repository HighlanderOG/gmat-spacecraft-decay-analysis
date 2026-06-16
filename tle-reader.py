from sgp4.api import Satrec, jday
import os
import sys

# GMAT placeholder paths (enter the actual paths to your GMAT installation)
sys.path.append("/home/.../GMAT/R2026a/api")
sys.path.append("/home/.../GMAT/R2026a/bin")
os.environ["LD_LIBRARY_PATH"] = "/home/.../GMAT/R2026a/lib"
script = "/home/.../gmat-spacecraft-decay-analysis/reentry-analysis.script"

# GMAT API imports
import load_gmat  # type: ignore # noqa: E402
import gmatpy as gmat  # type: ignore # noqa: E402

# Example TLE data for a satellite (replace with actual TLE data)
line1 = "1 45568U 20025AP  26152.73507564  .09883348  12554-4  24468-3 0  9991"
line2 = "2 45568  53.0178 328.0597 0007364 287.1114  72.9127 16.45563244339443"
TLE = Satrec.twoline2rv(line1, line2)

# Other satellite parameters
drag_coefficient = 2.2
dry_mass = 450  # kg
area = TLE.bstar * (2 * dry_mass) / (drag_coefficient * 0.15696615)  # m^2

jd = TLE.jdsatepoch
fr = TLE.jdsatepochF

# Julian Dates
jdate = jd+fr
mod_jdate = jdate - 2400000.5
gmat_mod_jdate = jdate - 2430000

print(f"Julian Date: {jdate}")
print(f"Modded Julian Date: {mod_jdate}")
print(f"GMAT Modified Julian Date: {gmat_mod_jdate}")

error, position, velocity = TLE.sgp4(jd, fr)

# Position and velocity vectors in the TEME frame (km and km/s)
print(f"Error code: {error}")
print(f"Position (km): {position}")
print(f"Velocity (km/s): {velocity}")

# GMAT reentry analysis
gmat.Setup("")

gmat.LoadScript(script)
gmat.Initialize()

gmat.ShowObjects()
sat = gmat.GetObject("Satellite")

# Set position
sat.SetField("X", position[0])
sat.SetField("Y", position[1])
sat.SetField("Z", position[2])

# Set velocity
sat.SetField("VX", velocity[0])
sat.SetField("VY", velocity[1])
sat.SetField("VZ", velocity[2])

# Set ballistics
sat.SetField("DryMass", dry_mass)
sat.SetField("DragArea", area)
sat.SetField("Cd", drag_coefficient)

# Set Epoch
sat.SetField("Epoch", str(gmat_mod_jdate))

print("Running simulation...")
success = gmat.RunScript()
if success:
    print("Simulation complete!")
else:
    print("Simulation failed or ended prematurely: error or accuracy violation occurred.")

# Final position
x = gmat.GetRuntimeObject("Satellite.TEME.X").GetRealParameter("Value")
y = gmat.GetRuntimeObject("Satellite.TEME.Y").GetRealParameter("Value")
z = gmat.GetRuntimeObject("Satellite.TEME.Z").GetRealParameter("Value")
final_position = (x, y, z)

# Final velocity
vx = gmat.GetRuntimeObject("Satellite.TEME.VX").GetRealParameter("Value")
vy = gmat.GetRuntimeObject("Satellite.TEME.VY").GetRealParameter("Value")
vz = gmat.GetRuntimeObject("Satellite.TEME.VZ").GetRealParameter("Value")
final_velocity = (vx, vy, vz)

print(f"Final Position (km): {final_position}")
print(f"Final Velocity (km/s): {final_velocity}")
