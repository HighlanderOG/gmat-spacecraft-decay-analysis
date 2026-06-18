from sgp4.api import Satrec, jday
import os
import sys

# Placeholder paths (enter the actual paths to your GMAT installation and script)
sys.path.append("/home/.../GMAT/R2026a/api")
sys.path.append("/home/.../GMAT/R2026a/bin")
os.environ["LD_LIBRARY_PATH"] = "/home/.../GMAT/R2026a/lib"
script = "/home/.../gmat-spacecraft-decay-analysis/reentry-analysis.script"
report_file = "/home/.../GMAT/R2026a/output/DecayAnalysisReportFile.txt"

# GMAT API imports
import load_gmat  # type: ignore # noqa: E402
import gmatpy as gmat  # type: ignore # noqa: E402

# Example TLE data for a satellite (replace with actual TLE data)
line1 = "1 46326U 20062B   26166.58087730  .06741012  12281-4  80525-3 0  9992"
line2 = "2 46326  53.0183 198.6201 0007139 294.2691  65.7607 16.35644660320448"
TLE = Satrec.twoline2rv(line1, line2)

# Other satellite parameters
drag_coefficient = 2.2
dry_mass = 248  # kg
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
print(f"Drag area (m^2): {area}")

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
print(f"Report file has been added/updated in {report_file}")

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
