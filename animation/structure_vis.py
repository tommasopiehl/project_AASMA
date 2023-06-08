import json

# [0 = wait for seat, 1 = waiting for food, 2 = eating, 3 = waiting for bill]   guest
#0 = not made, 1 = waiting, 2 = cooking, 3 = done, 4 = served   plate
#0 = free, 1 = taken   table

data = []

num_batch = 0
num_time = 0

add_data = {
    "batch": num_batch,
    "time": num_time,
    "current": [0, 0, 0, 0, 0, 0, 0, 0, 0]
}

#data[batch, time] = [guest1 4, guest2 4, guest3 4, plate1 4, plate2 4, plate3 4, table1 2, table2 2, table3 2]

#with open("file.json", "w") as json_file:
#    json.dump(data, json_file)
#    json_file.close()

with open("states.json", "r") as json_file:
    data = json.load(json_file)

print(len(data))
