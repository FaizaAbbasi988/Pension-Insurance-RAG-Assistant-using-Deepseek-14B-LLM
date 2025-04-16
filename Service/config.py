import json
from pathlib import Path

# Load the entire config file
with open(Path(__file__).parent / "config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Speech recognition configurations - model_config
speech_model = config["speech_recognition"]["model_config"]["speech_model"]
model_revision = config["speech_recognition"]["model_config"]["model_revision"]
vad_model = config["speech_recognition"]["model_config"]["vad_model"]
vad_model_revision = config["speech_recognition"]["model_config"]["vad_model_revision"]
punc_model = config["speech_recognition"]["model_config"]["punc_model"]
punc_model_revision = config["speech_recognition"]["model_config"]["punc_model_revision"]

# Speech recognition configurations - transcribe_config
language = config["speech_recognition"]["transcribe_config"]["language"]
use_itn = config["speech_recognition"]["transcribe_config"]["use_itn"]
batch_size_s = config["speech_recognition"]["transcribe_config"]["batch_size_s"]
merge_vad = config["speech_recognition"]["transcribe_config"]["merge_vad"]
merge_length_s = config["speech_recognition"]["transcribe_config"]["merge_length_s"]

# Insurance model configurations - llm_config
insurance_model = config["insurance_model"]["llm_config"]["insurance_model"]
base_url = config["insurance_model"]["llm_config"]["base_url"]

# Insurance model configurations - embedding_config
embedding_model_name = config["insurance_model"]["embedding_config"]["embedding_model_name"]

# Insurance model configurations - document_config
document_file_path = config["insurance_model"]["document_config"]["file_path"]
chunk_size = config["insurance_model"]["document_config"]["chunk_size"]
chunk_overlap = config["insurance_model"]["document_config"]["chunk_overlap"]