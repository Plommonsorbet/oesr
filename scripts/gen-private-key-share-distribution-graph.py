#!/usr/bin/env python3

COLORS = [ "crimson", "tan", "darkgray", "goldenrod", "darkgray", "thistle", "aquamarine", "rosybrown" ]
PEOPLE = [ "Fred-Roberts", "Fredrick-Gilbert", "Duane-Mcdaniel", "Rochelle-Jordan", "Omar-Scott", "Ellis-Griffith", "Wilbert-Gibson", "Beth-Fleming" ]

print("digraph G {")
for i, person in enumerate(PEOPLE):
    print(f'p_{i} [label="{person}" shape=egg]')

for i in range(0, len(PEOPLE)):
    color = COLORS[i]
    for j in range(0, len(PEOPLE)):
        if i != j:
            if PEOPLE[i] == PEOPLE[0]:
                print(f'p_{i} -> p_{j} [color="{color}" penwidth=2 headlabel="share" labelfontsize=20 labelloc="t" z=100 labeldistance=5]')
            else:
                print(f'p_{i} -> p_{j} [color="{color}" style=dashed]')
print("}")
