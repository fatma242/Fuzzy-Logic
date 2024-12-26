import ast

class FuzzySet:
    def __init__(self, name, type_, values):
        self.name = name
        self.type = type_.upper()
        self.values = values

    def fuzzify(self, crisp_value):
        if self.type == "TRI":
            a, b, c = self.values
            if a <= crisp_value <= b:
                return (crisp_value - a) / (b - a)
            elif b <= crisp_value <= c:
                return (c - crisp_value) / (c - b)
            else:
                return 0
        elif self.type == "TRAP":
            a, b, c, d = self.values
            if a <= crisp_value <= b:
                return (crisp_value - a) / (b - a)
            elif b <= crisp_value <= c:
                return 1
            elif c <= crisp_value <= d:
                return (d - crisp_value) / (d - c)
            else:
                return 0

class Variable:
    def __init__(self, name, var_type, range_):
        self.name = name
        self.type = var_type.upper()
        self.range = range_
        self.fuzzy_sets = {}

    def add_fuzzy_set(self, fuzzy_set):
        self.fuzzy_sets[fuzzy_set.name] = fuzzy_set

class FuzzySystem:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.variables = {}
        self.rules = []

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def add_rule(self, rule):
        self.rules.append(rule)

    def run_simulation(self, crisp_values):
        fuzzified_values = {}
        for var_name, crisp_value in crisp_values.items():
            variable = self.variables.get(var_name)
            if not variable:
                print(f"Error: Variable '{var_name}' not defined.")
                return
            fuzzified_values[var_name] = {
                fs_name: fs.fuzzify(crisp_value)
                for fs_name, fs in variable.fuzzy_sets.items()
            }

        inferred_outputs = {}
        for rule in self.rules:
            in_vars, out_var, out_set = rule
            min_degree = 1  

            for var_name, set_name, operator in in_vars:
                degree = fuzzified_values[var_name].get(set_name, 0)
                if operator == "and":
                    min_degree = min(min_degree, degree)
                elif operator == "or":
                    min_degree = max(min_degree, degree)
                elif operator == "and_not":
                    min_degree = min(min_degree, 1 - degree)
                else:
                    print(f"Unknown operator: {operator}. Defaulting to 'and'.")
                    min_degree = min(min_degree, degree)  # Default to 'and' if unknown operator

            if out_var not in inferred_outputs:
                inferred_outputs[out_var] = {}

            inferred_outputs[out_var][out_set] = max(
                inferred_outputs[out_var].get(out_set, 0), min_degree
            )

        results = {}
        for var_name, output in inferred_outputs.items():
            numerator = 0
            denominator = 0
            variable = self.variables[var_name]
            for set_name, degree in output.items():
                if degree in [float("inf"), float("-inf")]:
                    continue  # Skip invalid degrees
                fs = variable.fuzzy_sets[set_name]
                centroid = sum(fs.values) / len(fs.values)  # Calculate centroid of fuzzy set
                numerator += degree * centroid
                denominator += degree

            results[var_name] = numerator / denominator if denominator > 0 else 0

        return results

def load_test_case(system):
    # Add variables
    system.add_variable(Variable("proj_funding", "IN", [0, 100]))
    system.add_variable(Variable("exp_level", "IN", [0, 60]))
    system.add_variable(Variable("risk", "OUT", [0, 100]))

    # Add fuzzy sets
    proj_funding = system.variables["proj_funding"]
    proj_funding.add_fuzzy_set(FuzzySet("very_low", "TRAP", [0, 0, 10, 30]))
    proj_funding.add_fuzzy_set(FuzzySet("low", "TRAP", [10, 30, 40, 60]))
    proj_funding.add_fuzzy_set(FuzzySet("medium", "TRAP", [40, 60, 70, 90]))
    proj_funding.add_fuzzy_set(FuzzySet("high", "TRAP", [70, 90, 100, 100]))

    exp_level = system.variables["exp_level"]
    exp_level.add_fuzzy_set(FuzzySet("beginner", "TRI", [0, 15, 30]))
    exp_level.add_fuzzy_set(FuzzySet("intermediate", "TRI", [15, 30, 45]))
    exp_level.add_fuzzy_set(FuzzySet("expert", "TRI", [30, 60, 60]))

    risk = system.variables["risk"]
    risk.add_fuzzy_set(FuzzySet("low", "TRI", [0, 25, 50]))
    risk.add_fuzzy_set(FuzzySet("normal", "TRI", [25, 50, 75]))
    risk.add_fuzzy_set(FuzzySet("high", "TRI", [50, 100, 100]))

    # Add rules
    system.add_rule(([("proj_funding", "high", "or"), ("exp_level", "expert", "or")], "risk", "low"))
    system.add_rule(([("proj_funding", "medium", "and"), ("exp_level", "intermediate", "and")], "risk", "normal"))
    system.add_rule(([("proj_funding", "medium", "and"), ("exp_level", "beginner", "and")], "risk", "normal"))
    system.add_rule(([("proj_funding", "low", "and"), ("exp_level", "beginner", "and")], "risk", "high"))
    system.add_rule(([("proj_funding", "very_low", "and_not"), ("exp_level", "expert", "and_not")], "risk", "high"))

