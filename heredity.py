import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_p = 1
    for person in people:
        if check_parents(people, person):
            joint_p *= gene_prob(person, one_gene, two_genes, have_trait)
        else:
            # zero copies in both parents
            if parents(people, person, one_gene, two_genes) == 0:
                if people[person]['name'] in one_gene:
                    joint_p *= ((1 - PROBS["mutation"]) * (PROBS["mutation"]) + (1 - PROBS["mutation"]) * (PROBS["mutation"]))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][1][True]
                    else:
                        joint_p *= PROBS["trait"][1][False]
                elif people[person]['name'] in two_genes:
                    joint_p *= (PROBS["mutation"] * PROBS["mutation"])
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][2][True]
                    else:
                        joint_p *= PROBS["trait"][2][False]
                else:
                    joint_p *= ((1 - PROBS["mutation"]) * (1 - PROBS["mutation"]))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][0][True]
                    else:
                        joint_p *= PROBS["trait"][0][False]
            # one copy for both parents
            if parents(people, person, one_gene, two_genes) == 1:
                if people[person]['name'] in one_gene:
                    joint_p *= ((0.5 * 0.5) + (0.5 * 0.5))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][1][True]
                    else:
                        joint_p *= PROBS["trait"][1][False]
                elif people[person]['name'] in two_genes:
                    joint_p *= (0.5 * 0.5)
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][2][True]
                    else:
                        joint_p *= PROBS["trait"][2][False]
                else:
                    joint_p *= (0.5 * 0.5)
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][0][True]
                    else:
                        joint_p *= PROBS["trait"][0][False]
            # two copies for both parents        
            if parents(people, person, one_gene, two_genes) == 2:
                if people[person]['name'] in one_gene:
                    joint_p *= ((1 - PROBS["mutation"]) * (PROBS["mutation"]) + (1 - PROBS["mutation"]) * (PROBS["mutation"]))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][1][True]
                    else:
                        joint_p *= PROBS["trait"][1][False]
                elif people[person]['name'] in two_genes:
                    joint_p *= ((1 - PROBS["mutation"]) * (1 - PROBS["mutation"]))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][2][True]
                    else:
                        joint_p *= PROBS["trait"][2][False]
                else:
                    joint_p *= (PROBS["mutation"] * PROBS["mutation"])
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][0][True]
                    else:
                        joint_p *= PROBS["trait"][0][False]
            # one copy for one parent and two copies for the other parent
            if parents(people, person, one_gene, two_genes) == 3:
                if people[person]['name'] in one_gene:
                    joint_p *= ((0.5 * (PROBS["mutation"])) + ((1 - PROBS["mutation"]) * 0.5))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][1][True]
                    else:
                        joint_p *= PROBS["trait"][1][False]
                elif people[person]['name'] in two_genes:
                    joint_p *= (0.5 * (1 - PROBS["mutation"]))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][2][True]
                    else:
                        joint_p *= PROBS["trait"][2][False]
                else:
                    joint_p *= (0.5 * PROBS["mutation"])
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][0][True]
                    else:
                        joint_p *= PROBS["trait"][0][False]
            # one copy for one parent and zero copies for the other parent
            if parents(people, person, one_gene, two_genes) == 4:
                if people[person]['name'] in one_gene:
                    joint_p *= ((0.5 * (PROBS["mutation"])) + ((1 - PROBS["mutation"]) * 0.5))
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][1][True]
                    else:
                        joint_p *= PROBS["trait"][1][False]
                elif people[person]['name'] in two_genes:
                    joint_p *= (0.5 * PROBS["mutation"])
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][2][True]
                    else:
                        joint_p *= PROBS["trait"][2][False]
                else:
                    joint_p *= ((1 - PROBS["mutation"]) * 0.5)
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][0][True]
                    else:
                        joint_p *= PROBS["trait"][0][False]
            
            # two copies for one parent and zero copies for the other parent
            if parents(people, person, one_gene, two_genes) == 5:
                if people[person]['name'] in one_gene:
                    joint_p *= (1 - PROBS["mutation"] * 1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][1][True]
                    else:
                        joint_p *= PROBS["trait"][1][False]
                elif people[person]['name'] in two_genes:
                    joint_p *= ((1 - PROBS["mutation"]) * PROBS["mutation"])
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][2][True]
                    else:
                        joint_p *= PROBS["trait"][2][False]
                else:
                    joint_p *= ((1 - PROBS["mutation"]) * PROBS["mutation"])
                    if people[person]['name'] in have_trait:
                        joint_p *= PROBS["trait"][0][True]
                    else:
                        joint_p *= PROBS["trait"][0][False]
    return joint_p

def check_parents(people, person):
    if people[person]['father'] is None and people[person]['mother'] is None:
        return True
    return False


def gene_prob(person, one_gene, two_genes, have_trait):
    """
    Return gene probability, father and mother are None
    """
    if person in have_trait:
        if person in one_gene:
            return PROBS["gene"][1] * PROBS["trait"][1][True] 
        if person in two_genes:
            return PROBS["gene"][2] * PROBS["trait"][2][True]
        else:
            return PROBS["gene"][0] * PROBS["trait"][0][True]
    else:
        if person in one_gene:
            return PROBS["gene"][1] * PROBS["trait"][1][False] 
        if person in two_genes:
            return PROBS["gene"][2] * PROBS["trait"][2][False]
        else:
            return PROBS["gene"][0] * PROBS["trait"][0][False]

def parents(people, person, one_gene, two_genes):
    if zero_copies(people, 'father', person, one_gene, two_genes) and zero_copies(people, 'mother', person, one_gene, two_genes):
        return 0
    if people[person]['father'] in one_gene and people[person]['mother'] in one_gene:
        return 1
    if people[person]['father'] in two_genes and people[person]['mother'] in two_genes:
        return 2
    if (people[person]['father'] in one_gene and people[person]['mother'] in two_genes) or (people[person]['father'] in two_genes and people[person]['mother'] in one_gene):
        return 3
    if (zero_copies(people, 'father', person, one_gene, two_genes) and people[person]['mother'] in one_gene) or (zero_copies(people, 'mother', person, one_gene, two_genes) and people[person]['father'] in one_gene):
        return 4
    if (zero_copies(people, 'father', person, one_gene, two_genes) and people[person]['mother'] in two_genes) or (zero_copies(people, 'mother', person, one_gene, two_genes) and people[person]['father'] in two_genes):
        return 5

def zero_copies(people, parent, person, one_gene, two_genes):
    if people[person][parent] not in one_gene and people[person][parent] not in two_genes:
        return True
    return False

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    total_inverse = 1.0 / sum(probabilities.values())
    for key, val in probabilities.items():
        probabilities[key] = val * total_inverse
    return probabilities

    
if __name__ == "__main__":
    main()
