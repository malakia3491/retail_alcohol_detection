import torch.nn as nn
from torchvision.models.feature_extraction import get_graph_node_names

class EmbeddingNet(nn.Module):
    def __init__(self, base_model: nn.Module):
        super(EmbeddingNet, self).__init__()
        self.base = base_model
        train_nodes, _ = get_graph_node_names(base_model)
        last_node_name = train_nodes[-1]
        parts = last_node_name.split('.')
        if len(parts) == 2 and parts[0] == 'classifier':
            idx = int(parts[1])
            in_features = base_model.classifier[idx].in_features
        else:
            module = base_model
            for part in parts:
                if part.isdigit():
                    module = module[int(part)]
                else:
                    module = getattr(module, part)
            in_features = module.in_features
        self.base.fc = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Linear(512, 256)
        )
        
    def forward(self, x):
        return self.base(x)