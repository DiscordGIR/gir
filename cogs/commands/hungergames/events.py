events = {

    'bloodbath': {
        'title': "The Bloodbath",
        'description': "As the tributes stand on their podiums, the horn sounds.",
        'color': 0x9f0000,
        'nonfatal': [
            {
                'msg': "{0} grabs a shovel.",
                'tributes': 1
            },
            {
                'msg': "{0} grabs a backpack and retreats.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} fight for a bag. {0} gives up and retreats.",
                'tributes': 2
            },
            {
                'msg': "{0} and {1} fight for a bag. {1} gives up and retreats.",
                'tributes': 2
            },
            {
                'msg': "{0} finds a bow, some arrows, and a quiver.",
                'tributes': 1
            },
            {
                'msg': "{0} runs into the Cornucopia and hides.",
                'tributes': 1
            },
            {
                'msg': "{0} takes a handful of throwing knives.",
                'tributes': 1
            },
            {
                'msg': "{0} rips a mace out of {1}'s hands",
                'tributes': 2
            },
            {
                'msg': "{0} finds a canteen full of water.",
                'tributes': 1
            },
            {
                'msg': "{0} stays at the Cornucopia for resources.",
                'tributes': 1
            },
            {
                'msg': "{0} gathers as much food as {0.he_she} can.",
                'tributes': 1
            },
            {
                'msg': "{0} grabs a sword.",
                'tributes': 1
            },
            {
                'msg': "{0} takes a spear from inside the Cornucopia.",
                'tributes': 1
            },
            {
                'msg': "{0} finds a bag full of explosives.",
                'tributes': 1
            },
            {
                'msg': "{0} clutches a first aid kit and runs away.",
                'tributes': 1
            },
            {
                'msg': "{0} takes a sickle from inside the Cornucopia.",
                'tributes': 1
            },
            {
                'msg': "{0}, {1}, and {2} work together to get as many supplies as possible.",
                'tributes': 3
            },
            {
                'msg': "{0} runs away with a lighter and some rope.",
                'tributes': 1
            },
            {
                'msg': "{0} snatches a bottle of alcohol and a rag.",
                'tributes': 1
            },
            {
                'msg': "{0} finds a backpack full of camping equipment.",
                'tributes': 1
            },
            {
                'msg': "{0} grabs a backpack, not realizing it is empty.",
                'tributes': 1
            },
            {
                'msg': "{0} breaks {1}'s nose for a basket of bread.",
                'tributes': 2
            },
            {
                'msg': "{0}, {1}, {2}, and {3} share everything they gathered before running.",
                'tributes': 4
            },
            {
                'msg': "{0} receives a trident from inside the Cornucopia.",
                'tributes': 1
            },
            {
                'msg': "{0} grabs a jar of fishing bait while {1} gets fishing gear.",
                'tributes': 2
            },
            {
                'msg': "{0} scares {1} away from the Cornucopia.",
                'tributes': 2
            },
            {
                'msg': "{0} grabs a shield leaning on the Cornucopia.",
                'tributes': 1
            },
            {
                'msg': "{0} snatches a pair of sais.",
                'tributes': 1
            },
        ],
        'fatal': [
            {
                'msg': "{0} steps off {0.his_her} podium too soon and blows up.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} throws a knife into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} accidentally steps on a landmine.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} catches {1} off guard and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} work together to drown {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} strangles {1} after engaging in a fist fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} cannot handle the circumstances and commits suicide.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} bashes {1}'s head against a rock several times.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} snaps {1}'s neck.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} decapitates {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} spears {1} in the abdomen.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets {1} on fire with a molotov.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a pit and dies.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} stabs {1} while {1.his_her} back is turned.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1}, but puts {1.him_her} out of {1.his_her} misery.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1} and leaves {1.him_her} to die.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bashes {1}'s head in with a mace.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} pushes {1} off a cliff during a knife fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} throws a knife into {1}'s chest.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} is unable to convince {1} to not kill {0.him_her}.",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} convinces {1} not to kill {0.him_her}, only to kill {1.him_her} instead.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a frozen lake and drowns.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0}, {1}, and {2} start fighting, but {1} runs away as {0} kills {2}.",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} kills {1} with {1.his_her} own weapon.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} overpowers {1}, killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1} and {2}",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, and {3}.",
                'tributes': 4,
                'killer': [0],
                'killed': [1, 2, 3]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, {3}, and {4}",
                'tributes': 5,
                'killer': [0],
                'killed': [1, 2, 3, 4]
            },
            {
                'msg': "{0} kills {1} as {1.he_she} tries to run.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} threaten a double suicide. It fails and they die.",
                'tributes': 2,
                'killer': None,
                'killed': [0, 1]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} form a suicide pact, killing themselves.",
                'tributes': 4,
                'killer': None,
                'killed': [0, 1, 2, 3]
            },
            {
                'msg': "{0} kills {1} with a hatchet.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {0} and {1} survive.",
                'tributes': 4,
                'killer': [0, 1],
                'killed': [2, 3]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {2} and {3} survive.",
                'tributes': 4,
                'killer': [2, 3],
                'killed': [0, 1]
            },
            {
                'msg': "{0} attacks {1}, but {2} protects {1.him_her}, killing {0}",
                'tributes': 3,
                'killer': [2],
                'killed': [0]
            },
            {
                'msg': "{0} severely slices {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} strangles {1} with a rope",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} kills {1} for {1.his_her} supplies.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow at {1}, but misses and kills {2} instead",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} shoots a poisonous blow dart into {1}'s neck, slowly killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} stabs {1} wth a tree branch.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} stabs {1} in the back with a trident.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {0} triumphantly kills them both.",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {1} triumphantly kills them both.",
                'tributes': 3,
                'killer': [1],
                'killed': [0, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {2} triumphantly kills them both.",
                'tributes': 3,
                'killer': [2],
                'killed': [0, 1]
            },
            {
                'msg': "{0} finds {1} hiding in the Cornucopia and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} finds {1} hiding in the Cornucopia, but {1} kills {0.him_her}",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} kills {1} with a sickle.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} fight for a bag. {0} strangles {1} with the straps and runs.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} fight for a bag. {1} strangles {0} with the straps and runs.",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} repeatedly stabs {1} to death with sais.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
        ]
    },

    'day': {
        'title': "Day {0}",
        'description': None,
        'color': 0xf9eb0f,
        'nonfatal': [
            {
                'msg': "{0} goes hunting.",
                'tributes': 1
            },
            {
                'msg': "{0} injures {0.himself_herself}",
                'tributes': 1
            },
            {
                'msg': "{0} explores the arena.",
                'tributes': 1
            },
            {
                'msg': "{0} scares {1} off.",
                'tributes': 2
            },
            {
                'msg': "{0} diverts {1}'s attention and runs away.",
                'tributes': 2
            },
            {
                'msg': "{0} stalks {1}.",
                'tributes': 2
            },
            {
                'msg': "{0} fishes.",
                'tributes': 1
            },
            {
                'msg': "{0} camouflages {0.himself_herself} in the bushes.",
                'tributes': 1
            },
            {
                'msg': "{0} steals from {1} while {1.he_she} isn't looking.",
                'tributes': 2
            },
            {
                'msg': "{0} makes a wooden spear.",
                'tributes': 1
            },
            {
                'msg': "{0} discovers a cave.",
                'tributes': 1
            },
            {
                'msg': "{0} attacks {1}, but {1.he_she} manages to escape.",
                'tributes': 2
            },
            {
                'msg': "{0} chases {1}.",
                'tributes': 2
            },
            {
                'msg': "{0} runs away from {1}.",
                'tributes': 2
            },
            {
                'msg': "{0} collects fruit from a tree.",
                'tributes': 1
            },
            {
                'msg': "{0} receives a hatchet from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} receives clean water from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} receives medical supplies from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} receives fresh food from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} searches for a water source.",
                'tributes': 1
            },
            {
                'msg': "{0} defeats {1} in a fight, but spares {1.his_her} life.",
                'tributes': 2
            },
            {
                'msg': "{0} and {1} work together for the day.",
                'tributes': 2
            },
            {
                'msg': "{0} begs for {1} to kill {0.him_her}. {1.he_she_cap} refuses, keeping {0} alive.",
                'tributes': 2
            },
            {
                'msg': "{0} tries to sleep through the entire day.",
                'tributes': 1
            },
            {
                'msg': "{0}, {1}, {2}, and {3} raid {4}'s camp while {4.he_she} is hunting.",
                'tributes': 5
            },
            {
                'msg': "{0} constructs a shack.",
                'tributes': 1
            },
            {
                'msg': "{0} overhears {1} and {2} talking in the distance.",
                'tributes': 3
            },
            {
                'msg': "{0} practices {0.his_her} archery.",
                'tributes': 1
            },
            {
                'msg': "{0} thinks about home.",
                'tributes': 1
            },
            {
                'msg': "{0} is pricked by thorns while picking berries.",
                'tributes': 1
            },
            {
                'msg': "{0} tries to spear fish with a trident.",
                'tributes': 1
            },
            {
                'msg': "{0} searches for firewood.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} split up to search for resources.",
                'tributes': 2
            },
            {
                'msg': "{0} picks flowers.",
                'tributes': 1
            },
            {
                'msg': "{0} tends to {1}'s wounds.",
                'tributes': 2
            },
            {
                'msg': "{0} sees smoke rising in the distance, but decides not to investigate.",
                'tributes': 1
            },
            {
                'msg': "{0} sprains {0.his_her} ankle while running away from {1}.",
                'tributes': 2
            },
            {
                'msg': "{0} makes a slingshot.",
                'tributes': 1
            },
            {
                'msg': "{0} travels to higher ground.",
                'tributes': 1
            },
            {
                'msg': "{0} discovers a river.",
                'tributes': 1
            },
            {
                'msg': "{0} hunts for other tributes.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} hunt for other tributes.",
                'tributes': 2
            },
            {
                'msg': "{0}, {1}, and {2} hunt for other tributes.",
                'tributes': 3
            },
            {
                'msg': "{0}, {1}, {2}, and {3} hunt for other tributes.",
                'tributes': 4
            },
            {
                'msg': "{0}, {1}, {2}, {3}, and {4} hunt for other tributes.",
                'tributes': 5
            },
            {
                'msg': "{0} receives an explosive from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} questions {0.his_her} sanity.",
                'tributes': 1
            },
        ],
        'fatal': [
            {
                'msg': "{0} catches {1} off guard and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} throws a knife into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} begs for {1} to kill {0.him_her}. {1} reluctantly obliges, killing {0}",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} and {1} work together to drown {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} strangles {1} after engaging in a fist fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bleeds out due to untreated injuries.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} cannot handle the circumstances and commits suicide.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} bashes {1}'s head against a rock several times.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} unknowingly eats toxic berries.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} silently snaps {1}'s neck.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} taints {1}'s food, killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} decapitates {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} dies from an infection.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} spears {1} in the abdomen.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets {1} on fire with a molotov.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a pit and dies.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} stabs {1} while {1.his_her} back is turned.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1}, but puts {1.him_her} out of {1.his_her} misery.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1} and leaves {1.him_her} to die.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bashes {1}'s head in with a mace.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} attempts to climb a tree, but falls to {0.his_her} death.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} pushes {1} off a cliff during a knife fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} throws a knife into {1}'s chest.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}'s trap kills {1}",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} kills {1} while {1.he_she} is resting.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} is unable to convince {1} to not kill {0.him_her}.",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} convinces {1} not to kill {0.him_her}, only to kill {1.him_her} instead.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a frozen lake and drowns.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0}, {1}, and {2} start fighting, but {1} runs away as {0} kills {2}.",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} kills {1} with {1.his_her} own weapon.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} overpowers {1}, killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1} and {2}",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, and {3}.",
                'tributes': 4,
                'killer': [0],
                'killed': [1, 2, 3]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, {3}, and {4}",
                'tributes': 5,
                'killer': [0],
                'killed': [1, 2, 3, 4]
            },
            {
                'msg': "{0} kills {1} as {1.he_she} tries to run.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} threaten a double suicide. It fails and they die.",
                'tributes': 2,
                'killer': None,
                'killed': [0, 1]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} form a suicide pact, killing themselves.",
                'tributes': 4,
                'killer': None,
                'killed': [0, 1, 2, 3]
            },
            {
                'msg': "{0} dies from hypothermia.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} dies from hunger.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} dies from thirst.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} kills {1} with a hatchet.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {0} and {1} survive.",
                'tributes': 4,
                'killer': [0, 1],
                'killed': [2, 3]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {2} and {3} survive.",
                'tributes': 4,
                'killer': [2, 3],
                'killed': [0, 1]
            },
            {
                'msg': "{0} dies trying to escape the arena.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} dies of dysentery.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} accidentally detonates a land mine while trying to arm it.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} attacks {1}, but {2} protects {1.him_her}, killing {0}",
                'tributes': 3,
                'killer': [2],
                'killed': [0]
            },
            {
                'msg': "{0} ambushes {1} and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} accidentally steps on a landmine.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} severely slices {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} strangles {1} with a rope",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} kills {1} for {1.his_her} supplies.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow at {1}, but misses and kills {2} instead",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} shoots a poisonous blow dart into {1}'s neck, slowly killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, and {2} successfully ambush and kill {3}, {4}, and {5}.",
                'tributes': 6,
                'killer': [0, 1, 2],
                'killed': [3, 4, 5]
            },
            {
                'msg': "{0}, {1}, and {2} unsuccessfully ambush {3}, {4}, and {5}, who kill them instead.",
                'tributes': 6,
                'killer': [3, 4, 5],
                'killed': [0, 1, 2]
            },
            {
                'msg': "{0} stabs {1} wth a tree branch.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} forces {1} to kill {2} or {3}. {1.he_she_cap} decides to kill {2}.",
                'tributes': 4,
                'killer': [1],
                'killed': [2]
            },
            {
                'msg': "{0} forces {1} to kill {2} or {3}. {1.he_she_cap} decides to kill {3}.",
                'tributes': 4,
                'killer': [1],
                'killed': [3]
            },
            {
                'msg': "{0} forces {1} to kill {2} or {3}. {1.he_she_cap} refuses to kill, so {0} kills {1.him_her} "
                       "instead.",
                'tributes': 4,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} poisons {1}'s drink, but mistakes it for {0.his_her} own and dies.",
                'tributes': 2,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} poisons {1}'s drink. {1.he_she_cap} drinks it and dies.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} stabs {1} in the back with a trident.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} attempts to climb a tree, but falls on {1}, killing them both.",
                'tributes': 2,
                'killer': None,
                'killed': [0, 1]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {0} triumphantly kills them both.",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {1} triumphantly kills them both.",
                'tributes': 3,
                'killer': [1],
                'killed': [0, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {2} triumphantly kills them both.",
                'tributes': 3,
                'killer': [2],
                'killed': [0, 1]
            },
            {
                'msg': "{0} kills {1} with a sickle.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, {2}, {3}, and {4} track down and kill {5}.",
                'tributes': 6,
                'killer': [0, 1, 2, 3, 4],
                'killed': [5]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} track down and kill {4}.",
                'tributes': 5,
                'killer': [0, 1, 2, 3],
                'killed': [4]
            },
            {
                'msg': "{0}, {1}, and {2} track down and kill {3}.",
                'tributes': 4,
                'killer': [0, 1, 2],
                'killed': [3]
            },
            {
                'msg': "{0} and {1} track down and kill {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} tracks down and kills {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} repeatedly stabs {1} to death with sais.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
        ]
    },

    'night': {
        'title': "Night {0}",
        'description': None,
        'color': 0x001233,
        'nonfatal': [
            {
                'msg': "{0} starts a fire.",
                'tributes': 1
            },
            {
                'msg': "{0} sets up camp for the night.",
                'tributes': 1
            },
            {
                'msg': "{0} loses sight of where {0.he_she} is.",
                'tributes': 1
            },
            {
                'msg': "{0} climbs a tree to rest.",
                'tributes': 1
            },
            {
                'msg': "{0} goes to sleep.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} tell stories about themselves to each other.",
                'tributes': 2
            },
            {
                'msg': "{0}, {1}, {2}, and {3} sleep in shifts.",
                'tributes': 4
            },
            {
                'msg': "{0}, {1}, and {2} sleep in shifts.",
                'tributes': 3
            },
            {
                'msg': "{0} and {1} sleep in shifts.",
                'tributes': 2
            },
            {
                'msg': "{0} tends to {0.his_her} wounds.",
                'tributes': 1
            },
            {
                'msg': "{0} sees a fire, but stays hidden.",
                'tributes': 1
            },
            {
                'msg': "{0} screams for help.",
                'tributes': 1
            },
            {
                'msg': "{0} stays awake all night.",
                'tributes': 1
            },
            {
                'msg': "{0} passes out from exhaustion.",
                'tributes': 1
            },
            {
                'msg': "{0} cooks {0.his_her} food before putting {0.his_her} fire out.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} run into each other and decide to truce for the night.",
                'tributes': 2
            },
            {
                'msg': "{0} fends {1}, {2}, and {3} away from {0.his_her} fire.",
                'tributes': 4
            },
            {
                'msg': "{0}, {1}, and {2} discuss the games and what might happen in the morning.",
                'tributes': 3
            },
            {
                'msg': "{0} cries {0.himself_herself} to sleep.",
                'tributes': 1
            },
            {
                'msg': "{0} tries to treat {0.his_her} infection.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} talk about the tributes still alive.",
                'tributes': 2
            },
            {
                'msg': "{0} is awoken by nightmares.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} huddle for warmth.",
                'tributes': 2
            },
            {
                'msg': "{0} thinks about winning.",
                'tributes': 1
            },
            {
                'msg': "{0}, {1}, {2}, and {3} tell each other ghost stories to lighten the mood.",
                'tributes': 4
            },
            {
                'msg': "{0} looks at the night sky.",
                'tributes': 1
            },
            {
                'msg': "{0} defeats {1} in a fight, but spares {1.his_her} life.",
                'tributes': 2
            },
            {
                'msg': "{0} begs for {1} to kill {0.him_her}. {1.he_she_cap} refuses, keeping {0} alive.",
                'tributes': 2
            },
            {
                'msg': "{0} destroys {1}'s supplies while {1.he_she} is asleep.",
                'tributes': 2
            },
            {
                'msg': "{0}, {1}, {2}, {3}, and {4} sleep in shifts.",
                'tributes': 5
            },
            {
                'msg': "{0} lets {1} into {0.his_her} shelter.",
                'tributes': 2
            },
            {
                'msg': "{0} receives a hatchet from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} receives clean water from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} receives medical supplies from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} receives fresh food from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} tries to sing {0.himself_herself} to sleep.",
                'tributes': 1
            },
            {
                'msg': "{0} attempts to start a fire, but is unsuccessful.",
                'tributes': 1
            },
            {
                'msg': "{0} thinks about home.",
                'tributes': 1
            },
            {
                'msg': "{0} tends to {1}'s wounds.",
                'tributes': 2
            },
            {
                'msg': "{0} quietly hums.",
                'tributes': 1
            },
            {
                'msg': "{0}, {1}, and {2} cheerfully sing songs together.",
                'tributes': 3
            },
            {
                'msg': "{0} is unable to start a fire and sleeps without warmth.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} hold hands.",
                'tributes': 2
            },
            {
                'msg': "{0} convinces {1} to snuggle with {0.him_her}.",
                'tributes': 2
            },
            {
                'msg': "{0} receives an explosive from an unknown sponsor.",
                'tributes': 1
            },
            {
                'msg': "{0} questions {0.his_her} sanity.",
                'tributes': 1
            },
        ],
        'fatal': [
            {
                'msg': "{0} catches {1} off guard and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} throws a knife into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} begs for {1} to kill {0.him_her}. {1} reluctantly obliges, killing {0}",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} and {1} work together to drown {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} strangles {1} after engaging in a fist fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bleeds out due to untreated injuries.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} cannot handle the circumstances and commits suicide.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} bashes {1}'s head against a rock several times.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} unknowingly eats toxic berries.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} silently snaps {1}'s neck.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} taints {1}'s food, killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} decapitates {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} dies from an infection.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} spears {1} in the abdomen.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets {1} on fire with a molotov.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a pit and dies.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} stabs {1} while {1.his_her} back is turned.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1}, but puts {1.him_her} out of {1.his_her} misery.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1} and leaves {1.him_her} to die.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bashes {1}'s head in with a mace.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} attempts to climb a tree, but falls to {0.his_her} death.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} pushes {1} off a cliff during a knife fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} throws a knife into {1}'s chest.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}'s trap kills {1}",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} kills {1} while {1.he_she} is sleeping.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} is unable to convince {1} to not kill {0.him_her}.",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} convinces {1} not to kill {0.him_her}, only to kill {1.him_her} instead.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a frozen lake and drowns.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0}, {1}, and {2} start fighting, but {1} runs away as {0} kills {2}.",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} kills {1} with {1.his_her} own weapon.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} overpowers {1}, killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1} and {2}",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, and {3}.",
                'tributes': 4,
                'killer': [0],
                'killed': [1, 2, 3]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, {3}, and {4}",
                'tributes': 5,
                'killer': [0],
                'killed': [1, 2, 3, 4]
            },
            {
                'msg': "{0} kills {1} as {1.he_she} tries to run.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} threaten a double suicide. It fails and they die.",
                'tributes': 2,
                'killer': None,
                'killed': [0, 1]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} form a suicide pact, killing themselves.",
                'tributes': 4,
                'killer': None,
                'killed': [0, 1, 2, 3]
            },
            {
                'msg': "{0} dies from hypothermia.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} dies from hunger.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} dies from thirst.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} kills {1} with a hatchet.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {0} and {1} survive.",
                'tributes': 4,
                'killer': [0, 1],
                'killed': [2, 3]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {2} and {3} survive.",
                'tributes': 4,
                'killer': [2, 3],
                'killed': [0, 1]
            },
            {
                'msg': "{0} dies trying to escape the arena.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} dies of dysentery.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} accidentally detonates a land mine while trying to arm it.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} attacks {1}, but {2} protects {1.him_her}, killing {0}",
                'tributes': 3,
                'killer': [2],
                'killed': [0]
            },
            {
                'msg': "{0} ambushes {1} and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} accidentally steps on a landmine.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} severely slices {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} strangles {1} with a rope",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} kills {1} for {1.his_her} supplies.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow at {1}, but misses and kills {2} instead",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} shoots a poisonous blow dart into {1}'s neck, slowly killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, and {2} successfully ambush and kill {3}, {4}, and {5}.",
                'tributes': 6,
                'killer': [0, 1, 2],
                'killed': [3, 4, 5]
            },
            {
                'msg': "{0}, {1}, and {2} unsuccessfully ambush {3}, {4}, and {5}, who kill them instead.",
                'tributes': 6,
                'killer': [3, 4, 5],
                'killed': [0, 1, 2]
            },
            {
                'msg': "{0} stabs {1} wth a tree branch.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} forces {1} to kill {2} or {3}. {1.he_she_cap} decides to kill {2}.",
                'tributes': 4,
                'killer': [1],
                'killed': [2]
            },
            {
                'msg': "{0} forces {1} to kill {2} or {3}. {1.he_she_cap} decides to kill {3}.",
                'tributes': 4,
                'killer': [1],
                'killed': [3]
            },
            {
                'msg': "{0} forces {1} to kill {2} or {3}. {1.he_she_cap} refuses to kill, so {0} kills {1.him_her} "
                       "instead.",
                'tributes': 4,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} poisons {1}'s drink, but mistakes it for {0.his_her} own and dies.",
                'tributes': 2,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} poisons {1}'s drink. {1.he_she_cap} drinks it and dies.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} stabs {1} in the back with a trident.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} attempts to climb a tree, but falls on {1}, killing them both.",
                'tributes': 2,
                'killer': None,
                'killed': [0, 1]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {0} triumphantly kills them both.",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {1} triumphantly kills them both.",
                'tributes': 3,
                'killer': [1],
                'killed': [0, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {2} triumphantly kills them both.",
                'tributes': 3,
                'killer': [2],
                'killed': [0, 1]
            },
            {
                'msg': "{0} kills {1} with a sickle.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, {2}, {3}, and {4} track down and kill {5}.",
                'tributes': 6,
                'killer': [0, 1, 2, 3, 4],
                'killed': [5]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} track down and kill {4}.",
                'tributes': 5,
                'killer': [0, 1, 2, 3],
                'killed': [4]
            },
            {
                'msg': "{0}, {1}, and {2} track down and kill {3}.",
                'tributes': 4,
                'killer': [0, 1, 2],
                'killed': [3]
            },
            {
                'msg': "{0} and {1} track down and kill {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} tracks down and kills {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} repeatedly stabs {1} to death with sais.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
        ]
    },

    'feast': {
        'title': "The Feast",
        'description': "The Cornucopia is replenished with food, supplies, weapons, and memoirs from the tributes' "
                       "families.",
        'color': 0x39ea09,
        'nonfatal': [
            {
                'msg': "{0} gathers as much food into a bag as {0.he_she} can before fleeing.",
                'tributes': 1
            },
            {
                'msg': "{0} and {1} decide to work together to get more supplies.",
                'tributes': 2
            },
            {
                'msg': "{0} and {1} get into a fight over raw meat, but {1} gives up and runs away.",
                'tributes': 2
            },
            {
                'msg': "{0} and {1} get into a fight over raw meat, but {0} gives up and runs away.",
                'tributes': 2
            },
            {
                'msg': "{0}, {1}, and {2} confront each other, but grab what they want slowly to avoid conflict.",
                'tributes': 3
            },
            {
                'msg': "{0} destroys {1}'s memoirs out of spite.",
                'tributes': 2
            },
            {
                'msg': "{0}, {1}, {2}, and {3} team up to grab food, supplies, weapons, and memoirs.",
                'tributes': 4
            },
            {
                'msg': "{0} steals {1}'s memoirs.",
                'tributes': 2
            },
            {
                'msg': "{0} takes a staff leaning against the Cornucopia.",
                'tributes': 1
            },
            {
                'msg': "{0} stuffs a bundle of dry clothing into a backpack before sprinting away.",
                'tributes': 1
            },
        ],
        'fatal': [
            {
                'msg': "{0} throws a knife into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} accidentally steps on a landmine.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} catches {1} off guard and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} work together to drown {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} strangles {1} after engaging in a fist fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow into {1}'s head.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bleeds out due to untreated injuries.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} cannot handle the circumstances and commits suicide.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} bashes {1}'s head against a rock several times.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} snaps {1}'s neck.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} decapitates {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} dies from an infection.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} spears {1} in the abdomen.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets {1} on fire with a molotov.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a pit and dies.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0} stabs {1} while {1.his_her} back is turned.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1}, but puts {1.him_her} out of {1.his_her} misery.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely injures {1} and leaves {1.him_her} to die.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} bashes {1}'s head in with a mace.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} pushes {1} off a cliff during a knife fight.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} throws a knife into {1}'s chest.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}'s trap kills {1}",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} is unable to convince {1} to not kill {0.him_her}.",
                'tributes': 2,
                'killer': [1],
                'killed': [0]
            },
            {
                'msg': "{0} convinces {1} not to kill {0.him_her}, only to kill {1.him_her} instead.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} falls into a frozen lake and drowns.",
                'tributes': 1,
                'killer': None,
                'killed': [0]
            },
            {
                'msg': "{0}, {1}, and {2} start fighting, but {1} runs away as {0} kills {2}.",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} kills {1} with {1.his_her} own weapon.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} overpowers {1}, killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} sets an explosive off, killing {1} and {2}",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, and {3}.",
                'tributes': 4,
                'killer': [0],
                'killed': [1, 2, 3]
            },
            {
                'msg': "{0} sets an explosive off, killing {1}, {2}, {3}, and {4}",
                'tributes': 5,
                'killer': [0],
                'killed': [1, 2, 3, 4]
            },
            {
                'msg': "{0} kills {1} as {1.he_she} tries to run.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} threaten a double suicide. It fails and they die.",
                'tributes': 2,
                'killer': None,
                'killed': [0, 1]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} form a suicide pact, killing themselves.",
                'tributes': 4,
                'killer': None,
                'killed': [0, 1, 2, 3]
            },
            {
                'msg': "{0} kills {1} with a hatchet.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {0} and {1} survive.",
                'tributes': 4,
                'killer': [0, 1],
                'killed': [2, 3]
            },
            {
                'msg': "{0} and {1} fight {2} and {3}. {2} and {3} survive.",
                'tributes': 4,
                'killer': [2, 3],
                'killed': [0, 1]
            },
            {
                'msg': "{0} attacks {1}, but {2} protects {1.him_her}, killing {0}",
                'tributes': 3,
                'killer': [2],
                'killed': [0]
            },
            {
                'msg': "{0} ambushes {1} and kills {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} severely slices {1} with a sword.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} strangles {1} with a rope",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} kills {1} for {1.his_her} supplies.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} shoots an arrow at {1}, but misses and kills {2} instead",
                'tributes': 3,
                'killer': [0],
                'killed': [2]
            },
            {
                'msg': "{0} shoots a poisonous blow dart into {1}'s neck, slowly killing {1.him_her}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, and {2} successfully ambush and kill {3}, {4}, and {5}.",
                'tributes': 6,
                'killer': [0, 1, 2],
                'killed': [3, 4, 5]
            },
            {
                'msg': "{0}, {1}, and {2} unsuccessfully ambush {3}, {4}, and {5}, who kill them instead.",
                'tributes': 6,
                'killer': [3, 4, 5],
                'killed': [0, 1, 2]
            },
            {
                'msg': "{0} stabs {1} wth a tree branch.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} stabs {1} in the back with a trident.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {0} triumphantly kills them both.",
                'tributes': 3,
                'killer': [0],
                'killed': [1, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {1} triumphantly kills them both.",
                'tributes': 3,
                'killer': [1],
                'killed': [0, 2]
            },
            {
                'msg': "{0}, {1}, and {2} get into a fight. {2} triumphantly kills them both.",
                'tributes': 3,
                'killer': [2],
                'killed': [0, 1]
            },
            {
                'msg': "{0} kills {1} with a sickle.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0}, {1}, {2}, {3}, and {4} track down and kill {5}.",
                'tributes': 6,
                'killer': [0, 1, 2, 3, 4],
                'killed': [5]
            },
            {
                'msg': "{0}, {1}, {2}, and {3} track down and kill {4}.",
                'tributes': 5,
                'killer': [0, 1, 2, 3],
                'killed': [4]
            },
            {
                'msg': "{0}, {1}, and {2} track down and kill {3}.",
                'tributes': 4,
                'killer': [0, 1, 2],
                'killed': [3]
            },
            {
                'msg': "{0} and {1} track down and kill {2}.",
                'tributes': 3,
                'killer': [0, 1],
                'killed': [2]
            },
            {
                'msg': "{0} tracks down and kills {1}.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
            {
                'msg': "{0} repeatedly stabs {1} to death with sais.",
                'tributes': 2,
                'killer': [0],
                'killed': [1]
            },
        ]
    },

    'arena': [
        {
            'title': "Arena Event: Wolf Mutts",
            'description': "Wolf mutts are let loose in the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is crushed by a pack of wolf mutts.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} is eaten by wolf mutts.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} knocks {1} out and leaves {1.him_her} for the wolf mutts.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} pushes {1} into a pack of wolf mutts.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "As {0} and {1} fight, a pack of wolf mutts show up and kill them both.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Acid Rain",
            'description': "Acidic rain pours down on the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is unable to find shelter and dies.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} trips face first into a puddle of acidic rain.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} injures {1} and leaves {1.him_her} in the rain to die.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} refuses {1} shelter, killing {1.him_her}.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} shoves {1} into a pond of acidic rain, but is pulled in by {1}, killing them both.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Poison Cloud",
            'description': "A cloud of poisonous smoke starts to fill the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is engulfed in the cloud of poisonous smoke.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} sacrifices {0.himself_herself} so {1} can get away.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} slowly pushes {1} closer into the cloud until {1.he_she} can't resist anymore.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} and {1} agree to die in the cloud together, but {0} pushes {1} in without warning.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} and {1} decide to run into the cloud together.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Hurricane",
            'description': "A monstrous hurricane wreaks havoc on the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is sucked into the hurricane.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} is incapacitated by flying debris and dies.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} pushes {1} into an incoming boulder.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} stabs {1}, then pushes {1.him_her} close enough for the hurricane to suck {1.him_her} "
                           "in.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} tries to save {1} from being sucked into the hurricane, only to be sucked in as well.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Tracker Jacker Swarm",
            'description': "A swarm of tracker jackers invades the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is stung to death.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} slowly dies from the tracker jacker toxins.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} knocks {1} unconscious and leaves {1.him_her} there as bait.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "While running away from tracker jackers, {0} grabs {1} and throws {1.him_her} to the "
                           "ground.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} and {1} run out of places to run and are stung to death.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Tsunami",
            'description': "A tsunami rolls into the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is swept away.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} fatally injures {0.himself_herself} on debris.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} holds {1} underwater to drown.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} defeats {1}, but throws {1.him_her} in the water to make sure {1.he_she} dies.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} and {1} smash their heads together as the tsunami rolls in, leaving them both to "
                           "drown.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Fire",
            'description': "A fire spreads throughout the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "The fire catches up to {0}, killing {0.him_her}.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "A fireball strikes {0}, killing {0.him_her}.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} kills {1} in order to utilize a body of water safely.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} falls to the ground, but kicks {1} hard enough to then push {2.him_her} into the fire.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} and {1} fail to find a safe spot and suffocate.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Border Shrink",
            'description': "The arena's border begins to rapidly contract.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is electrocuted by the border.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} trips on a tree root and is unable to recover fast enough.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} restrains {1} to a tree and leaves {1.him_her} to die.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} pushes {1} into the border while {1.he_she} is not paying attention",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "Thinking they could escape, {0} and {1} attempt to run through the border together.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Monkey Mutts",
            'description': "Monkey mutts fill the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} dies from internal bleeding caused by a monkey mutt.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} is pummeled to the ground and killed by a troop of monkey mutts.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} uses {1} as a shield from the monkey mutts.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} injures {1} and leaves {1.him_her} for the monkey mutts.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "While running, {0} falls over and grabs {1} on the way down. The monkey mutts kill them.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Carnivorous Squirrels",
            'description': "Carnivorous squirrels start attacking the tributes.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is brutally attacked by a scurry of squirrels.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} tries to kill as many squirrels as {0.he_she} can, but there are too many.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} uses the squirrels to {0.his_her} advantage, shoving {1} into them.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0}, in agony, kills {1} so {1.he_she} does not have to be attacked by the squirrels.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "The squirrels separate and kill {0} and {1}.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Volcano",
            'description': "A volcano erupts near the center of the arena.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} is buried in ash.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} suffocates.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} pushes {1} in the lava.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} dips {0.his_her} weapon in the lava and kills {1} with it.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "As {0} trips over {1} into the lava, {0.he_she} grabs {1.him_her} and pulls {1.him_her} "
                           "down with {0.him_her}.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Total Darkness",
            'description': "The arena turns pitch black and no one can see a thing.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} trips on a rock and falls off a cliff.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} accidentally makes contact with spiny, lethal plant life.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} flails {0.his_her} weapon around, accidentally killing {1}.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} finds and kills {1}, who was making too much noise.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "While fighting, {0} and {1} lose their balance, roll down a jagged hillside, and die.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
        {
            'title': "Arena Event: Mass Hallucination",
            'description': "The remaining tributes begin to hallucinate.",
            'color': 0xff9c0f,
            'nonfatal': [
                {
                    'msg': "{0} survives.",
                    'tributes': 1
                },
            ],
            'fatal': [
                {
                    'msg': "{0} eats a scorpion, thinking it is a delicate dessert.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} hugs a tracker jacker nest, believing it is a pillow.",
                    'tributes': 1,
                    'killer': None,
                    'killed': [0]
                },
                {
                    'msg': "{0} mistakes {1} for a bear and kills {1.him_her}.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} drowns {1}, who {0.he_she} thought was a shark trying to eat {0.him_her}.",
                    'tributes': 2,
                    'killer': [0],
                    'killed': [1]
                },
                {
                    'msg': "{0} and {1} decide to jump down the rabbit hole to Wonderland, which turns out to be a "
                           "pit of rocks.",
                    'tributes': 2,
                    'killer': None,
                    'killed': [0, 1]
                },
            ]
        },
    ]

}
