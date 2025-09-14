import pandas as pd
from classifier import classifier

def train_from_logs():
    df = pd.read_csv("training_data.csv", sep="\t", names=["query", "tool"])
    queries = df["query"].tolist()
    labels = df["tool"].tolist()

    classifier.train(queries, labels)
    print("✅ Classifier trained and saved as classifier.pkl")

if __name__ == "__main__":
    train_from_logs()
