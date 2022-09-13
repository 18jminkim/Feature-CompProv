import csv
import sys
import numpy as np

def main():
    """
    Get averages of each feature vector by label
    """
    avg_feat = dict()
    num_vectors = dict()

    np.set_printoptions(suppress=True)

    with open(feature_path, newline='') as file:

        reader = csv.reader(file)
        # Skip header
        next(reader, None)

        for row in reader:
            label = row[0]

            # Init. key
            if label not in avg_feat.keys():
                avg_feat[label] = np.zeros(len(row) - 1)
                num_vectors[label] = 0
            
            avg_feat[label] += np.array([float(v) for v in row[1:]])
            num_vectors[label] += 1
        
        for key in avg_feat.keys():
            avg_feat[key] /= num_vectors[key]
        
        for key, val in avg_feat.items():
            print(f'{key}\n{val}\n')


        print(np.abs(avg_feat['clang'] - avg_feat['gcc']))







if __name__ == "__main__":
    feature_path = sys.argv[1]
    main()