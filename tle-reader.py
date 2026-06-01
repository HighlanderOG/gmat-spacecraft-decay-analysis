from sgp4.api import Satrec, jday

TLE1 = "1 45568U 20025AP  26152.73507564  .09883348  12554-4  24468-3 0  9991"
TLE2 = "2 45568  53.0178 328.0597 0007364 287.1114  72.9127 16.45563244339443"

satellite = Satrec.twoline2rv(TLE1, TLE2)

jd = satellite.jdsatepoch
fr = satellite.jdsatepochF

print(f"Julian Date: {(jd + fr)}")
print(f"Modded Julian Date: {(jd + fr) - 2400000.5}")
print(f"GMAT Modified Julian Date: {(jd + fr) - 2430000}")

error, position, velocity = satellite.sgp4(jd, fr)

# POSITION AND VELOCITY VECTORS in TEME FRAME
print(f"Error code: {error}")
print(f"Position (km): {position}")
print(f"Velocity (km/s): {velocity}")
