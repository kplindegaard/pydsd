# Base properties
m = 1.0  # System mass
k = 1.0  # Spring stiffness
zeta = 0.01  # Damping factor, d will be auto-calculated
h = 0.1  # Sampling interval [s]

# Derived properties
omega = (k/m)**0.5
d = 2*m*omega*zeta

# Number of cycles
MAX_CYCLES = 1000
