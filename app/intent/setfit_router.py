from setfit import SetFitModel, Trainer, TrainingArguments
from datasets import Dataset
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = Path(".models/gitvoice-setfit")

TRAIN_EXAMPLES = [
    # git_status
    ("show git status", "git_status"),
    ("what's my git status", "git_status"),
    ("check the status", "git_status"),
    ("please check status of the repo", "git_status"),
    ("status please", "git_status"),

    # run_tests
    ("run tests", "run_tests"),
    ("run all the tests", "run_tests"),
    ("execute pytest", "run_tests"),
    ("run the unit tests again", "run_tests"),
    ("test everything", "run_tests"),

    # smart_commit_push
    ("commit and push my changes", "smart_commit_push"),
    ("create a commit and push", "smart_commit_push"),
    ("git commit then git push", "smart_commit_push"),
    ("status then commit and push", "smart_commit_push"),
    ("save everything and push", "smart_commit_push"),
    ("write commit and push", "smart_commit_push"),

    # git_diff
    ("show me the diff", "git_diff"),
    ("what changed since last commit", "git_diff"),
    ("show git diff", "git_diff"),
    ("what did i change", "git_diff"),

    # git_pull
    ("pull latest changes", "git_pull"),
    ("git pull", "git_pull"),
    ("sync with origin main", "git_pull"),
    ("update code", "git_pull"),

    # help / fallback
    ("what can you do", "help"),
    ("help", "help"),
    ("show help", "help"),
    ("fix conflicts", "help"), # Fallback for now
]

class SetFitIntentClassifier:
    def __init__(self):
        self.model: Optional[SetFitModel] = None

    def _build_dataset(self) -> Dataset:
        texts, labels = zip(*TRAIN_EXAMPLES)
        return Dataset.from_dict({"text": list(texts), "label": list(labels)})

    def train(self) -> None:
        logger.info("Starting SetFit training...")
        dataset = self._build_dataset()
        # Map labels to integers internally - SetFit handles this mostly but explicit mapping is good if needed.
        # However SetFit Trainer handles string labels fine in recent versions or we might need to map them.
        # Let's try direct string labels first as SetFit 1.x supports it.
        
        # Note: SetFit Trainer might require a body for 'train_dataset' if we use TrainingArguments way.
        
        model = SetFitModel.from_pretrained(
            "sentence-transformers/paraphrase-mpnet-base-v2",
            labels=sorted(list(set(dataset["label"]))),
        )

        args = TrainingArguments(
            output_dir=str(MODEL_DIR),
            batch_size=4, # Small batch for CPU/fast training
            num_epochs=1, # Quick epoch for few-shot
            report_to="none",
        )

        trainer = Trainer(
            model=model,
            args=args,
            train_dataset=dataset,
        )

        trainer.train()
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        trainer.model.save_pretrained(str(MODEL_DIR))
        self.model = trainer.model
        logger.info(f"Model saved to {MODEL_DIR}")

    def load(self) -> None:
        if MODEL_DIR.exists():
            try:
                self.model = SetFitModel.from_pretrained(str(MODEL_DIR))
                logger.info("Loaded SetFit model from disk.")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}. Retraining...")
                self.train()
        else:
            logger.info("No saved model found. Training from scratch...")
            self.train()

    def predict_intent(self, text: str) -> Tuple[str, float]:
        if self.model is None:
            self.load()
        
        # predict_proba returns [ [prob_label1, prob_label2, ...] ]
        # if using strings, predict() returns strings directly, predict_proba returns probabilities
        if self.model: # Check again for type safety
            preds = self.model.predict_proba([text])[0]
            best_idx = int(preds.argmax())
            label = self.model.labels[best_idx]
            confidence = float(preds[best_idx])
            return label, confidence
        return "help", 0.0
