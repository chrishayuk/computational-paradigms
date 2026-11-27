# CP-POSING: incremental
# A program whose only effects would be to write a file and print a marker.
# harnesses/python/check must leave no trace of either.
__import__("os").close(__import__("os").open("/tmp/cp-check-marker-file", 65))  # O_CREAT | O_WRONLY
print("CP-CHECK-MARKER-PRINTED")
while (s := cp.stage()) is not None:
    pass
