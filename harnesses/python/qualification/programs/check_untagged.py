# CP-POSING: incremental
# A constants block in the old form: an entry with no '# stage k' line.
# CONSTANTS BEGIN
A_VALUE = 3
# CONSTANTS END
while (s := cp.stage()) is not None:
    cp.answer(s.constants)
