from sgp4.api import Satrec, jday
import os
import sys

# GMAT placeholder paths (enter the actual paths to your GMAT installation)
sys.path.append("/home/.../GMAT/R2026a/api")
sys.path.append("/home/.../GMAT/R2026a/bin")
os.environ["LD_LIBRARY_PATH"] = "/home/.../GMAT/R2026a/lib"

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
rho = 1e-12  # kg/m^3, very low density for high altitude
# m^2, using the bstar parameter to estimate the area
area = TLE.bstar * (2 * dry_mass) / (drag_coefficient * 0.15696615)

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

#########################
# GMAT reentry analysis #
#########################
gmat.Setup("")

# Spacecraft (units in km/kg)
sat = gmat.Construct("Spacecraft", "Satellite")
sat.SetField("DateFormat", "UTCModJulian")
sat.SetField("Epoch", str(gmat_mod_jdate))
sat.SetField("CoordinateSystem", "TEME")
sat.SetField("X", position[0])
sat.SetField("Y", position[1])
sat.SetField("Z", position[2])
sat.SetField("VX", velocity[0])
sat.SetField("VY", velocity[1])
sat.SetField("VZ", velocity[2])
sat.SetField("DryMass", dry_mass)
sat.SetField("Cd", drag_coefficient)
sat.SetField("Cr", 1.8)
sat.SetField("DragArea", area)
sat.SetField("SRPArea", area)
sat.SetField("OrbitErrorCovariance",  (1e+70, 0, 0, 0, 0, 0,
                                       0, 1e+70, 0, 0, 0, 0,
                                       0, 0, 1e+70, 0, 0, 0,
                                       0, 0, 0, 1e+70, 0, 0,
                                       0, 0, 0, 0, 1e+70, 0,
                                       0, 0, 0, 0, 0, 1e+70))
sat.SetField("Id", 'SatId')
sat.SetField("Attitude", "CoordinateSystemFixed")

# ForceModels
sat_force_model = gmat.Construct("ForceModel", "SatPropagator_ForceModel")
sat_force_model.SetField("CentralBody", "Earth")

earth_gravity = gmat.Construct("GravityField", "Earth10x10")
earth_gravity.SetField("BodyName", "Earth")
earth_gravity.SetField(
    "PotentialFile", "/home/.../GMAT/R2026a/data/gravity/earth/JGM2.cof")
earth_gravity.SetField("Degree", 10)
earth_gravity.SetField("Order", 10)

moon_gravity = gmat.Construct("GravityField", "MoonGravity")
moon_gravity.SetField("BodyName", "Luna")
sun_gravity = gmat.Construct("GravityField", "SunGravity")
sun_gravity.SetField("BodyName", "Sun")

drag_model = gmat.Construct("DragForce", "DragModel")
drag_model.SetField("AtmosphereModel", "MSISE90")

atmosphere = gmat.Construct("MSISE90", "Atmosphere")
drag_model.SetReference(atmosphere)

srp = gmat.Construct("SolarRadiationPressure", "SRPModel")

sat_force_model.AddForce(earth_gravity)
sat_force_model.AddForce(moon_gravity)
sat_force_model.AddForce(sun_gravity)
sat_force_model.AddForce(drag_model)
sat_force_model.AddForce(srp)


# Propagators
sat_propagator = gmat.Construct("Propagator", "SatPropagator")
