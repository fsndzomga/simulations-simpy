import random
import simpy
import numpy as np
import matplotlib.pyplot as plt

# Averaged polling data with standard deviations
biden_vs_trump = {
    "Biden": (0.439, 0.05),
    "Trump": (0.461, 0.05)
}

biden_vs_desantis = {
    "Biden": (0.431, 0.05),
    "DeSantis": (0.419, 0.05)
}


def citizen(env, name, election):
    vote = random.random()

    if election == "Trump vs. Biden":
        biden_prob = np.random.normal(biden_vs_trump["Biden"][0], biden_vs_trump["Biden"][1])
        if vote < biden_prob:
            return "Biden"
        else:
            return "Trump"
    elif election == "Biden vs. DeSantis":
        biden_prob = np.random.normal(biden_vs_desantis["Biden"][0], biden_vs_desantis["Biden"][1])
        if vote < biden_prob:
            return "Biden"
        else:
            return "DeSantis"

def election_scenario(env, num_citizens, election):
    votes = []
    for i in range(num_citizens):
        vote = citizen(env, f"Citizen {i+1}", election)
        votes.append(vote)
        yield env.timeout(1)
    return votes



def plot_results(results, election):
    candidates = list(set(result for run_results in results for result in run_results.keys()))
    total_wins = {candidate: 0 for candidate in candidates}

    for result in results:
        winner = max(result, key=result.get)
        total_wins[winner] += 1

    plt.bar(total_wins.keys(), total_wins.values())
    plt.title(f"Results of the {election} simulation ({len(results)} runs)")
    plt.ylabel("Number of wins")
    plt.show()

    for candidate, wins in total_wins.items():
        print(f"{candidate}: {wins} wins ({(wins / len(results)) * 100:.2f}% chance)")

def simulate_election(election, num_runs):
    num_citizens = 1000
    results = []

    for _ in range(num_runs):
        env = simpy.Environment()

        def run_election_scenario():
            votes = yield from election_scenario(env, num_citizens, election)
            return votes

        election_gen = env.process(run_election_scenario())
        env.run()

        votes = election_gen.value
        candidates = list(set(votes))
        vote_counts = {candidate: votes.count(candidate) for candidate in candidates}
        results.append(vote_counts)

    plot_results(results, election)

num_runs = 100
print("Simulation: Trump vs. Biden")
simulate_election("Trump vs. Biden", num_runs)

print("\nSimulation: Biden vs. DeSantis")
simulate_election("Biden vs. DeSantis", num_runs)
