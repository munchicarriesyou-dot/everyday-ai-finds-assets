def theme(topic):
    if topic.get("theme"): return topic["theme"]
    if topic.get("category")=="research": return "research"
    return "practical"

def choose(candidates, policy, rng):
    groups={}
    for item in candidates: groups.setdefault(theme(item),[]).append(item)
    keys=sorted(groups)
    if rng.random()<policy["exploration"]:
        key=rng.choice(keys)
    else:
        key=rng.choices(keys,weights=[policy["weights"].get(k,5) for k in keys])[0]
    return rng.choice(groups[key])
