import simpy
import random
import matplotlib.pyplot as plt
from scipy.stats import beta
import numpy as np

# Polls
polls = [    ('Biden', 'DeSantis', 38, 44),    ('Biden', 'DeSantis', 41, 48),    ('Biden', 'Trump', 39, 45),    ('Biden', 'Trump', 42, 49),    ('Biden', 'DeSantis', 45, 42),    ('Biden', 'DeSantis', 41, 36),    ('Biden', 'Trump', 46, 46),    ('Biden', 'Trump', 41, 41),    ('Biden', 'Trump', 41, 48),    ('Biden', 'DeSantis', 40, 35),    ('Biden', 'DeSantis', 35, 34),    ('Biden', 'Trump', 42, 45),    ('Biden', 'Trump', 37, 45),    ('Biden', 'DeSantis', 43, 41),    ('Biden', 'Trump', 44, 42),    ('Biden', 'Trump', 44, 43),    ('Biden', 'DeSantis', 42, 47),    ('Biden', 'DeSantis', 45, 42),    ('Biden', 'Trump', 47, 42),    ('Biden', 'Trump', 43, 47),]

biden_winning_percentages = np.array([biden / (biden + other) for biden, other in [(b, o) for _, _, b, o in polls]])
biden_mean = biden_winning_percentages.mean()
biden_var = biden_winning_percentages.var()
alpha_biden = biden_mean * (biden_mean * (1 - biden_mean) / biden_var - 1)
beta_biden = (1 - biden_mean) * (biden_mean * (1 - biden_mean) / biden_var - 1)

def citizen(env, name, election, vote_dict):
    while True:
        if "Biden" in election:
            biden_preference = beta.rvs(alpha_biden, beta_biden)
            if random.random() < biden_preference:
                vote = "Biden"
            else:
                vote = "Trump" if "Trump" in election else "DeSantis"
        else:
            vote = random.choice(election.split(" vs. "))

        timeout = yield env.timeout(random.expovariate(1))
        vote_dict[name] = vote
        break

def election_scenario(env, num_citizens, election):
    votes = []
    vote_dict = {}
    citizen_gens = [env.process(citizen(env, f"Citizen {i+1}", election, vote_dict)) for i in range(num_citizens)]
    yield simpy.AllOf(env, citizen_gens)

    for citizen_name, vote in vote_dict.items():
        votes.append(vote)

    return votes


def plot_results(results, election):
    candidates = list(set(result for run_results in results for result in run_results.keys()))
    total_wins = {candidate: 0 for candidate in candidates}

    for result in results:
        winner = max(result, key=result.get)
        total_wins[winner] += 1

    plt.bar(total_wins.keys(), total_wins.values())
    plt.title(f"Results of the {election}")
    plt.ylabel("Number of wins")
    plt.show()

    for candidate, wins in total_wins.items():
        print(f"{candidate}: {wins} wins ({(wins / len(results)) * 100:.2f}% chance)")

def simulate_election(election, num_runs):
    num_citizens = 10000
    results = []

    for _ in range(num_runs):
        env = simpy.Environment()
        election_gen = env.process(election_scenario(env, num_citizens, election))
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
