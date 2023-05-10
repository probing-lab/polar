def get_test_specs(filename, spec_id):
    specs = []
    starts_with = "#test: " + spec_id + ";"
    with open(filename, "r") as file:
        for line in file:
            if line.startswith(starts_with):
                line = line[len(starts_with) :]
                spec = [d.strip() for d in line.split(";")]
                specs.append(spec)
    return specs
