from setfit import SetFitModel, Trainer, TrainingArguments
from datasets import Dataset
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

MODEL_DIR = Path(".models/gitvoice-setfit")

TRAIN_EXAMPLES = [
    # git_status
    ("show git status", "git.status"),
    ("what's my git status", "git.status"),
    ("check the status", "git.status"),
    ("please check status of the repo", "git.status"),
    ("status please", "git.status"),

    # run_tests
    ("run tests", "git.run_tests"),
    ("run all the tests", "git.run_tests"),
    ("execute pytest", "git.run_tests"),
    ("run the unit tests again", "git.run_tests"),
    ("test everything", "git.run_tests"),

    # smart_commit_push
    ("commit and push my changes", "git.smart_commit_push"),
    ("create a commit and push", "git.smart_commit_push"),
    ("git commit then git push", "git.smart_commit_push"),
    ("status then commit and push", "git.smart_commit_push"),
    ("save everything and push", "git.smart_commit_push"),
    ("write commit and push", "git.smart_commit_push"),
    ("git status, git add, git commit and git push", "git.smart_commit_push"),
    ("do everything: status, add, commit and push", "git.smart_commit_push"),
    ("prepare commit and push my changes", "git.smart_commit_push"),
    ("check status and then commit and push", "git.smart_commit_push"),

    # git_diff
    ("show me the diff", "git.diff"),
    ("what changed since last commit", "git.diff"),
    ("show git diff", "git.diff"),
    ("what did i change", "git.diff"),
    ("what changed since origin main", "git.diff"),
    ("show diff for app/main.py", "git.diff"),
    ("diff against origin/main", "git.diff"),

    # git_branch
    ("create new branch feature/login", "git.branch"),
    ("switch to develop branch", "git.branch"),
    ("checkout main", "git.branch"),
    ("new branch fix/bug-123", "git.branch"),
    ("change branch to master", "git.branch"),

    # git_pull
    ("pull latest changes", "git.pull"),
    ("git pull", "git.pull"),
    ("sync with origin main", "git.pull"),
    ("update code", "git.pull"),

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
