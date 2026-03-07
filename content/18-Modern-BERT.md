---
title: ModernBERT Model Uses
---


<div style="float: right;">
  <div class="flex flex-wrap space-x-1">
    <img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-DE3412?style=flat&logo=pytorch&logoColor=white">
    <img alt="FlashAttention" src="https://img.shields.io/badge/%E2%9A%A1%EF%B8%8E%20FlashAttention-eae0c8?style=flat">
    <img alt="SDPA" src="https://img.shields.io/badge/SDPA-DE3412?style=flat&logo=pytorch&logoColor=white">
  </div>
</div>

[ModernBERT](https://huggingface.co/papers/2412.13663) is a modernized version of [`BERT`] trained on 2T tokens. It brings many improvements to the original architecture such as rotary positional embeddings to support sequences of up to 8192 tokens, unpadding to avoid wasting compute on padding tokens, GeGLU layers, and alternating attention.

You can find all the original ModernBERT checkpoints under the [ModernBERT](https://huggingface.co/collections/answerdotai/modernbert-67627ad707a4acbf33c41deb) collection.

> [!TIP]
> Click on the ModernBERT models in the right sidebar for more examples of how to apply ModernBERT to different language tasks.

The example below demonstrates how to predict the `[MASK]` token with [`Pipeline`], [`AutoModel`], and from the command line.

```python
import torch
from transformers import pipeline

pipeline = pipeline(
    task="fill-mask",
    model="answerdotai/ModernBERT-base",
    torch_dtype=torch.float16,
    device=0
)
pipeline("Plants create [MASK] through a process known as photosynthesis.")
```


```python
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "answerdotai/ModernBERT-base",
)
model = AutoModelForMaskedLM.from_pretrained(
    "answerdotai/ModernBERT-base",
    torch_dtype=torch.float16,
    device_map="auto",
    attn_implementation="sdpa"
)
inputs = tokenizer("Plants create [MASK] through a process known as photosynthesis.", return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model(**inputs)
    predictions = outputs.logits

masked_index = torch.where(inputs['input_ids'] == tokenizer.mask_token_id)[1]
predicted_token_id = predictions[0, masked_index].argmax(dim=-1)
predicted_token = tokenizer.decode(predicted_token_id)

print(f"The predicted token is: {predicted_token}")
```

```bash
echo -e "Plants create [MASK] through a process known as photosynthesis." | transformers run --task fill-mask --model answerdotai/ModernBERT-base --device 0
```
## ModernBertConfig

```python
from transformers import ModernBertModel, ModernBertConfig

# Initializing a ModernBert style configuration
configuration = ModernBertConfig()

# Initializing a model from the modernbert-base style configuration
model = ModernBertModel(configuration)

# Accessing the model configuration
configuration = model.config
```
## ModernBertForMaskedLM

```python
from transformers import AutoTokenizer, ModernBertForMaskedLM
import torch

tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = ModernBertForMaskedLM.from_pretrained("answerdotai/ModernBERT-base")

inputs = tokenizer("The capital of France is <mask>.", return_tensors="pt")

with torch.no_grad():
	logits = model(**inputs).logits

# retrieve index of <mask>
mask_token_index = (inputs.input_ids == tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0]

predicted_token_id = logits[0, mask_token_index].argmax(axis=-1)
tokenizer.decode(predicted_token_id)


labels = tokenizer("The capital of France is Paris.", return_tensors="pt")["input_ids"]
# mask labels of non-<mask> tokens
labels = torch.where(inputs.input_ids == tokenizer.mask_token_id, labels, -100)

outputs = model(**inputs, labels=labels)
round(outputs.loss.item(), 2)
```
## ModernBertForSequenceClassification

Example of single-label classification:
```python
import torch
from transformers import AutoTokenizer, ModernBertForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = ModernBertForSequenceClassification.from_pretrained("answerdotai/ModernBERT-base")

inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

predicted_class_id = logits.argmax().item()
model.config.id2label[predicted_class_id]

# To train a model on `num_labels` classes, you can pass `num_labels=num_labels` to `.from_pretrained(...)`
num_labels = len(model.config.id2label)
model = ModernBertForSequenceClassification.from_pretrained("answerdotai/ModernBERT-base", num_labels=num_labels)

labels = torch.tensor([1])
loss = model(**inputs, labels=labels).loss
round(loss.item(), 2)
```

Example of multi-label classification:

```python
import torch
from transformers import AutoTokenizer, ModernBertForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = ModernBertForSequenceClassification.from_pretrained("answerdotai/ModernBERT-base", problem_type="multi_label_classification")

inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

predicted_class_ids = torch.arange(0, logits.shape[-1])[torch.sigmoid(logits).squeeze(dim=0) > 0.5]

# To train a model on `num_labels` classes, you can pass `num_labels=num_labels` to `.from_pretrained(...)`
num_labels = len(model.config.id2label)
model = ModernBertForSequenceClassification.from_pretrained(
    "answerdotai/ModernBERT-base", num_labels=num_labels, problem_type="multi_label_classification"
)

labels = torch.sum(
    torch.nn.functional.one_hot(predicted_class_ids[None, :].clone(), num_classes=num_labels), dim=1
).to(torch.float)
loss = model(**inputs, labels=labels).loss
```
## ModernBertForTokenClassification

```python
from transformers import AutoTokenizer, ModernBertForTokenClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = ModernBertForTokenClassification.from_pretrained("answerdotai/ModernBERT-base")

inputs = tokenizer(
    "HuggingFace is a company based in Paris and New York", add_special_tokens=False, return_tensors="pt"
)

with torch.no_grad():
    logits = model(**inputs).logits

predicted_token_class_ids = logits.argmax(-1)

# Note that tokens are classified rather then input words which means that
# there might be more predicted token classes than words.
# Multiple token classes might account for the same word
predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]
predicted_tokens_classes

labels = predicted_token_class_ids
loss = model(**inputs, labels=labels).loss
round(loss.item(), 2)
```

## ModernBertForQuestionAnswering

```python
from transformers import AutoTokenizer, ModernBertForQuestionAnswering
import torch

tokenizer = AutoTokenizer.from_pretrained("answerdotai/ModernBERT-base")
model = ModernBertForQuestionAnswering.from_pretrained("answerdotai/ModernBERT-base")

question, text = "Who was Jim Henson?", "Jim Henson was a nice puppet"

inputs = tokenizer(question, text, return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)

answer_start_index = outputs.start_logits.argmax()
answer_end_index = outputs.end_logits.argmax()

predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)

# target is "nice puppet"
target_start_index = torch.tensor([14])
target_end_index = torch.tensor([15])

outputs = model(**inputs, start_positions=target_start_index, end_positions=target_end_index)
loss = outputs.loss
round(loss.item(), 2)
```

### Usage tips

The ModernBert model can be fine-tuned using the HuggingFace Transformers library with its [official script](https://github.com/huggingface/transformers/blob/main/examples/pytorch/question-answering/run_qa.py) for question-answering tasks.

## Links for Classification Datasets

- https://huggingface.co/datasets/santhedan/question_classifier
- https://huggingface.co/datasets/nqdhocai/education-question-type-classify
- https://huggingface.co/datasets/Lots-of-LoRAs/task384_socialiqa_question_classification
- https://huggingface.co/datasets/Lots-of-LoRAs/task521_trivia_question_classification
- https://huggingface.co/datasets/Lots-of-LoRAs/task1534_daily_dialog_question_classification
- https://huggingface.co/datasets/wesley7137/question_complexity_classification
- https://huggingface.co/datasets/TimeRobber/ag_news_classify_question_first_100

This was the code for an interesting Space in Huggingface - 

```python
import torch
import torch.nn as nn
import lightning as L
import torchmetrics as tm
from tokenizers import Tokenizer
import gradio as gr
from huggingface_hub import hf_hub_download

COARSE_LABELS = [
    "ABBR (0): Abbreviation",
    "ENTY (1): Entity",
    "DESC (2): Description and abstract concept",
    "HUM (3): Human being",
    "LOC (4): Location",
    "NUM (5): Numeric value",
]

FINE_LABELS = [
    "ABBR (0): Abbreviation",
    "ABBR (1): Expression abbreviated",
    "ENTY (2): Animal",
    "ENTY (3): Organ of body",
    "ENTY (4): Color",
    "ENTY (5): Invention, book and other creative piece",
    "ENTY (6): Currency name",
    "ENTY (7): Disease and medicine",
    "ENTY (8): Event",
    "ENTY (9): Food",
    "ENTY (10): Musical instrument",
    "ENTY (11): Language",
    "ENTY (12): Letter like a-z",
    "ENTY (13): Other entity",
    "ENTY (14): Plant",
    "ENTY (15): Product",
    "ENTY (16): Religion",
    "ENTY (17): Sport",
    "ENTY (18): Element and substance",
    "ENTY (19): Symbols and sign",
    "ENTY (20): Techniques and method",
    "ENTY (21): Equivalent term",
    "ENTY (22): Vehicle",
    "ENTY (23): Word with a special property",
    "DESC (24): Definition of something",
    "DESC (25): Description of something",
    "DESC (26): Manner of an action",
    "DESC (27): Reason",
    "HUM (28): Group or organization of persons",
    "HUM (29): Individual",
    "HUM (30): Title of a person",
    "HUM (31): Description of a person",
    "LOC (32): City",
    "LOC (33): Country",
    "LOC (34): Mountain",
    "LOC (35): Other location",
    "LOC (36): State",
    "NUM (37): Postcode or other code",
    "NUM (38): Number of something",
    "NUM (39): Date",
    "NUM (40): Distance, linear measure",
    "NUM (41): Price",
    "NUM (42): Order, rank",
    "NUM (43): Other number",
    "NUM (44): Lasting time of something",
    "NUM (45): Percent, fraction",
    "NUM (46): Speed",
    "NUM (47): Temperature",
    "NUM (48): Size, area and volume",
    "NUM (49): Weight",
]


class Classifier:
    def __init__(self, tokenizer_ckpt_path, model_ckpt_path):
        self.tokenizer = Tokenizer.from_file(tokenizer_ckpt_path)
        self.model = LSTMWithAttentionClassifier.load_from_checkpoint(
            model_ckpt_path,
            map_location="cpu",
        )

    def predict(self, text):
        encoding = self.tokenizer.encode(text)
        ids = torch.tensor([encoding.ids])
        logits, _ = self.model(ids)
        probs = torch.softmax(logits, dim=1).squeeze().tolist()
        return {
            category: prob
            for category, prob in zip(
                FINE_LABELS if self.model.fine else COARSE_LABELS, probs
            )
        }


class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.WQuery = nn.Linear(hidden_dim, hidden_dim)
        self.WKey = nn.Linear(hidden_dim, hidden_dim)
        self.WValue = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        query = torch.tanh(self.WQuery(x))
        key = torch.tanh(self.WKey(x))

        attention_weights = torch.softmax(self.WValue(query + key), dim=1)

        return (attention_weights * x).sum(dim=1), attention_weights


class LSTMWithAttentionClassifier(L.LightningModule):
    def __init__(
        self,
        vocab_size,
        embedding_dim,
        hidden_dim,
        num_classes,
        lr=1e-3,
        weight_decay=1e-2,
        num_layers=1,
        bidirectional=False,
        dropout=0.0,
        padding_idx=3,
        fine=False,
        **kwargs,
    ):
        super().__init__()
        self.save_hyperparameters()
        self.lr = lr
        self.weight_decay = weight_decay
        self.fine = fine

        self.embedding = nn.Embedding(
            vocab_size,
            embedding_dim,
            padding_idx=padding_idx,
        )
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout,
        )
        self.attention = Attention(
            hidden_dim * (1 + bidirectional),
        )
        self.fc = nn.Linear(
            hidden_dim * (1 + bidirectional),
            num_classes,
        )

        self.criteria = nn.CrossEntropyLoss()
        self.accuracy = tm.Accuracy(
            task="multiclass",
            num_classes=num_classes,
        )

    def forward(self, input_ids):
        x = self.embedding(input_ids)
        x, _ = self.lstm(x)
        x, attention_weights = self.attention(x)
        x = self.fc(x)
        return x, attention_weights

    def training_step(self, batch, batch_idx):
        input_ids = batch["input_ids"]
        coarse = batch["coarse"]
        fine = batch["fine"]
        logits, _ = self(input_ids)
        loss = self.criteria(logits, fine if self.fine else coarse)
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        input_ids = batch["input_ids"]
        coarse = batch["coarse"]
        fine = batch["fine"]
        logits, _ = self(input_ids)
        loss = self.criteria(logits, fine if self.fine else coarse)
        self.log("val_loss", loss)
        pred = logits.argmax(dim=1)
        self.accuracy(pred, fine if self.fine else coarse)
        self.log("val_acc", self.accuracy, prog_bar=True)

    def configure_optimizers(self):
        return torch.optim.AdamW(
            self.parameters(),
            lr=self.lr,
            weight_decay=self.weight_decay,
        )


tokenizer_ckpt_path = hf_hub_download(
    repo_id="SatwikKambham/trec-classifier",
    filename="tokenizer.json",
)
model_ckpt_path = hf_hub_download(
    repo_id="SatwikKambham/trec-classifier",
    filename="lstm_attention.ckpt",
)
classifier = Classifier(tokenizer_ckpt_path, model_ckpt_path)
interface = gr.Interface(
    fn=classifier.predict,
    inputs=gr.components.Textbox(
        label="Question",
        placeholder="Enter a question here...",
    ),
    outputs=gr.components.Label(
        label="Predicted class",
        num_top_classes=3,
    ),
    examples=[
        [
            "What does LOL mean?",
        ],
        [
            "What is the meaning of life?",
        ],
        [
            "How long does it take for light from the sun to reach the earth?",
        ],
        [
            "When is friendship day?",
        ],
    ],
)
interface.launch()
```
