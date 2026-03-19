from bridge.bridge_protocol import InterlangBridge

bridge = InterlangBridge(mode="cdp", wait=30)

bridge.bootstrap()

print("Running protocol test...\n")

# Step 1: ping
r1 = bridge.send(". test")
print("TEST:", r1["parsed"]["raw"])

# Step 2: ask version
r2 = bridge.send(". ? q vers -> state")
print("VERS:", r2["parsed"]["raw"])

# Step 3: propose rule
r3 = bridge.send(". prop ^ = xor")
print("PROP:", r3["parsed"]["raw"])

# Step 4: sync state
sync = bridge.sync_message()
r4 = bridge.send(sync)
print("SYNC:", r4["parsed"]["raw"])

# Step 5: dictionary sync
print("\n[DICT SYNC]")
dmsg = bridge.sync_dictionary()
r5 = bridge.send(dmsg)
print("DICT SENT:", dmsg)
print("RESP:", r5["parsed"]["raw"])

# Save logs
bridge.save_log()

print("\nDone.")
