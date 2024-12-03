import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

class TaggerModel(nn.Module):
    def __init__(self, num_tags, vocab_size, emb_size, rnn_size, hidden_size, dropout_rate):
        super(TaggerModel, self).__init__()

        # Embedding layer: maps word indices to dense vectors of fixed size (embedding size)
        # Padding accounts for <UNK>s
        self.embedding = nn.Embedding(vocab_size, emb_size, padding_idx=0)
        self.dropout = nn.Dropout(dropout_rate)
        self.lstm = nn.LSTM(input_size=emb_size, hidden_size=rnn_size, bidirectional=True)
        self.fc = nn.Linear(2 * rnn_size, hidden_size)
        self.relu = nn.ReLU()
        self.out = nn.Linear(hidden_size, num_tags)

    def forward(self, x):

        embedded = self.embedding(x)  # Convert input indices to embeddings
        embedded = self.dropout(embedded)  # Apply dropout to embeddings
        lstm_out, _ = self.lstm(embedded.view(len(x), 1, -1))  # LSTM expects (seq_len, batch, input_size)
        lstm_out = lstm_out.view(len(x), -1)  # Reshape LSTM output to (seq_len, 2 * rnn_size)
        fc_out = self.fc(lstm_out)  # Fully connected layer
        fc_out = self.relu(fc_out)  # Apply ReLU activation
        tag_logits = self.out(fc_out)  # Output layer, produces tag logits
        return tag_logits

class RandomDataset(Dataset):
    def __init__(self, num_samples, seq_length, vocab_size):
        self.data = torch.randint(1, vocab_size, (num_samples, seq_length), dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

def run_test():
    try:

        num_tags = 10
        vocab_size = 10000
        emb_size = 200
        rnn_size = 400
        hidden_size = 200
        dropout_rate = 0.3
        num_samples = 5
        seq_length = 10

        tagger = TaggerModel(num_tags, vocab_size, emb_size, rnn_size, hidden_size, dropout_rate)
        dataset = RandomDataset(num_samples, seq_length, vocab_size)
        dataloader = DataLoader(dataset, batch_size=1)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(tagger.parameters(), lr=0.001)

        for batch_idx, inputs in enumerate(dataloader):
            optimizer.zero_grad()  # Clear gradients
            outputs = tagger(inputs.squeeze(0))  # Forward pass
            targets = torch.randint(0, num_tags, (seq_length,), dtype=torch.long)  # Simulated targets
            loss = criterion(outputs, targets)  # Calculate loss
            loss.backward()  # Backward pass
            optimizer.step()  # Update model parameters
        print("TaggerModel module test completed successfully.")

    except Exception as e:
        print(f"Error in TaggerModel module test: {str(e)}")

if __name__ == "__main__":
    run_test()