def main():
    print("Fuzzy Logic")
    print("===================")

    systems = {}

    while True:
        print("\nMain Menu:")
        print("1- Create a new fuzzy system")
        print("2- Run predefined test case")
        print("3- Quit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            name = input("Enter the system's name: ").strip()
            description = input("Enter a brief description: ").strip()
            system = FuzzySystem(name, description)
            systems[name] = system

            while True:
                print("\nSystem Menu:")
                print("1- Add variables")
                print("2- Add fuzzy sets to an existing variable")
                print("3- Add rules")
                print("4- Run the simulation on crisp values")
                sub_choice = input("Enter your choice: ").strip()

                if sub_choice == "1":
                    while True:
                        var_input = input("Enter variable's name, type (IN/OUT), and range [lower, upper] (or 'x' to finish): ").strip()
                        if var_input.lower() == "x":
                            break

                        try:
                            name, var_type, range_str = var_input.split(maxsplit=2)
                            range_ = ast.literal_eval(range_str)
                            if not (isinstance(range_, list) and len(range_) == 2 and all(isinstance(n, (int, float)) for n in range_)):
                                raise ValueError("Invalid range format. Use [lower, upper].")

                            variable = Variable(name, var_type, range_)
                            system.add_variable(variable)
                        except ValueError as e:
                            print(f"Error: {e}. Please try again.")

                elif sub_choice == "2":
                    var_name = input("Enter the variable's name: ").strip()
                    variable = system.variables.get(var_name)
                    if not variable:
                        print(f"Error: Variable '{var_name}' not found.")
                        continue

                    while True:
                        set_input = input("Enter fuzzy set name, type (TRI/TRAP), and values (or 'x' to finish): ").strip()
                        if set_input.lower() == "x":
                            break

                        try:
                            set_name, type_, *values = set_input.split()
                            values = list(map(float, values))
                            fuzzy_set = FuzzySet(set_name, type_, values)
                            variable.add_fuzzy_set(fuzzy_set)
                        except ValueError:
                            print("Error: Invalid fuzzy set format. Please try again.")

                elif sub_choice == "3":
                    while True:
                        rule_input = input(
                            "Enter the rules in this format (Press x to finish):\n"
                            "IN_variable set operator IN_variable set => OUT_variable set\n"
                        ).strip()
                        if rule_input.lower() == "x":
                            break

                        try:
                            parts = rule_input.split(" => ")
                            if len(parts) != 2:
                                raise ValueError("Invalid rule format. Use 'var set op var set => out_var out_set'.")

                            in_part, out_part = parts
                            in_vars = []
                            conditions = in_part.split(" ")
                            idx = 0
                            while idx < len(conditions):
                                var_name = conditions[idx]
                                set_name = conditions[idx + 1]
                                operator = conditions[idx + 2] if idx + 2 < len(conditions) and conditions[idx + 2] in {"and", "or", "and_not"} else "and"  # Default to "and" if no operator specified
                                 
                                in_vars.append((var_name, set_name, operator))
                                idx += 3 if operator else 2  

                            out_var, out_set = out_part.split()
                            system.add_rule((in_vars, out_var, out_set))
                        
                        except ValueError as e:
                            print(f"Error: {e}. Please try again.") 


                elif sub_choice == "4":
                    crisp_values = {}
                    if not system.rules:
                        print("CAN’T START THE SIMULATION! Please add the fuzzy sets and rules first.")
                        continue

                    for var_name, variable in system.variables.items():
                        if variable.type == "IN":  
                            value = input(f"Enter crisp value for {var_name}: ").strip()
                            try:
                                crisp_values[var_name] = float(value)
                            except ValueError:
                                print(f"Invalid input for {var_name}. Please enter a numeric value.")
                                continue

                    print("\nRunning the simulation...")
                    print("Fuzzification => done")
                    print("Inference => done")
                    print("Defuzzification => done")

                    results = system.run_simulation(crisp_values)
                    for var_name, result in results.items():
                        print(f"The predicted {var_name} is {result:.1f}")

                elif sub_choice in ["close", "end", "exit"]:
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif choice == "2":
            system = FuzzySystem("test_case", "Predefined system for testing.")
            load_test_case(system)
            test_inputs = {"proj_funding": 50, "exp_level": 40}
            print("Test Inputs:", test_inputs)
            results = system.run_simulation(test_inputs)
            print("Simulation Results:", results)
        elif choice == "3":
            break

if __name__ == "__main__":
    main()
